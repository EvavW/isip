import os,sys,re
#input the filelocations with filenames
# this script outputs the patients description with length of file
# input list should be list of files with absolute addresses
def fileInfo(filelist):

    readfile = open(filelist,'r').read()
    files = readfile.split('\n')
    for _file in files:
        if _file=='':
            break
        #_file = _file.rstrip()
        cmd = "nedc_print_header %s>./tmp.x"%_file
        cmd =os.system('%s'%cmd)
        readhdr = open('tmp.x','r').read()
        hdrlines = readhdr.split('\n')
        i = 0

        for line in hdrlines:
            if line=='':
                continue
            p_info = []    
            if 'lpti_gender' in line:
                gender = line.split()
                gender[2] = gender[2].strip('[').strip(']')
                
            if 'lpti_dob' in line:
                dob = line.split()
                dob[2] = dob[2].strip('[').strip(']')
                
            if 'lpti_age' in line:
                age = line.split()
                age[2] = age[2].strip('[').strip(']')
            if 'ghdi_num_recs' in line:
                rectime = line.split()
                rectime[2] = rectime[2].strip('[').strip(']')

        print  _file,',',gender[2],',',dob[2],',',age[2],',',rectime[2]

if __name__=="__main__":fileInfo(sys.argv[1])
