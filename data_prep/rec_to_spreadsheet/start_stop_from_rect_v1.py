
import sys

SEIZ = int(7)

BCKG = int(6)

def main(list_a):

    # read file list
    #
    filelist = open(list_a, 'r').read()
    files = filelist.split('\n')

    # iterate over files in list
    #
    index = 1
    file_no = 1
    for ifile in files:

        # bool to see if we found a seizure
        #
        seiz_found = False
        
        # open file
        #
        with open(ifile, 'r') as fp:
         
            # iterate over labels in fp
            #
            for label in fp:
                
                # only consider the first channel
                #
                if int(label.split(',')[0].replace(" ", "")) == 0:

                    print "%d,%d,%s,%.4f,%.4f,%s" % \
                        (index, file_no, ifile, float(label.split(',')[1].replace(" ", "")),
                         float(label.split(',')[2].replace(" ", "")), label.split(',')[3].replace(" ", "").replace("\n", ""))
                    index += 1
        file_no += 1

if __name__ == "__main__":
    main(sys.argv[1])
