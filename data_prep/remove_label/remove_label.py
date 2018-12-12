#!/usr/bin/env python
#
# usage:
# python remove_label.py [options] rec.list
#
# This script remove a given label from a list of rec files
# default label to remove is 6 (bckg)
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
USAGE_FILE="/data/isip/data/tuh_eeg_seizure/work/_TOOLS/data_prep/remove_label/remove_label.usage"
HELP_FILE="/data/isip/data/tuh_eeg_seizure/work/_TOOLS/data_prep/remove_label/remove_label.help"

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
    parser.add_argument("-label", "-l", type = str)
    parser.add_argument("-help", action="help")

    #parse the command line
    #
    args = parser.parse_args()

    # check if the proper number of lists has been provided
    #
    if len(args.args) != NUM_ARGS:
        parser.print_usage()
        exit(-1)

    # set the label to remove
    #
    if args.label is not None:
        label = args.label

    else:
        
        label = "6"

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

    # convert label to an integer
    #
    rm_label = int(label)

    #load the lists
    #
    rec_list = nft.get_flist(rec_list_name)

    if (rec_list == None):
        print  "%s (%s: %s): error loading input list (%s)" % \
            (sys.argv[0], __name__, "main", rec_list_name)
        exit (-1)

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

        # set the ofile ext
        #
        if args.ext is not None:
            ext = args.ext

        else:
            ext = rec_file.split(".")[1]

        # get name of the output file and make it
        #
        ofile = nft.make_ofile(rec_file, ext, odir_a, rdir_a)
        nft.make_dir(os.path.abspath(ofile).strip(os.path.basename(ofile)))
        
        # read the rec file
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
            line = line.replace(nft.DELIM_SPACE, nft.DELIM_NULL) \
                       .replace(nft.DELIM_NEWLINE, nft.DELIM_NULL)
            parts = line.split(nft.DELIM_COMMA)

            # append lines to events
            #
            events.append([int(parts[0]), float(parts[1]), \
                           float(parts[2]), int(parts[3])])

        # end for

        non_bckg=[]

        for event in events:
            label = event[3]
            
            if label != rm_label:
                non_bckg.append(event)
	
        # end for event in events

        # overwrite the rec file with the non bckg array
        #
        replace_file(non_bckg,ofile)

    #end for (file)
    # exit
    #
    return True

# of the passed array
#
def replace_file(new_events_a,rec_file_a):
 
    # clear file
    #
    open(rec_file_a, "wb").close()

    # open file for reading
    #
    fp = open(rec_file_a, "wb")

    # write each event to the file
    #
    for event in new_events_a:
        fp.write("%d,%.4f,%.4f,%d\n" \
                 %(event[0],event[1],event[2],event[3]))

    # close the file
    #
    fp.close()

    #exit 
    #
    return True
    

if __name__ == "__main__":

    main(sys.argv[:])

