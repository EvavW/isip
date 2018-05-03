
import sys

BCKG = int(1)
SEIZ = int(2)
SLOW = int(3)

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
            events = 1
            bckg_no = 0
            seiz_no = 0
            slow_no = 0
            # iterate over labels in fp
            #
            for label in fp:
                
                # only consider the first channel
                #
                if int(label.split(',')[0].replace(" ", "")) == 0 and                              int(label.split(',')[3].replace(" ", "")) == 1:
                    bckg_no += 1

                    print "%d,%d,%d,%d,%d,%d,%s,%.4f,%.4f,%s" % \
                        (events,bckg_no,seiz_no,slow_no,index, file_no, ifile, float(label.split(',')[1].replace(" ", "")),
                         float(label.split(',')[2].replace(" ", "")), label.split(',')[3].replace(" ", "").replace("\n", ""))
                    events += 1

                if int(label.split(',')[0].replace(" ", "")) == 0 and                              int(label.split(',')[3].replace(" ", "")) == 2:
                    seiz_no += 1

                    print "%d,%d,%d,%d,%d,%d,%s,%.4f,%.4f,%s" % \
                        (events,bckg_no,seiz_no,slow_no,index, file_no, ifile, float(label.split(',')[1].replace(" ", "")),
                         float(label.split(',')[2].replace(" ", "")), label.split(',')[3].replace(" ", "").replace("\n", ""))
                    events += 1
                                
                if int(label.split(',')[0].replace(" ", "")) == 0 and                              int(label.split(',')[3].replace(" ", "")) == 3:
                    slow_no += 1

                    print "%d,%d,%d,%d,%d,%d,%s,%.4f,%.4f,%s" % \
                        (events,bckg_no,seiz_no,slow_no,index, file_no, ifile, float(label.split(',')[1].replace(" ", "")),
                         float(label.split(',')[2].replace(" ", "")), label.split(',')[3].replace(" ", "").replace("\n", ""))
                    events += 1

                    index += 1
        
        file_no += 1
        
if __name__ == "__main__":
    main(sys.argv[1])
