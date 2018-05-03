
import os,sys,re

## This scripts checks for the bugs in .rec file after the postprocessing is done.
#  The .rec files should be in order: use sort -t"," -k1n,1 -k2n,2 filename : to sort the files


## Bug in experiments can occur due to:
#  start time of seizure as 0
#  overlap between events
#  total time exceeding time of edf file
#  repeatative annotation
#  non-existance of files at a given loction   ---->>>> Remaining
#  Last element is not \n for any file         ---->>>> Remaining


def main(filelist):
    ## process files to iterate one by one
    #
    filelist = fileprocessing(filelist)    
    ## iterate operation on files one by one
    #
    for filename in filelist:
        if filename == "":
            break
        ## Process individual file
        #
        filecont = fileprocessing(filename)
        ## Loop through each line of .rec file
        #
        line_counter = 0
        ch_change_flag = False
        prev_channel_name = -1
        
        prev_ch_no = -1
        prev_start_time = -1
        prev_stop_time = -1
        prev_class_no = -1

        for line in filecont:
            if line == "":
                break
###            print line
            line_counter += 1
            ## Separate the words of each line namely channel number, start and stop time of event and class number
            ## Create lists or arrays to store the last two records of annotation's start stop time for (i.e. checking overlap)
            #
            line_cont = line.split(',')
            ch_no = int(line_cont[0])
            start_time = float(line_cont[1])
            stop_time = float(line_cont[2])
            class_no = int(line_cont[3])
            
            ## find out when the channel number changes and use that for per channel operation
            #
            if prev_channel_name != ch_no:
                ch_change_flag = True
###                print " channel change flag is True here !!"
                ###if ch_no != 0:
                prev_channel_name += 1
            else:
                ch_change_flag = False
            
            ## From here start checking for the bugs
            ## Create a separate function for each bug
            #

            ## Check for the overlap and consecutive repeatation
            ## prev_* variables are updated later than processing so that one can compare the previous and current values..
            #
            if line_counter != 1:
                annotation_overlap_buffer(ch_no, start_time, stop_time, class_no, prev_ch_no, prev_start_time, prev_stop_time, prev_class_no, filename)


                prev_ch_no = ch_no
                prev_start_time = start_time
                prev_stop_time = stop_time
                prev_class_no = class_no
                

            ## Check whether annotation are exceeding the time of edf files or not
            #
            annot_exceeding_file_len(stop_time,filename)


            
            ## start time of seizure as 'zero'
            #
            start_seiz_zero(start_time,class_no,filename)
   
            
def start_seiz_zero(start_time,class_no,filename):
    ## Check whether this line of rec file has start time as zero for seizure..
    #
    if class_no == 7 and float(start_time) == 0.0:
        print filename  ,"\033[1;34;40m  start time of seizure is 0.0"
        print ("\033[1;37;40m")
        print filename


def annotation_overlap_buffer(ch_no, start_time, stop_time, class_no, prev_ch_no, prev_start_time, prev_stop_time, prev_class_no, filename):
    ## This function looks for repeatative annotation and also overlaps between events
    #
###    print "ch_no " , (ch_no)
###    print "start time ", (start_time)
###    print "stop_time ", (stop_time)
###    print "class_no " , (class_no)
###    print "prev_ch_no " , (prev_ch_no)
###    print " prev start time " , (prev_start_time)
###    print " prev_stop_time " ,(prev_stop_time)
###    print " prev_class_no ", (prev_class_no)
###    print " filename " , (filename)
    
    ## check whether previous annotation line and recent annotation line is the same or not
    #
    if ch_no == prev_ch_no and class_no == prev_class_no and start_time == prev_start_time and stop_time == prev_stop_time:
        print ("\033[1;34;40m This file has similar / repeatative annotations at ")
        print ("\033[1;37;40m")
        print filename
        print ch_no, "  and " , prev_ch_no, " at annotations: " , prev_start_time, ' ', prev_stop_time , ' and ', start_time , ' ', stop_time
    ## check whether there is an overlap between annotation by comparing the previous class's end time and recent class's start time for the very same channel
    #
    if ch_no == prev_ch_no and prev_stop_time > start_time:
        print ("\033[1;34;40m This file has overlap between annotation between same channels ")
        print ("\033[1;37;40m")
        print filename
        print ch_no, " and " , prev_ch_no, " at annotations: " , prev_start_time, ' ', prev_stop_time , ' and ', start_time , ' ', stop_time
        
def annot_exceeding_file_len(stop_time, filename):
    ## This function looks for the annotation that exceeds the length of the file
    #
    
    ## For that first we need to change the file to format to the actual edf file location format so that we can you nedc_print_header tool for finding out the length of the file
    #
    edf_file_len = find_files_length(filename)
###    print edf_file_len

    ## check whether stop time exceeds the length of file
    #
    if stop_time > edf_file_len:
        print "\033[1;34;40m this file has an annotation beyond the length of edf file: "
        print ("\033[1;37;40m")
        print filename

def find_files_length(non_edf_file):
    ## convert file to the edf file formatted location
    #
   
    file_words = non_edf_file.split(r'/')
    '''
    file_words[7] = "edf"
    file_words[12] = file_words[12].split('.')[0]  + ".edf"
    edf_file = r'/'.join(file_words)
'''
#    print edf_file
    ## temporary for edf file's length for old directory structure...
    file_words = non_edf_file.split(r'/')
    filename = file_words[-1].split('.')
    filename = filename[0] + ".edf"
    edf_file = "/data/isip/data/tuh_eeg/v0.6.1/edf" + r'/' + file_words[-4] + r'/' + file_words[-3] + r'/' + file_words[-2] + r'/' + filename
#    print edf_file
    ## end of old_directory structure changes ,remove this if not working with old structures

    
###    print " modified edf file location is: ", edf_file
    
    ## apply nedc_print_header tool on this edf file and find for the edf time
    #
    cmd = "nedc_print_header %s>./tmp.xxxx"%edf_file
    cmd = os.system("%s"%cmd)

    print edf_file
    
    readhdr = open('tmp.xxxx','r').read()
    hdrlines = readhdr.split('\t')
    for line in hdrlines:
        if line == "":
            break
        if 'ghdi_num_recs' in line:
            rectime = line.split()
            rectime[2] = rectime[2].strip('[').strip(']')
    total_recording_time = rectime[2]
###    print total_recording_time, " is the total recording time "
    return float(total_recording_time)

    
def fileprocessing(files):
    ## fileprocessing: separate the files and creates a list for that
    #
    fileop = open(files,'r').read()
    filelist = fileop.split('\n')
    return filelist
    ## End of fileprocessing
    #


if __name__=="__main__": main(sys.argv[1])
