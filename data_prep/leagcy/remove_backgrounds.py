from decimal import getcontext, Decimal
import sys, os,re
import numpy as np

def file_processing(file_list):
    getcontext().prec = 2
    files = open(file_list,'r').read()
    files = files.split('\n')
    for file in files:
        if file == "":
            break
        #print file
        os.system('>tmp.x')
        remove_backgrounds(file)
        

def remove_backgrounds(file):
    file_content = open(file,'r').read()
    file_content = file_content.split('\n')
    #file_content.strip()
    #print file_content
    #for content in file:
    #    if content=="":
    #        break
        #print content

    fwr = open('tmp.x','a')
    for line in file_content:
        if line=="":
            break
        #print line
        print file
        line_content = line.split(',')
        if line_content[3]=="6":
            pass
        elif int(line_content[3]) >= 7: 
            
            
            line_content[2] =float(line_content[2])
            line_content[1] =float(line_content[1])
            if line_content[2] <= line_content[1]:
                break

            line_content[1] = str(round(line_content[1],1))
            line_content[2] = str(round(line_content[2],1))            
            #print line_content
            channel_str = line_content[0] + ',' + line_content[1] + ',' + line_content[2] + ',' + line_content[3] +'\n'
            print channel_str
            
            fwr.write(channel_str)

            ## only seizure annotations are written in tmp.x here with the precesion of .1f
            #  also all the wrong annotations have been removed like seiz stop time less than seizure start time
            
            

            
    fwr.close()
    os.system('cat tmp.x>%s'%file)
            
        

            
if __name__=="__main__": file_processing(sys.argv[1])
