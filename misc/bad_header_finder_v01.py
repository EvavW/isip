import os
import sys
import nedc_edf_reader as ner

def main(filelist_a):

    # list of bad headers
    #
    bad_edfs = []

    # get files from file list
    #
    filelist = open(filelist_a, 'r').read()
    files = filelist.split('\n')

    # loop over files
    #
    for ifile in files:
        
        if os.path.isfile(ifile):

            # try to get header
            #
            try:
                h = ner.return_header(ifile)
            except ValueError as e:
                print "%s" % (ifile)
                bad_edfs.append(ifile)
        else:
            print("%s does not exist" %(ifile))

    return bad_edfs

if __name__ == '__main__':
    main(sys.argv[1])
