import sys,os

def main(filelist):
    op = open(filelist, 'r').read()
    files = op.split('\n')
    
    os.system(">_file_problems.list")
    for filename in files:
        if filename == '':
            break
        
        file_op = open(filename,'r').read()
        filelines = file_op.split('\n')
        
        file_prob = open("_file_problems.list","a")

        ## Collect all the filenames for seizure start time less than 1 second in a file called _file_problems.list
        #
        for line in filelines:
            if line == '':
                break
            line_parts = line.split(',')
            if float(line_parts[1]) < 1.0:
#                print line_parts
#                print filename
                file_prob.write(filename)
                file_prob.write('\n')
                break
        file_prob.close()
        ## All files have been collected here in file "_file_problems.list"
        #

    fix_file()


def fix_file():
    ## here we only work with the files with all the problems
    #

    op = open("_file_problems.list", 'r').read()
    files = op.split('\n')
    



    for filename in files:
        if filename == "":
            break
        
        file_op = open(filename,'r').read()
        file_lines = file_op.split('\n')

        print filename
        os.system(">tmp.x")
        write_file = open("tmp.x","a")
        for line in file_lines:
            if line == "":
                break
            line_parts = line.split(',')
            if float(line_parts[1]) < 1.0:
                print " inside if condition ", line_parts
                ed_str = ",".join([line_parts[0],"1.0",line_parts[2],line_parts[3]])
                print "edited string ", ed_str
                write_file.write(ed_str)
                write_file.write('\n')
            else:
                write_file.write(line)
                write_file.write('\n')

        write_file.close()
        
        cmd_str = "cat tmp.x >%s"%filename

        os.system(cmd_str)


if __name__=="__main__": main(sys.argv[1])
