import os,sys,re

def useful_lay(_filelist):
    
    # read the list of files
    filelist = open(_filelist,'r')
    filelist =filelist.read()
    
    files =filelist.split('\n')
    for filename in files:
        if filename =='':
#            print "file skipped"
            break
        
        layfile = open('%s'%filename,'r')
        layfile = layfile.read()
        layfile =layfile.rstrip()
        comments = layfile.split('[Comments]')
        if not comments[1] or comments[1]=='':
            continue
        print filename
#        print comments[1] 
        












if __name__=="__main__":useful_lay(sys.argv[1])
