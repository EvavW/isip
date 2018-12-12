#!/usr/bin/env python
#
# usage:
# python rec_to_chtse.py [options] rec.list
#
# This script creates channel based tse files from a list of rec files
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
USAGE_FILE="/data/isip/data/tuh_eeg_seizure/work/_TOOLS/data_prep/rec_to_chtse/rec_to_chtse.usage"
HELP_FILE="/data/isip/data/tuh_eeg_seizure/work/_TOOLS/data_prep/rec_to_chtse/rec_to_chtse.help"

# define the minimum number of arguments
#
NUM_ARGS = 1
DSK_RAID_STR = '/dsk0_raid10'

# this is the main function of the program
#
def main(argv):

    #create a command line parser
    #
    parser = ncp.CommandLineParser(USAGE_FILE, HELP_FILE)
    
    #define command line arguments
    #
    parser.add_argument("args", type = str, nargs='*')
    parser.add_argument("-odir", "-o", type = str)
    parser.add_argument("-rdir", "-r", type = str)
    parser.add_argument("-mfile", "-m", type = str)
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

    # set the output directory
    #
    if args.odir is not None:
        odir = args.odir

    # set the replace directory
    #
    if args.rdir is not None:
        rdir = args.rdir

    # set the map
    #
    if args.mfile is not None:
        mfile = args.mfile
    
    #set the input file lists names
    #
    rec_list_name = args.args[0]

    #load the lists
    #
    rec_list = nft.get_flist(rec_list_name)

    # create the output directory
    #
    nft.make_dir(odir)

    # load the map
    #
    tmpmap = nft.load_parameters(mfile, "REC_MAP")
    lmap = nft.generate_map(tmpmap)
    
    #loop through the files
    #
    for rec_file in rec_list:

        # convert rec_file name to absolute path
        #
        abs_rec_file = os.path.abspath(os.path.realpath(
            os.path.expanduser(rec_file)))
        
        if DSK_RAID_STR in abs_rec_file:
            rec_file = abs_rec_file.split(DSK_RAID_STR)[1]

        # set the ofile extension
        #
        if args.ext is not None:
            ext = args.ext

        else:
            ext = "tse"
        
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
            line = line.replace(nft.DELIM_SPACE, nft.DELIM_NULL)                                    .replace(nft.DELIM_NEWLINE, nft.DELIM_NULL)
            parts = line.split(nft.DELIM_COMMA)

            # append lines to events
            #
            events.append([int(parts[0]), float(parts[1]),                                              float(parts[2]), parts[3]])

    
        #find out how many channels there should be based on montage
        #
        file_dirs=rec_file.split("/")
        montage=file_dirs[len(file_dirs)-5]
        
        if montage == ("01_tcp_ar" or "02_tcp_le"):
            chan_num = 22
        elif montage == ("03_tcp_ar_a" or "04_tcp_le_a"):
            chan_num = 20

        #loop through each channel and associated annotations
        #
        for channel in range(0,chan_num):
            
            #list to store events for this channel
            #
            chan_events = []

            # make tse file that these events will be stored in
            #
            rec_filename = os.path.basename(rec_file).split(".")[0] +\
                           "_ch" + format(channel, '03') + ".rec"
            rec_dirname = os.path.dirname(rec_file)

            chan_file = os.path.join(rec_dirname, rec_filename)

            ofile = nft.make_ofile(chan_file, ext, odir, rdir)

            nft.make_dir(os.path.abspath(ofile).strip(os.path.basename(ofile)))

            #loop through events
            #
            for event in events:
                
                ann_chan = event[0]

                if ann_chan == channel:

                    start = event[1]
                    stop = event[2]
                    key = event[3]
                   
                    # translate numerical label to string label
                    #
                    label = str(lmap.get(key))[2:-2]
                    
                    # add event to chan_events
                    #
                    chan_events.append([start, stop, label, "1.0000"])
                    
            # write chan_events to ofile, if there are any
            #
            if len(chan_events) != 0:
                
                gen_file(chan_events,ofile)

    # exit
    #
    return True

#
#
def gen_file(events_a,file_name_a):
 
    # clear file
    #
    open(file_name_a, "wb").close()

    # open file for writing
    #
    fp = open(file_name_a, "wb")

    # write tse header
    #
    fp.write("# example: foo.tse\n")
    fp.write("version = tse_v1.0.0\n")
    fp.write("# data starts here\n#\n")

    # write each event to the file
    #
    for event in events_a:
        fp.write("%.4f %.4f %s %s\n" %                                                         (event[0],event[1],event[2],event[3]))

    # close the file
    #
    fp.close()

    #exit 
    #
    return True
    

if __name__ == "__main__":

    main(sys.argv[:])

