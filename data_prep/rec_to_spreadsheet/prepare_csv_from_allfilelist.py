import sys, os, re
import Annotators_annot_v09 as ANN

def main(filelist):

    op = open(filelist, 'r').read()
    files = op.split('\n')


    seiz_desc = ANN.compare_annotation_files()
    print 'Index', ',', 'File No. ' , ',' , 'Seizure Filename' , ',' , 'Start time', ',' , 'Stop time', ',' , 'File', ',' , 'Session'
    j = 1
    i = 0
    for filename in files:
        if filename == '':
            break
        

        seiz_start_stop_array = seiz_desc.accumulate_annotation_for_fully_annotated_files(filename)
        seiz_start_time_array, seiz_stop_time_array, file_start_time, file_stop_time = seiz_desc.separate_class_fields_for_start_stop_time(seiz_start_stop_array)
        
       ## import pdb;pdb.set_trace()
        if len(seiz_start_time_array) == 0:


            print   str(j), ',' , str(i),  ',' , filename, ',' , ',' 
            j += 1


            i += 1

        elif len(seiz_start_time_array) != 0:


            print   str(j), ',' , str(i),  ',' , filename, ',' , seiz_start_time_array[0] , ',' , seiz_stop_time_array[0] 
            j += 1

            for annotation_index in range(len(seiz_start_time_array)):

                if annotation_index == 0:
                    continue

                print  str(j), ',' , str(i) , ',' , filename, ',' , seiz_start_time_array[annotation_index] , ',' , seiz_stop_time_array[annotation_index]

                j += 1

            i += 1










if __name__ == "__main__": main(sys.argv[1])
