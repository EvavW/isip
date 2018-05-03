import sys, os, re
import Annotators_annot_v09 as ANN

## args:
#  filelist: list of annotation (lab_ov) files
#  odir: output directory where updated annotations should be saved
def main(filelist,min_dur):

    op = open(filelist, 'r').read()
    files = op.split('\n')

    total_events = 0
    total_brief_events = 0
    seiz_desc = ANN.compare_annotation_files()

    for filename in files:
        if filename == '':
            break


        long_seiz_start_time_array = []
        long_seiz_stop_time_array = []

        seiz_start_stop_array = seiz_desc.accumulate_annotation_for_fully_annotated_files(filename)
        seiz_start_time_array, seiz_stop_time_array, file_start_time, file_stop_time = seiz_desc.separate_class_fields_for_start_stop_time(seiz_start_stop_array)

        total_events += len(seiz_start_time_array)
        brief_seiz = 0
        for seiz_index in range(len(seiz_start_time_array)):

            if seiz_stop_time_array[seiz_index] - seiz_start_time_array[seiz_index] <= float(min_dur):
                brief_seiz += 1

            else:
                long_seiz_start_time_array.append(seiz_start_time_array[seiz_index])
                long_seiz_stop_time_array.append(seiz_stop_time_array[seiz_index])
                                                  


        total_brief_events += brief_seiz

        if len(seiz_start_time_array) > brief_seiz:
            print filename, '\n', seiz_start_time_array, '\n', seiz_stop_time_array
            print '\n', long_seiz_start_time_array, long_seiz_stop_time_array

    print total_events
    print total_events - total_brief_events


if __name__ == "__main__": main(sys.argv[1], sys.argv[2])
