import sys,os,re

## This is a working script which changes all seizure subtypes (8..17) to 
#  common seiz class type (class number 7)

## The input should be a filelist which point to the absolute address of rec files.

def class_change(reclist):
    list_info = open(reclist,'r').read()
    list = list_info.split('\n')

    for files in list:
        if files == '':
            break
    
        file_operation(files)

def file_operation(filename):
    open('tmp.x','w').close()
    fileinfo = open(filename,'r').read()
    if fileinfo == "":
        return
    print filename
    f = open('tmp.x','a')
    file_cont = fileinfo.split('\n')
    for group in file_cont:
        if group == '':
            break
        csv = group.split(',')
        if int(csv[-1]) >= 7 and int(csv[-1]) < 18:
            string = csv[0] + ',' + csv[1] + ',' + csv[2] + ',' + '7\n'
            print string

            f.write(string)
    f.close()
    os.system('cat tmp.x>%s'%filename)


if __name__=="__main__": class_change(sys.argv[1])
