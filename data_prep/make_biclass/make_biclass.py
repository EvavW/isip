#!/usr/bin/env python
#
# usage:
# python make_biclass.py [options] rec.list
#
# This script create rec_bi files from a list of rec files
#
# Eva von Weltin
# 20180522
#-----------------------------------------------------------------------------#

# import system modules
#
import os
import sys

# import NEDC modules
#
import nedc_cmdl_parser as ncp
import nedc_file_tools as nft

# define the help and usage messages
#
USAGE_FILE="/data/isip/data/tuh_eeg_seizure/work/_TOOLS/data_prep/make_biclass/make_biclass.usage"
HELP_FILE="/data/isip/data/tuh_eeg_seizure/work/_TOOLS/data_prep/make_biclass/make_biclass.help"

# define the minimum number of arguments
#
NUM_ARGS = 1

def main(argv):

    #create a command line parser
    #
    parser = ncp.CommandLineParser(USAGE_FILE, HELP_FILE)
    
    #define command line arguments
    #
    parser.add_argument("args", type = str, nargs='*')
    parser.add_argument("-rdir", "-r", type = str)
    parser.add_argument("-odir", "-o", type = str)
    parser.add_argument("-ext", "-e", type = str)
    parser.add_argument("-help", action="help")

    #parse the command line
    #
    args = parser.parse_args()

     # check if the proper number of lists has been provided
    #
    if len(args.args) != NUM_ARGS:
        parser.print_usage()
        exit(-1)

    # set the replace file
    #
    if args.rdir is not None:
        rdir_a = args.rdir

    # set the output file
    #
    if args.odir is not None:
        odir_a = args.odir
    
    #set the input file lists names
    #
    rec_list_name = args.args[0]

    #load the lists
    #
    rec_list = nft.get_flist(rec_list_name)

    # create the output directory
    #
    if nft.make_dir(odir_a) == False:
        print  "%s: error creating output directory (%s)" \
            % (sys.argv[0], odir)
        exit (-1)

    #loop through the files
    #
    for rec_file in rec_list:

        # convert rec file name to full path
        #
        rec_file = os.path.abspath(os.path.realpath(
            os.path.expanduser(rec_file)))

        # set the ofile extension
        #
        if args.ext is not None:
            ext = args.ext

        else:
            if (rec_file.endswith("t")):
                ext = "rect_bi"
            else:
                ext = "rec_bi"

        # get name of the output file and make it
        #
        ofile = nft.make_ofile(rec_file, ext, odir_a, rdir_a)
        nft.make_dir(os.path.abspath(ofile).strip(os.path.basename(ofile)))
        
        # read the rec filepyth
        #
        lines = [line.rstrip('\n') for line in open(rec_file)]
        
        # list to store events
        #
        events = []
        
        # loop over lines in the rec file
        #
        for line in lines:
        
            #remove spaces and newline chars, split the line
            #
            line = line.replace(nft.DELIM_SPACE, nft.DELIM_NULL)                                    .replace(nft.DELIM_NEWLINE, nft.DELIM_NULL)
            parts = line.split(nft.DELIM_COMMA)

            # append lines to events
            #
            events.append([int(parts[0]), float(parts[1]),                                              float(parts[2]), int(parts[3])])

        # end for

        # list to store converted events
        #
        bi_events = []
        
        # loop through all annotations
        #
        for event in events:

            # check if the label is a seizure label
            #
            label =  event[3]
            
            if label >= 8 and label <= 18:

                # convert to bi_class and add to bi_events
                #
                bi_label = 7
                bi_events.append([event[0],event[1],event[2],bi_label])
                
            # if this is not a seizure, just copy the event to bi_events
            #
            else:
                
                bi_events.append(event)

        # overwrite the rec file with the non bckg array
        #
        replace_file(bi_events,ofile)

    #end for (file)
    # exit
    #
    return True

# of the passed array
#
def replace_file(new_events_a,ofile_a):
 
    # clear file
    #
    open(ofile_a, "wb").close()

    # open file for reading
    #
    fp = open(ofile_a, "wb")

    # write each event to the file
    #
    for event in new_events_a:
        fp.write("%d,%.4f,%.4f,%d\n" %                                                         (event[0],event[1],event[2],event[3]))

    # close the file
    #
    fp.close()

    #exit 
    #
    return True
    

if __name__ == "__main__":

    main(sys.argv[:])

