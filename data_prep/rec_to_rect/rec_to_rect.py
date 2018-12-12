#!/usr/bin/env python
#
# usage:
# python rec_to_rect.py [options] rec.list
#
# This script create term based rect files from a list of rec files
#
# Eva von Weltin
# 20180522
#-----------------------------------------------------------------------------#

# import system modules
#
import os
import sys

# import NEDC and other modules
#
from operator import itemgetter
import nedc_cmdl_parser as ncp
import nedc_file_tools as nft

# define usage and help messages
#
USAGE_FILE="/data/isip/data/tuh_eeg_seizure/work/_TOOLS/data_prep/rec_to_rect/rec_to_rect.usage"
HELP_FILE="/data/isip/data/tuh_eeg_seizure/work/_TOOLS/data_prep/rec_to_rect/rec_to_rect.help"

# define the minimum number of arguments
#
NUM_ARGS = 1

# define annotation map
#
NULL = int(0)
SPSW = int(1)
GPED = int(2)
PLED = int(3)
EYBL = int(4)
ARTF = int(5)
BCKG = int(6)
SEIZ = int(7)
FNSZ = int(8)
GNSZ = int(9)
SPSZ = int(10)
CPSZ = int(11)
ABSZ = int(12)
TNSZ = int(13)
CNSZ = int(14)
TCSZ = int(15)
ATSZ = int(16)
MYSZ = int(17)
NESZ = int(18)
INTR = int(19)
SLOW = int(20)
EYEM = int(21)
CHEW = int(22)
SHIV = int(23)
MUSC = int(24)
ELPP = int(25)
ELST = int(26)
TRIG = int(27)

# define priority map
#
PRIORITY_MAP = {BCKG:  1, MYSZ:  2, ABSZ:  3, ATSZ:  4, SPSZ:  5, NESZ:  6, 
                FNSZ:  7, GNSZ:  8, CPSZ: 9, CNSZ: 10, TNSZ: 11,  
                TCSZ: 12, INTR: 13, SEIZ: 14, SPSW: 15, GPED: 16, PLED: 17, 
                EYBL: 18, ARTF: 19, EYEM: 21, CHEW: 22, SHIV: 23, MUSC: 24, \
                ELPP: 25, ELST: 26, TRIG: 27}

def main(argv):

    # create a command line parser
    #
    parser = ncp.CommandLineParser(USAGE_FILE, HELP_FILE)

    # define command line arguments
    #
    parser.add_argument("args", type = str, nargs='*')
    parser.add_argument("-rdir", "-r", type = str)
    parser.add_argument("-odir", "-o", type = str)
    parser.add_argument("-ext", "-e", type = str)
    parser.add_argument("-help", action="help")

    # parse the command line
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

    # set the input file lists names
    #
    rec_list_name = args.args[0]

    # load the list of rec files
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

    # loop through the files

    for ifile in rec_list:

        # convert rec file name to full path
        #
        ifile = os.path.abspath(os.path.realpath(
            os.path.expanduser(ifile)))

        # get name of the output file and make it
        #
        if args.ext is not None:
            ext = args.ext
            
        else:

            if (ifile.endswith("bi")):
                ext = "rect_bi"
            else:
                ext = "rect"

        ofile = nft.make_ofile(ifile, ext, odir_a, rdir_a)
        nft.make_dir(os.path.abspath(ofile).strip(os.path.basename(ofile)))

        # find out how many channels there should be based on montage
        #
        file_dirs=ifile.split("/")
        montage=file_dirs[len(file_dirs)-5]

        if montage == ("01_tcp_ar" or "02_tcp_le"):
            chan_num = 22
        elif montage == ("03_tcp_ar_a" or "04_tcp_le_a"):
            chan_num = 20

        # list to store annotations
        #
        segments = {}
        
        # open file
        #
        with open(ifile, 'r') as fp:

            # iterate over labels in fp
            #
            for label in fp:

                channel = int(label.split(',')[0].replace(" ", ""))
                start = float(label.split(',')[1].replace(" ", ""))
                stop = float(label.split(',')[2].replace(" ", ""))
                symbol = int(label.split(',')[3].replace(" ", ""))
            
                if channel not in segments:
                    segments[channel] = []

                segments[channel].append([start, stop, symbol])

        #
        # end of with

        # aggregate the segments!
        #
        agg_segs = nedc_aggregate_segments(segments)

        # write to file
        #
        with open(ofile, 'w') as fp:

            for i in range(chan_num):
                for seg in agg_segs[0]:
                    fp.write("%d,%.4f,%.4f,%d\n" % (i, seg[0], seg[1], seg[2]))

# this function converts event based annotations to term based annotation
#
def nedc_aggregate_segments(segments_a):

    channels = []
    unique_events = []
    event_finished = False
    low_start = int(-1)
    high_end = int(-1)
    high_priority = int(-1)
    agg_events = []

    for channel in segments_a:
        channels.append(channel)
        event_list = segments_a[channel]

        for event in event_list:
            if event not in unique_events and event[2] != BCKG:
                unique_events.append(event)

    unique_events = sorted(unique_events, key=itemgetter(0,1))

    # while unique_events isn't empty
    #
    while (unique_events != []):

        # reset values
        #
        event_finished = False
        low_start = -1
        high_end = -1
        high_priority = -1

        # while the event isn't over
        #
        while (event_finished is False):

            # iterate over events
            #
            for i in range(len(unique_events)):

                start = unique_events[i][0]
                end = unique_events[i][1]

                # if this is the first loop
                #

                if low_start == -1 and high_end == -1 and high_priority == -1:
                    low_start = start
                    high_end = end
                    break

                # if we found a new highest end time, and start time is
                # between low_start and high_end
                #
                if high_end < end and (low_start <= start and \
                                       start <= high_end):
                    high_end = end
                    break
            #
            # end of for

            # if we looked through all events
            #
            if i == len(unique_events) - 1:

                event_finished = True            

                temp_list = []
                for event in unique_events:

                    # if the event is not part of the agg
                    #
                    if event[0] > high_end:

                        # we want to keep this event
                        #
                        temp_list.append(event)

                    # else the event was not part of the agg
                    #
                    else:

                        # find the highest priority
                        #
                        symbol = event[2]
                        priority = PRIORITY_MAP[symbol]

                        if priority > high_priority:
                            high_priority = priority

                # unique_events is now all events not in the agg_event
                #
                unique_events = temp_list
        #
        # end of while

        # get symbol of highest priority
        #
        for key in PRIORITY_MAP:
            if PRIORITY_MAP[key] == high_priority:
                symbol = key

        # create agg event based on low_start and high_end
        #
        agg_events.append([low_start, high_end, symbol])
    #
    # end of while

    return {0: agg_events}

if __name__ == "__main__":

    main(sys.argv[:])

