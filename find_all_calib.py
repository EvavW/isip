
# import system modules
#
import os
import sys
import numpy as np
import math
from scipy import signal
from scipy import fftpack
import matplotlib.pyplot as plt

# import NEDC modules
#
import nedc_edf_reader as ner
import nedc_file_tools as nft

proc = open("./proc.list", 'a')
out = open("./out.list", 'a')
err = open("./err.list", 'a')


# difference magnitude threshold
#
THRES = 10

# window length, in seconds
#
WIN_LEN = float(.4)

# amount to shift window by
#
WIN_SHIFT = float(0.1)

# length of edf to read
#
DEF_LENGTH = 15

# names of montages
#
AR_DIR = "01_tcp_ar"
LE_DIR = "02_tcp_le"
AR_A_DIR = "03_tcp_ar_a"
LE_A_DIR = "04_tcp_le_a"

# montage definitions
#
AR_MONTAGE = ['FP1-F7: EEG FP1-REF  --  EEG F7-REF',
              'F7-T3:  EEG F7-REF   --  EEG T3-REF',
              'T3-T5:  EEG T3-REF   --  EEG T5-REF',
              'T5-O1:  EEG T5-REF   --  EEG O1-REF',
              'FP2-F8: EEG FP2-REF  --  EEG F8-REF',
              'F8-T4:  EEG F8-REF   --  EEG T4-REF',
              'T4-T6:  EEG T4-REF   --  EEG T6-REF',
              'T6-O2:  EEG T6-REF   --  EEG O2-REF',
              'A1-T3:  EEG A1-REF   --  EEG T3-REF',
              'T3-C3:  EEG T3-REF   --  EEG C3-REF',
              'C3-CZ:  EEG C3-REF   --  EEG CZ-REF',
              'CZ-C4:  EEG CZ-REF   --  EEG C4-REF',
              'C4-T4:  EEG C4-REF   --  EEG T4-REF',
              'T4-A2:  EEG T4-REF   --  EEG A2-REF',
              'FP1-F3: EEG FP1-REF  --  EEG F3-REF',
              'F3-C3:  EEG F3-REF   --  EEG C3-REF',
              'C3-P3:  EEG C3-REF   --  EEG P3-REF',
              'P3-O1:  EEG P3-REF   --  EEG O1-REF',
              'FP2-F4: EEG FP2-REF  --  EEG F4-REF',
              'F4-C4:  EEG F4-REF   --  EEG C4-REF',
              'C4-P4:  EEG C4-REF   --  EEG P4-REF',
              'P4-O2:  EEG P4-REF   --  EEG O2-REF']

LE_MONTAGE = ['FP1-F7: EEG FP1-LE  --  EEG F7-LE',
              'F7-T3:  EEG F7-LE   --  EEG T3-LE',
              'T3-T5:  EEG T3-LE   --  EEG T5-LE',
              'T5-O1:  EEG T5-LE   --  EEG O1-LE',
              'FP2-F8: EEG FP2-LE  --  EEG F8-LE',
              'F8-T4:  EEG F8-LE   --  EEG T4-LE',
              'T4-T6:  EEG T4-LE   --  EEG T6-LE',
              'T6-O2:  EEG T6-LE   --  EEG O2-LE',
              'A1-T3:  EEG A1-LE   --  EEG T3-LE',
              'T3-C3:  EEG T3-LE   --  EEG C3-LE',
              'C3-CZ:  EEG C3-LE   --  EEG CZ-LE',
              'CZ-C4:  EEG CZ-LE   --  EEG C4-LE',
              'C4-T4:  EEG C4-LE   --  EEG T4-LE',
              'T4-A2:  EEG T4-LE   --  EEG A2-LE',
              'FP1-F3: EEG FP1-LE  --  EEG F3-LE',
              'F3-C3:  EEG F3-LE   --  EEG C3-LE',
              'C3-P3:  EEG C3-LE   --  EEG P3-LE',
              'P3-O1:  EEG P3-LE   --  EEG O1-LE',
              'FP2-F4: EEG FP2-LE  --  EEG F4-LE',
              'F4-C4:  EEG F4-LE   --  EEG C4-LE',
              'C4-P4:  EEG C4-LE   --  EEG P4-LE',
              'P4-O2:  EEG P4-LE   --  EEG O2-LE']

AR_A_MONTAGE = ['FP1-F7: EEG FP1-REF  --  EEG F7-REF',
                'F7-T3:  EEG F7-REF   --  EEG T3-REF',
                'T3-T5:  EEG T3-REF   --  EEG T5-REF',
                'T5-O1:  EEG T5-REF   --  EEG O1-REF',
                'FP2-F8: EEG FP2-REF  --  EEG F8-REF',
                'F8-T4:  EEG F8-REF   --  EEG T4-REF',
                'T4-T6:  EEG T4-REF   --  EEG T6-REF',
                'T6-O2:  EEG T6-REF   --  EEG O2-REF',
                'T3-C3:  EEG T3-REF   --  EEG C3-REF',
                'C3-CZ:  EEG C3-REF   --  EEG CZ-REF',
                'CZ-C4:  EEG CZ-REF   --  EEG C4-REF',
                'C4-T4:  EEG C4-REF   --  EEG T4-REF',
                'FP1-F3: EEG FP1-REF  --  EEG F3-REF',
                'F3-C3:  EEG F3-REF   --  EEG C3-REF',
                'C3-P3:  EEG C3-REF   --  EEG P3-REF',
                'P3-O1:  EEG P3-REF   --  EEG O1-REF',
                'FP2-F4: EEG FP2-REF  --  EEG F4-REF',
                'F4-C4:  EEG F4-REF   --  EEG C4-REF',
                'C4-P4:  EEG C4-REF   --  EEG P4-REF',
                'P4-O2:  EEG P4-REF   --  EEG O2-REF']

