#!/usr/bin/env python
#
# usage:
# python full_ann.py [options] rec.list edf.list
#
# This script fully annotates rec annotation files
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
USAGE_FILE="/data/isip/data/tuh_eeg_seizure/work/_TOOLS/data_prep/full_ann/full_ann.usage"
HELP_FILE="/data/isip/data/tuh_eeg_seizure/work/_TOOLS/data_prep/full_ann/full_ann.help"

# define the required number of arguments
#
NUM_ARGS = 2

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
    parser.add_argument("-label", "-l", type = str)
    parser.add_argument("-help", action="help")

    # parse the command line
    #
    args = parser.parse_args()

    # check if the proper number of lists has been provided
    #
    if len(args.args) != NUM_ARGS:
        parser.print_usage()
        exit(-1)
    
    # set the label used to fully annotate
    #
    if args.label is not None:
        fill_label = args.label
    
    # set default label to bckg
    #
    else:
        
        fill_label = 0

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
    edf_list_name = args.args[1]

    # load the list of rec files
    #
    rec_list = nft.get_flist(rec_list_name)

    if (rec_list == None):
        print  "%s (%s: %s): error loading input list (%s)" % \
            (sys.argv[0], __name__, "main", rec_list_name)
        exit (-1)
    
    # load the list of edf files
    #
    edf_list = nft.get_flist(edf_list_name)

    if (edf_list == None):
        print  "%s (%s: %s): error loading input list (%s)" % \
            (sys.argv[0], __name__, "main", edf_list_name)
        exit (-1)

    # create the output directory
    #
    if nft.make_dir(odir_a) == False:
        print  "%s: error creating output directory (%s)" \
            % (sys.argv[0], odir)
        exit (-1)

    # loop through the files
    #
    for rec_file, edf_file in zip(rec_list, edf_list):

        # convert rec file name to full path
        #
        rec_file = os.path.abspath(os.path.realpath(
            os.path.expanduser(rec_file)))

        # set ofile extension
        #
        if args.ext is not None:
            ext = args.ext

        else:
            ext = rec_file.split(".")[1]

        # get name of the output file and make it
        #
        ofile = nft.make_ofile(rec_file, ext, odir_a, rdir_a)
        nft.make_dir(os.path.abspath(ofile).strip(os.path.basename(ofile)))
        
        # get duration of the edf file
        # 
        cmd ="nedc_print_header %s | grep secs | awk '{printf $6}'"%edf_file
        edf_dur = os.popen('%s'%cmd).read()
        edf_dur = int(float(edf_dur))

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
            line = line.replace(nft.DELIM_SPACE, nft.DELIM_NULL)\
                       .replace(nft.DELIM_NEWLINE, nft.DELIM_NULL)
            parts = line.split(nft.DELIM_COMMA)

            # append lines to events
            #
            events.append([int(parts[0]), float(parts[1]), \
                           float(parts[2]), int(parts[3])])

        # end for

        # find out how many channels there should be based on montage
        #
        file_dirs=rec_file.split("/")
        montage=file_dirs[len(file_dirs)-5]

        if montage == ("01_tcp_ar" or "02_tcp_le"):
            chan_num = 22
        elif montage == ("03_tcp_ar_a" or "04_tcp_le_a"):
            chan_num = 20

        # list to store fully annotated events
        #
        full_events = []
        
        # fully annotate each channel
        #
        for chan in range(0, chan_num):
            
            # list to store events for each channel
            #
            chan_events =[]
            
            # loop through events
            #
            i = 0
            for event in events:
                channel = event[0]
                label = event[3]
                
                # events to chan_events if channel # matches
                # exclue fill label annotations. default will
                # exclude bckg annotations
                #
                if channel == chan and label != fill_label:
                    chan_events.append(event)
             
            #end for

            # if there are no annotations for this channel: fill with bckg
            #
            if len(chan_events) == 0:

                chan_events.append([chan, 0, edf_dur, fill_label])
                
            # if there are annotations for this channel: call fill_blanks
            #
            else:
                
                chan_events=fill_blanks(chan_events, edf_dur, fill_label)

            # loop through the events for this channel and add then to
            # full_events list
            #
            for event in chan_events:

                full_events.append(event)

            #end for (event)
        #end for (chan)

        # overwrite the rec file with the fully annotated event list
        #
        replace_file(full_events, ofile)

    #end for (file)
    # exit
    #
    return True

# this function fills in background between annotations
# annotation for a single channel should be passed
#
def fill_blanks(chan_events_a, edf_dur_a, fill_label_a):

    # list for full annotation for each channel
    #
    full_ann = []

    # loop through events for this channel
    #
    i = 0
    for event in chan_events_a:

        #parse events array
        #
        channel = event[0]
        start = event[1]
        stop = event[2]
        label = event[3]

        # if this is the only event: fill from 0 and to the end
        if len(chan_events_a) == 1:
            if start < 1:
                start = 1.0000
            full_ann.append([channel, 0, start, fill_label_a])

            if stop > edf_dur_a-1:
                stop = edf_dur_a-1
            full_ann.append([channel, start, stop, label])
            full_ann.append([channel, stop, edf_dur_a, fill_label_a])
    
        # if this is the first annotation:
        # fill from 0 to event
        #
        elif i == 0:
            if start < 1:
                start = 1.0000

            full_ann.append([channel, 0, start, fill_label_a])
            full_ann.append([channel, start, stop, label])
        
        # if this is the last annotation: fill from previous annotation
        # add event, and fill to the end
        #
        elif i == (len(chan_events_a)-1):

            if stop > edf_dur_a-1:

                stop = edf_dur_a-1

            prev_stop = chan_events_a[i-1][2]
            full_ann.append([channel, prev_stop, start, fill_label_a])
            full_ann.append([channel, start, stop, label])
            full_ann.append([channel, stop, edf_dur_a, fill_label_a])

        # if this is a middle annotations: fill from previous annotation 
        # and add the event
        #
        else:

            prev_stop=chan_events_a[i-1][2]
            full_ann.append([channel, prev_stop, start, fill_label_a])
            full_ann.append(event)

        i += 1
    #end for

    #return the fully annotated list
    #
    return full_ann

# this method clears out the passed file and fills it with the content
# of the passed array
#
def replace_file(full_events_a, ofile_a):
 
    # clear file
    #
    open(ofile_a, "wb").close()

    # open file for reading
    #
    fp = open(ofile_a, "wb")

    # write each event to the file
    #
    for event in full_events_a:
        fp.write("%d,%.4f,%.4f,%d\n"\
                 %(event[0], event[1], event[2], event[3]))

    # close the file
    #
    fp.close()

    #exit 
    #
    return True
    

if __name__ == "__main__":

    main(sys.argv[:])

