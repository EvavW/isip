#!/usr/bin/env python
#
# file: /data/isip/exp/tuh_eeg/exp_2282/scripts/quantize_rec.py
#
# revision history:
#
#  20180223 (NC): initial version
#
# usage:
#  quantize_rec -odir output -rdir rdir edf.list rec.list
#
# options:
#  -odir: output directory [EXP_DIR/output]
#  -rdir: replace directory [None]
#
#  -help: display this help message
#
# arguments:
#  edf.list: a list of ".edf" files
#  rec.list: a list of ".rec" files, corresponding to edf files
#
# This script quantizes .rec annotations to comply with the sampling frequency
# of the given edf file
#------------------------------------------------------------------------------

# import system modules
import os
import sys

# import NEDC modules
#
import nedc_cmdl_parser as ncp
import nedc_file_tools as nft
import nedc_edf_reader as ner

# determine the location of the source code
#
EXP_DIR = "/data/isip/exp/tuh_eeg/exp_2282"

# define the help file and usage message
#
HELP_FILE = EXP_DIR + "/scripts/quantize_rec.help"
USAGE_FILE = EXP_DIR + "/scripts/quantize_rec.usage"

# define defaults for arguments
#
DEF_ODIR = EXP_DIR + "/output"
DEF_RDIR = None

# define the required number of arguments
#
NEDC_NUM_ARGS = 2

# index of sampling frequency from ner.load_edf
#
FS_IND = 1

# file extensions
#
EDF_EXT = "edf"
REC_EXT = "rec"

#------------------------------------------------------------------------------
#
# the main program starts here
#
#------------------------------------------------------------------------------
# method: main
#
# arguments: none
#
# This method is the main function.
#
def main(argv):

    # declare default values for command line arugments
    #
    odir = DEF_ODIR
    rdir = DEF_RDIR
    
    # create a command line parser
    #
    parser = ncp.CommandLineParser(USAGE_FILE, HELP_FILE)

    # define the command line arguments
    #
    parser.add_argument("args", type = str, nargs='*')
    parser.add_argument("-odir", type = str)
    parser.add_argument("-rdir", type = str)
    parser.add_argument("-help", action="help")

    # parse the command line
    #
    args = parser.parse_args()

    # check if the proper number of lists has been provided
    #
    if len(args.args) != NEDC_NUM_ARGS:
        parser.print_usage()
        exit(-1)

    # set option and argument values
    #
    # set the output directory
    #
    if args.odir is not None:
        odir = args.odir

    # set the replace directory
    #
    if args.rdir is not None:
        rdir = args.rdir

    # set the input file lists names
    #
    edf_name = args.args[0]
    rec_name = args.args[1]

    # load the lists
    #
    edf_list = nft.get_flist(edf_name)
    rec_list = nft.get_flist(rec_name)

    if edf_list is None:
        print "%s (%s: %s): error loading input list (%s)" % \
            (sys.argv[0], __name__, "main", edf_list)
        exit(-1)

    if rec_list is None:
        print "%s (%s: %s): error loading input list (%s)" % \
            (sys.argv[0], __name__, "main", rec_list)
        exit(-1)

    # create the output directory
    #
    if nft.make_dir(odir) == False:
        print "%s: error creating output direcory (%s)" \
            (sys.argv[0], odir)
        exit(-1)

    # loop over file lists
    #
    num_read = 0
    num_quantized = 0
    for edf_file, rec_file in zip(edf_list, rec_list):
        print edf_file
        
        # count number of read files
        #
        num_quantized += 1

        # load the edf file, we only care about the sampling frequency
        #
        fs = ner.load_edf(edf_file, 0, 0, None)[FS_IND]

        # read the rec file
        #
        lines = [line.rstrip('\n') for line in open(rec_file)]

        # create the new filename
        #
        ofile = nft.make_ofile(rec_file, REC_EXT, odir, rdir)
        fp = nft.make_fp(ofile)

        # list to store events
        #
        events = []

        # loop over rec file lines
        #
        for line in lines:

            # remove spaces and newline chars, split the line
            #
            line = line.replace(nft.DELIM_SPACE, nft.DELIM_NULL) \
                       .replace(nft.DELIM_NEWLINE, nft.DELIM_NULL)
            parts = line.split(nft.DELIM_COMMA)
            
            # append line to events
            #
            events.append([int(parts[0]), float(parts[1]), \
                           float(parts[2]), int(parts[3])])
        #
        # end of for

        # list to store quantized events
        #
        quantized_events = []

        # loop over events
        #
        for event in events:

            # get left/right bounds from event
            #
            left_bound = event[1]
            right_bound = event[2]

            # quantize bounds to be multiples of (1 / fs)
            #
            left_bound = quantize_position(left_bound, fs)
            right_bound = quantize_position(right_bound, fs)

            # store quantized event
            #
            quantized_events.append([event[0], left_bound, \
                                     right_bound, event[3]])
        #
        # end of for

        # write quantized events to output file
        #
        for q_event in quantized_events:

            fp.write("%d,%.4f,%.4f,%d\n" % \
                     (q_event[0], q_event[1], q_event[2], q_event[3]))
        #
        # end of for

        # close the output file
        #
        fp.close()
    #
    # end of for

    # exit gracefully
    #
    return True
#
# end of main

# function: quantize_position
#
# arguments: 
#  pos: a floating point number to be quantized
#  fs: sampling frequency
#
# return:
#  a version of this number which has been quantized
#
def quantize_position(pos_a, fs_a):

    # calculate time step
    #
    dt = 1 / fs_a

    # lock into discrete grid
    #
    quantized = round(pos_a / dt) * dt

    # truncate to 4 decimal points
    #
    return round(quantized, 4)
#
# end of function

# begin gracefully
#
if __name__ == "__main__":
    main(sys.argv)

#
# end of file