LE_A_MONTAGE = ['FP1-F7: EEG FP1-LE  --  EEG F7-LE',
                'F7-T3:  EEG F7-LE   --  EEG T3-LE',
                'T3-T5:  EEG T3-LE   --  EEG T5-LE',
                'T5-O1:  EEG T5-LE   --  EEG O1-LE',
                'FP2-F8: EEG FP2-LE  --  EEG F8-LE',
                'F8-T4:  EEG F8-LE   --  EEG T4-LE',
                'T4-T6:  EEG T4-LE   --  EEG T6-LE',
                'T6-O2:  EEG T6-LE   --  EEG O2-LE',
                'T3-C3:  EEG T3-LE   --  EEG C3-LE',
                'C3-CZ:  EEG C3-LE   --  EEG CZ-LE',
                'CZ-C4:  EEG CZ-LE   --  EEG C4-LE',
                'C4-T4:  EEG C4-LE   --  EEG T4-LE',
                'FP1-F3: EEG FP1-LE  --  EEG F3-LE',
                'F3-C3:  EEG F3-LE   --  EEG C3-LE',
                'C3-P3:  EEG C3-LE   --  EEG P3-LE',
                'P3-O1:  EEG P3-LE   --  EEG O1-LE',
                'FP2-F4: EEG FP2-LE  --  EEG F4-LE',
                'F4-C4:  EEG F4-LE   --  EEG C4-LE',
                'C4-P4:  EEG C4-LE   --  EEG P4-LE',
                'P4-O2:  EEG P4-LE   --  EEG O2-LE']

def main(argv):

    # create edf object
    #
    edf = ner.Edf()

    # grab commandline arguments
    #
    ilist = argv[1]

    files = nft.get_flist(ilist)

    # get all files that have calibration at beginning and end
    #
    for ifile in files:
        
        proc.write(ifile + "\n")

        # make sure file exists
        #
        if not (os.path.isfile(ifile)):
            continue

        # load the header
        #
        try:
            header = edf.get_header(ifile)
        except Exception as e:
            err.write("Error: \n")
            err.write(ifile + "\n")
            continue

        # get length of EEG signal
        #
        edf_length = int(edf.get_duration())

        # default length to read
        #
        length = DEF_LENGTH

        # read length of edf if lower than the default length
        #
        if edf_length <= length:
            length = edf_length
                
        # read a certain length of data
        #
        for i in range(0, edf_length - length + 1):

            # start and stop times to read
            #
            tstart = i
            tstop = i+length

            # last window of data
            #
            if i == (edf_length - length):
                
                # ignore the last second of data, usually is dead signal
                #
                tstop -= 1
                length -= 1
    
            # load beginning of montaged signal
            #  TODO: currently only using _A montages,
            #         removed fp1-f3 channels
            #
            if AR_DIR in ifile:
                data = ner.load_edf(ifile, tstart, tstop, AR_A_MONTAGE)
            if LE_DIR in ifile:
                data = ner.load_edf(ifile, tstart, tstop, LE_A_MONTAGE)
            if AR_A_DIR in ifile:
                data = ner.load_edf(ifile, tstart, tstop, AR_A_MONTAGE)
            if LE_A_DIR in ifile:
                data = ner.load_edf(ifile, tstart, tstop, LE_A_MONTAGE)

            # get all channels of signal
            #
            channels = data[0]
            import pdb;pdb.set_trace()
            # report the error, ignore this file
            #
            if channels is None:
                err.write("**> Montage Error" + "\n")
                err.write(ifile + "\n")
                break

            # get sample frequency
            #
            fs = data[1]
        
            # denotes whether calibration was found at the beginning
            #
            found_calib = False

            # create a sliding window over the channels
            #
            nwindows = int(round((length - WIN_LEN) / WIN_SHIFT))
            for win_ind in range(0, nwindows):

                # calculate sample indices for the window
                #
                i_start = int(round(win_ind * WIN_SHIFT * fs))
                i_stop = i_start + int(round(WIN_LEN * fs))

                # calibration was found at beginning, look to end of file
                #
                if found_calib:
                    break

                # loop over the channels
                #
                for i in range(len(channels)):

                    # isolate window from the signal
                    #
                    window = channels[i][i_start:i_stop]
                    import pdb;pdb.set_trace()
                    # reset flag
                    #
                    found_calib = False

                    # get range of the channel
                    #
                    diff = max(window) - min(window)
                    
                    # check if window is below difference threshold
                    #
                    if diff < THRES:

                        # get digital min/max
                        #
                        physical_max = header['physical_max'][i]
                        physical_min = header['physical_min'][i]

                        # make sure signal is not flattened by digital min/max
                        #
                        p_max = max(channels[i][i_start:i_stop]) + 10
                        p_min = min(channels[i][i_start:i_stop]) - 10
                        if (p_max > physical_max) or (p_min < physical_min):
                            found_calib = False
                            break

                        # found calibration
                        #
                        found_calib = True

                    # channel is not calibration, go to next window
                    #
                    else:
                        found_calib = False
                        break
                    #
                    # end of if
                #
                # end of for
            #
            # end of for

            # calibration not found, exit this file
            #
            if not found_calib:
                break
            #
            # end of if
        #
        # end of for

        # calibration found in entire file
        #
        if found_calib:
            out.write(ifile + '\n')
    #
    # end of for

    # exit gracefully
    #
    return True
#
# end of main

# begin gracefully
#
if __name__ == "__main__":
    main(sys.argv)

#
# end of file
