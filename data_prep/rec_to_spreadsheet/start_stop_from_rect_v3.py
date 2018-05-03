
import os, sys

BCKG = int(6)

SEIZ = int(7)

def main(list_a,list_b):

    # read file list
    #
    filelist = open(list_a, 'r').read()
    files = filelist.split('\n')

    first_files = open(list_b,'r').read()
    firsts = first_files.split('\n')

    # iterate over files in list
    #
    index = 1
    file_no = 1
    session_events = 0
    
    for ifile in files:

        # bool to see if we found a seizure
        #
        seiz_found = False
        is_first = False
        first_event = True


        for first in firsts:
            if ifile == first:
                if is_first is False:
                    is_first = True
                    session_events = 0

        # open file
        #
        with open(ifile, 'r') as fp:
            seiz_no = 0
            # iterate over labels in fp
            #
            for label in fp:
                
                # only consider the first channel
                #

                if int(label.split(',')[0].replace(" ", "")) == 0 and                              int(label.split(',')[3].replace(" ", "")) == 7:
                    seiz_no += 1
                    session_events += 1
                    if seiz_found is False:
                        seiz_found = True
                    if seiz_no > 1:
                        is_first = False
                        first_event = False
                        
                        
                    print "%r,%r,%d,%d,%d,%s,%.4f,%.4f" % \
                        (is_first,first_event,session_events,seiz_no,file_no,ifile, float(label.split(',')[1].replace(" ", "")),
                         float(label.split(',')[2].replace(" ", "")))
                                
                    index += 1

            if seiz_found is False:
                        
                print "%r,%r,%d,%d,%d,%s" % \
                    (is_first,first_event,session_events,seiz_no,file_no,ifile)
                        
                index += 1
        
        file_no += 1
        
if __name__ == "__main__":
    main(sys.argv[1],sys.argv[2])
