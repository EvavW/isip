
#import system modules
#
import os
import sys

#import NEDC modules
#
import nedc_cmdl_parser as ncp
import nedc_file_tools as nft

#define the help and usage messages
#
USAGE_FILE="/home/tue95303/use.txt"
HELP_FILE="/home/tue95303/help.txt"

def main(argv):

    #create a command line parser
    #
    parser = ncp.CommandLineParser(USAGE_FILE, HELP_FILE)
    
    #define command line arguments
    #
    parser.add_argument("args", type = str, nargs='*')

    #parse the command line
    #
    args = parser.parse_args()
    
    #set the input file lists names
    #
    rec_list_name = args.args[0]
    edf_list_name = args.args[1]

    #load the lists
    #
    rec_list = nft.get_flist(rec_list_name)
    edf_list = nft.get_flist(edf_list_name)

    #loop through the files
    #
    for rec_file, edf_file in zip(rec_list, edf_list):
        
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
            line = line.replace(nft.DELIM_SPACE, nft.DELIM_NULL)                                    .replace(nft.DELIM_NEWLINE, nft.DELIM_NULL)
            parts = line.split(nft.DELIM_COMMA)

            # append lines to events
            #
            events.append([int(parts[0]), float(parts[1]),                                              float(parts[2]), int(parts[3])])

        # end for

        # list to store fully annotated events
        #
        full_events = []
        
        # fully annotate each channel
        #
        for chan in range(0,22):
            
            # list to store events for each channel
            #
            chan_events =[]
            
            # loop through events
            #
            i=0
            for event in events:
                channel = event[0]
                label = event[3]
                
                # events to chan_events if channel # matches
                #
                if channel == chan and label != 6:
                    chan_events.append(event)
             
            #end for

            # if there are no annotations for this channel: fill with bckg
            #
            if len(chan_events) == 0:

                chan_events.append([chan,0,edf_dur,6])
                
            # if there are annotations for this channel: call fill_blanks
            #
            else:
                
                chan_events=fill_blanks(chan_events,edf_dur)

                        
            # loop through the events for this channel and add then to
            # full_events list
            #
            for event in chan_events:

                full_events.append(event)

            #end for (event)
        #end for (chan)

        # overwrite the rec file with the fully annotated event list
        #
        replace_file(full_events,rec_file)

    #end for (file)
    # exit
    #
    return True

# this function fills in background between annotations
# annotation for a single channel should be passed
#
def fill_blanks(chan_events,edf_dur):

    # list for full annotation for each channel
    #
    full_ann = []

    # loop through events for this channel
    #
    i=0
    for event in chan_events:
     
        #parse events array
        #
        channel = event[0]
        start = event[1]
        stop = event[2]
        label = event[3]

        # if this is the first annotation: fill from 0 and add event
        #
        if i == 0:
            full_ann.append([channel,0,start,6])
            full_ann.append(event)
        
        # if this is the last annotation: fill from previous annotation
        # add event, and fill to the end
        #
        elif i == (len(chan_events)-1):
            prev_stop=chan_events[i-1][2]
            full_ann.append([channel,prev_stop,start,6])
            full_ann.append(event)
            full_ann.append([channel,stop,edf_dur,6])

        # if this is a middle annotations: fill from previous annotation 
        # and add the event
        #
        else:
            prev_stop=chan_events[i-1][2]
            full_ann.append([channel,prev_stop,start,6])
            full_ann.append(event)

        i+=1
    #end for

    #return the fully annotated list
    #
    return full_ann

# this method clears out the passed file and fills it with the content
# of the passed array
#
def replace_file(full_events,rec_file):
 
    # clear file
    #
    open(rec_file, "wb").close()

    # open file for reading
    #
    fp = open(rec_file, "wb")

    # write each event to the file
    #
    for event in full_events:
        fp.write("%d,%.4f,%.4f,%d\n" %                                                         (event[0],event[1],event[2],event[3]))

    # close the file
    #
    fp.close()

    #exit 
    #
    return True
    

if __name__ == "__main__":

    main(sys.argv[:])

