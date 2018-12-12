#!/usr/bin/env python
#
# usage:
# python get_list.py [options] flist
#
# This script generates a list of desired output files from a given list 
# default use is to create edf files
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
USAGE_FILE="/data/isip/data/tuh_eeg_seizure/work/_TOOLS/data_prep/get_list/get_list.usage"
HELP_FILE="/data/isip/data/tuh_eeg_seizure/work/_TOOLS/data_prep/get_list/get_list.help"

# define the minimum number of arguments
#
NUM_ARGS = 1

# this is the main function of the script
#
def main(argv):

    #create a command line parser
    #
    parser = ncp.CommandLineParser(USAGE_FILE, HELP_FILE)
    
    #define command line arguments
    #
    parser.add_argument("args", type = str, nargs='*')
    parser.add_argument("-rdir", type = str)
    parser.add_argument("-odir", type = str)
    parser.add_argument("-ext", type = str)
    parser.add_argument("-help", action = "help")

    #parse the command line
    #
    args = parser.parse_args()

    # check if the proper number of lists has been provided
    #
    if len(args.args) != NUM_ARGS:
        parser.print_usage()
        exit(-1)

    # set the output extension
    #
    if args.ext is not None:
        
        ext = args.ext
    
    else: # set default
        
        ext = "edf"


    # set the output directory
    #
    if args.odir is not None:
        odir = args.odir

    # set the replace directory
    #
    if args.rdir is not None:
        rdir = args.rdir
    
    #set the input file lists names
    #
    file_list_name = args.args[0]

    #load the lists
    #
    file_list = nft.get_flist(file_list_name)

    #loop through the files
    #
    for this_file in file_list:

        # convert input to full path
        #
        this_file = os.path.abspath(os.path.realpath(
            os.path.expanduser(this_file)))

        # check to see if this is a channel based file
        #
        file_parts=this_file.split("/")

        if len(file_parts[len(file_parts)-1].split("_")) == 4:
            
            # if channel based, strip channel name
            #
            cut_file = this_file[:-10]+".ext"
            
            # create edf file name from striped input
            #
            ofile = nft.make_ofile(cut_file, ext, odir, rdir)

        # if not channel based, use original file to make ofile
        #
        else:
            ofile = nft.make_ofile(this_file, ext, odir, rdir)

        # print to console. direct output from command line
        #
        print ofile

    # exit
    #
    return True

if __name__ == "__main__":

    main(sys.argv[:])

