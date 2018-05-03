import sys,os

def file_details(file):
    
    file = open(file,'r').read()
    file_content = file.split('\n')
    for name in file_content:
        if name=="":
            break
        #print name
        info = name.split(', ')
        length = int(info[-1])
        
        if length > 3600:
            print name, " length:",length

if __name__=="__main__": file_details(sys.argv[1])
