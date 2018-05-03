
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
                
                # only consider the first channel, check if symbol is seiz
                #
                if int(label.split(',')[0].replace(" ", "")) == 0 and \
                   int(label.split(',')[3].replace(" ", "")) == SEIZ:

                    if seiz_found is False:
                        seiz_found = True

                    print "%s,%.4f,%.4f" % \
                        (ifile, float(label.split(',')[1].replace(" ", "")),
                         float(label.split(',')[2].replace(" ", "")))
            
            # print file name only if we found no seizures
            #
            if seiz_found is False:
                print "%s" % ifile

if __name__ == "__main__":
    main(sys.argv[1])
