import sys,os,re

## UNCOMMENT THE LAST COMMAND IN ORDER TO ACTUALLY CREATE AND APLLY TO THE NEW TERM FILES


## This program is for conversion from epoch based anntation to term based annotation



def file_list_sep(filelist):
    list = open(filelist,'r').read()
    list = list.split('\n')
    for file in list:
        if file=="":
            break

        array_operation(file)


def array_operation(file):
    
    threshold = 0.6
    consistency_in_sec = 3


    file_content = open(file,'r').read()
    file_content = file_content.split('\n')
    open('tmp.x','w').close()
    
    event_list = []
    for line in file_content:
        if line=="":
            break
        line_content = line.split(',')
        
        if float(line_content[1]) > threshold:
            event_list.append(1)
        else:
            event_list.append(0)



    i = 0
    
    f = open('tmp.x','a')

    start_index = 0
    ## Later on all this sub while loops should be inside some function
    # during multiclass specification
    while i < len(event_list):
        j = 0
        while event_list[i] == 0:

            if j == 0:
                start_index = i + j
            i += 1
            j += 1
            if i>=len(event_list):
                #print " bckg start ", start_index, " end ", i+1
                term_line =str(start_index) + ',' + str(i+1) + ',' + 'bckg\n'
                print term_line
                f.write(term_line)
                break
        #print " bckg start ", start_index, " end ", i+1

        if i>= len(event_list):
            break
        ## For beginning where start time should be from 0
        if (start_index == 0):
            term_line = '0' + ',' + str(i+1) + ',' + 'bckg\n'
            print term_line
            f.write(term_line)

        else:
            term_line = str(start_index+1) + ',' + str(i+1) + ',' + 'bckg\n'
            print term_line
            f.write(term_line)

        j = 0
        while event_list[i] == 1:

            if j == 0:
                start_index = i + j
            i += 1
            j += 1
            if i>=len(event_list):
                #print " seiz start ", start_index, " end ", i+1
                term_line = str(start_index+1) + ',' + str(i+1) + ',' + 'seiz\n'
                print term_line
                f.write(term_line)
                break
        #print " seiz start ", start_index +1, " end ", i+1

        if i >= len(event_list):
            break
        term_line = str(start_index+1) + ',' + str(i+1) + ',' + 'seiz\n'
        print term_line
        f.write(term_line)

    f.close()
    new_file = file.split('.')
    term_file = ".." + new_file[2] + ".term"
    #print term_file
    cmd = "cat tmp.x>%s"%term_file
    #print cmd
#    cmd = os.system(cmd)


if __name__=="__main__": file_list_sep(sys.argv[1])
