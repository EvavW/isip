
import os
import sys
from operator import itemgetter

NUM_CHANS = 22

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

PRIORITY_MAP = {BCKG:  1, MYSZ:  2, ABSZ:  3, ATSZ:  4, SPSZ:  5, NESZ:  6, 
                FNSZ:  7, GNSZ:  8, CPSZ: 9, CNSZ: 10, TNSZ: 11,  
                TCSZ: 12, INTR: 13, SEIZ: 14, SPSW: 15, GPED: 16, PLED: 17, EYBL: 18, ARTF: 19}

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
                if high_end < end and (low_start <= start and start <= high_end):
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

def main(filelist_a):

    filelist = open(filelist_a, 'r').read()
    files = filelist.split('\n')

    for ifile in files:
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
        ofile = ifile.replace("rec", "rect")

        with open(ofile, 'w') as fp:

            for i in range(NUM_CHANS):
                for seg in agg_segs[0]:
                    fp.write("%d,%.4f,%.4f,%d\n" % (i, seg[0], seg[1], seg[2]))

if __name__ == "__main__":

    main(sys.argv[1])

