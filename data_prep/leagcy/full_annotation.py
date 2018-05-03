import seiz_annotation_array as saa
import re,sys,os
import numpy as np
import math as m
np.set_printoptions(threshold=np.inf)

# For accurate start and stop time annotation (no margins) --> first remove all background using remove_bckg.. script.
# This file annotates the full files with remaining intervals (non-seizures) as bckg. Just input the list of .rec files and it will read the size of the file using nedc_print_header tool and fill up the remaining intervals as bckg.
# After running this script, make sure to run emacs.list for sorting all the files accurately.

# This script can be annotated for counting process of seizure events in a particular file.


def read_filelists(rec_filelist):
    
    files = open(rec_filelist,'r').read()
    files = files.split('\n')
    for filename in files:
        if filename =="":
            break
                
        ## Create an Array of 22 channels (rows) and 50 columns to save seizure start and 
        ## stop time from rec files (50 number should be increased if events are more than
        ## 25 by count
        #
        channel_array = saa.file_operation(filename)

        
        ## Conversion of recent (.rec) files location to absolute edf file location ,
        ## so that nedc_print_header can be use to get information from headers
        #
        edf_file = filename.split(r'/')

        #print edf_file
        edf_file[-1] = edf_file[-1].split('.')[-2] + ".edf"
        
        ## For conventional Directory structure
        #
        edf_file = "/data/isip/data/tuh_eeg/v1.1.0/edf" + "/" + edf_file[-5] + "/" + edf_file[-4] + "/" + edf_file[-3] + "/" + edf_file[-2]  + "/" + edf_file[-1]
        print edf_file
        
        ## For new directory structure at tuh_eeg_seizure
        #
###        edf_file = r"/".join([edf_file[0] , edf_file[1] , edf_file[2] , edf_file[3] , edf_file[4] , edf_file[5] , edf_file[6] + "/edf" , edf_file[8] , edf_file[9] , edf_file[10] , edf_file[11] , edf_file[-1]])
#        edf_file = r"/".join([ "/" + edf_file[0+10] , edf_file[1+10] , edf_file[2+10] , edf_file[3+10] , edf_file[4+10] , edf_file[5+10] + "/edf" ,edf_file[7+10] , edf_file[8+10] , edf_file[9+10] , edf_file[10+10] , edf_file[-1]])
                

        ## find out the end of recording time
        #
        cmd ="nedc_print_header %s>./tmp.x"%edf_file

        cmd = os.system('%s'%cmd)

        readhdr = open('tmp.x','r').read()
        hdrlines = readhdr.split('\t')


        for line in hdrlines:
            if line=='':
                break
            if 'ghdi_num_recs' in line:
                rectime = line.split()
                rectime[2] = rectime[2].strip('[').strip(']')

        total_recording_time = rectime[2]
        
        background_est(filename, channel_array, total_recording_time)
        




## This function annotates the whole non-seizure interval (till the EOF) as bckg
#

def background_est(rec_file, arr, total_rec):
    
    f = open(rec_file,'a')
    row = 0
    
    while row < 22:
        col = 0
        while (int(arr[row,col]) != 0):
          
            #print "zero to the number" , m.floor(float(arr[row,col]))
            if col == 0:

#                string = str(row) + ',' + '0.0' + ',' + str(m.floor(float(arr[row,col]))) + ',' + '6\n'
                string = str(row) + ',' + '0.0' + ',' + str((float(arr[row,col]))) + ',' + '6\n'
                col += 2
                f.write('%s'%string)

            elif col%2 == 0:
#                string = str(row) + ',' + str(m.ceil(float(arr[row,col-1]))) + ',' + str(m.floor(float(arr[row,col]))) + ',' + '6\n' 
                string = str(row) + ',' + str((float(arr[row,col-1]))) + ',' + str((float(arr[row,col]))) + ',' + '6\n' 
                col += 2
                f.write('%s'%string)
                
        #print m.ceil(float(arr[row,col - 1])), " to the end of the file at ", total_rec
#        string = str(row) + ',' + str(m.ceil(float(arr[row,col -1]))) + ',' + total_rec + ',' + '6\n'
        string = str(row) + ',' + str((float(arr[row,col -1]))) + ',' + total_rec + ',' + '6\n'
        f.write('%s'%string)
        row += 1
    f.close()


if __name__=="__main__": read_filelists(sys.argv[1])
