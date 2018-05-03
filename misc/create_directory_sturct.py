import os,sys

def main(filelist):
    op = open(filelist,'r').read()
    files = op.split('\n') 

    for filename in files: 
        if filename == '': 
            break
        if not os.path.exists(os.path.dirname(filename)):

            try:
                os.makedirs(os.path.dirname(filename))

            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        with open(filename, "w") as f:
            f.close()

if __name__=="__main__": main(sys.argv[1])
