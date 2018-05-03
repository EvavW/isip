import sys

def listop(rec_filelist):
    files = open(rec_filelist,'r').read()
    files = files.split('\n')
    for filename in files:
        if filename == "":
            break
        #print filename

        file_cont = open(filename,'r').read()
        file_cont = file_cont.split('\n')
        for lines in file_cont:
            if lines == '':
                break
            word = lines.split(',')
            word[3] = word[3].strip('\r')
            if word[1] == word[2]:
                #print "****"
                print filename, "  has the same start and stop time at ", lines
            elif float(word[1]) == 0.0 and int(word[3]) >= 7:
                #print "****"
                print filename, " the seizure in this file starts from 0.0 at ", lines
            elif float(word[1])>float(word[2]):
                
                print filename, " has start time greater than stop time at ", lines

if __name__=="__main__":listop(sys.argv[1])
