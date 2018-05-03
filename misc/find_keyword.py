import os,re,sys,subprocess

# This script finds out types of seizures avalable in tuh dataset by given report file list(temp1.txt)


# among 16367 sessions on TUH database, in reports, 15227 have impressions, 14301 have clinical correlation and
# 3 have clinical correction; so it would be better idea to loop everything first through impressino and then others.


def seiz_classification(filelist,keyword):
    filelist = open(filelist,'r')    # text report files goes here.
    filelist = filelist.read()

    files = filelist.split('\n')

    os.system('>keyword_file')

    #print files
    for filename in files:
        if filename =='':
       
            break

        cmd = 'cp '+ filename + ' ./hehe.txt'
       
        firstcmd = os.system('%s'%cmd)
       
        firstcmd = open('hehe.txt','r')
        firstcmd = firstcmd.read()
        totalfiles = open('overall_files_ununiqed','a')
        totalfiles.write('%s\n'%filename)
        totalfiles.close()

        if 'description' in firstcmd.lower():
            filecontent = firstcmd.lower().split('description')
            #print filecontent[0]
            #print filecontent[1]

            if keyword.lower() in filecontent[1].lower():
                keyfile=open('keyword_file','a')
                keyfile.write('%s\n'%filename)
                keyfile.close()




           
if __name__=="__main__":seiz_classification(sys.argv[1],sys.argv[2])
