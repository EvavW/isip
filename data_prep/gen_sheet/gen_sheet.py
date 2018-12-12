#!/usr/bin/env python
#
# usage:
# python gen_sheet.py -info [session info] tse.list
#
# This script creates the _SEIZURES spreadhseet values
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
USAGE_FILE="/data/isip/data/tuh_eeg_seizure/work/_TOOLS/data_prep/gen_sheet/gen_sheet.usage"
HELP_FILE="/data/isip/data/tuh_eeg_seizure/work/_TOOLS/data_prep/gen_sheet/gen_sheet.help"

# define minimum number of arguments
# 
NUM_ARGS = 1

print_index = 1

def main(argv):

    #create a command line parser
    #
    parser = ncp.CommandLineParser(USAGE_FILE, HELP_FILE)
    
    #define command line arguments
    #
    parser.add_argument("args", type = str, nargs='*')
    parser.add_argument("-info", "-o", type = str)
    parser.add_argument("-help", action="help")

    #parse the command line
    #
    args = parser.parse_args()

    # check if the proper number of lists has been provided
    #
    if len(args.args) != NUM_ARGS:
        parser.print_usage()
        exit(-1)

    # set the info array
    #
    if args.info is not None:
        info_file = args.info

    # set the input file lists names
    #
    tse_list_name = args.args[0]

    #load the lists
    #
    tse_list = nft.get_flist(tse_list_name)

    if (tse_list == None):
        print  "%s (%s: %s): error loading input list (%s)" % \
            (sys.argv[0], __name__, "main", tse_list_name)
        exit (-1)

    # translate session_info.csv into an array
    #
    info_list_array = [line.rstrip('\n') for line in open(info_file)]
    
    # list to store processed session info
    #
    info_array = []

    #loop through each line in the info file
    #
    for session_info in info_list_array:
     
        # remove new line characters, split the line
        #
        session_info = session_info.replace(nft.DELIM_NEWLINE, nft.DELIM_NULL)
        parts = session_info.split(nft.DELIM_COMMA)

        # remove carriage return characters that appear after normal/abnormal
        #
#        parts[5] = parts[5].replace('\r','')

        # append each session to session_info
        #
        info_array.append([parts[0],parts[1],parts[2],parts[3],
                             parts[4],parts[5]])

    # print sheet headers before looping through filelist
    #
    print ",,,,,,,,,,,,Seizure Time,"
    print "Index,File No.,Patient,Session,File,EEG Type,EEG SubType,LTM -or- Routine,Normal/Abnormal,No. Seizures/File,No. Seizures/Session,Filename,Start,Stop,Seizure_Type"

    #loop through the files
    #
    file_index = 1
    global print_index
    print_index = 1

    done_sessions = []
    for tse_file in tse_list:
        
        # read the tse file
        #
        lines = [line.rstrip('\n') for line in open(tse_file)]
        
        # list to store events
        #
        events = []
        
        # loop over lines in the tse file
        #
        for line in lines:

            # make sure that we are looking at an acutal label
            #
            if (not line.startswith("#")) and \
               (not line.startswith("version")) and \
               "bckg" not in line and \
               line:

                # remove spaces and newline chars, split the line
                #
                line = line.replace(nft.DELIM_NEWLINE, nft.DELIM_NULL)
                parts = line.split(nft.DELIM_SPACE)

                # append lines to events
                #
                events.append([float(parts[0]), float(parts[1]),\
                               parts[2], float(parts[3])])
              
        # get basic info about this tse file
        #
        file_info = get_file_info(tse_file,tse_list_name,events)
        
        # print relevant info from this file to the console
        # update local print_index
        #
        #print_index=print_sheet(file_info,events,done_sessions,info_array,\
        #                        file_index)#,print_index)
        print_sheet(file_info,events,done_sessions,info_array, file_index)

        # iterate the file index number
        #
        file_index+=1

        # add this session to the list of accessed sessions
        #
        done_sessions.append(file_info[3])

    # end for tse_file in tse_list
        
    return True

def get_file_info(tse_file_a,tse_list_name_a,events_a):

    # extract info from the name of the tse file
    #
    file_parts = tse_file_a.split("/")
    file_num = file_parts[len(file_parts)-1].split("_")[2].split(".")[0]
    patient = file_parts[len(file_parts)-3].lstrip("0")
    sesh_num = file_parts[len(file_parts)-2].split("_")[0]
    session = "%s_%s" % (patient,sesh_num)
        
    # get the number of seizures for this session
    #
    cmd = "grep %s %s | xargs grep 1.000 | grep -v bckg | wc -l"\
          %(session,tse_list_name_a)

    seiz_sesh = os.popen('%s'%cmd).read()
    seiz_sesh = int(seiz_sesh)

    # count number of seizures for this file
    #
    num_seiz = 0
    for event in events_a:
        if event[2] != "bckg":
            num_seiz+=1
    
    # end for event in events_a

    # add all info into file_info
    #
    file_info= [file_num, patient, sesh_num, session, num_seiz, seiz_sesh, tse_file_a ]

    # return file_info array
    #
    return file_info


def print_sheet(file_info_a,events_a,done_sessions_a,info_array_a,\
                file_index_a):#,print_index_a):

    global print_index
    #extract info from file_info_a
    #
    file_num = file_info_a[0]
    patient = file_info_a[1]
    session_num = file_info_a[2]
    session = file_info_a[3]
    num_seiz = file_info_a[4]
    seiz_sesh = file_info_a[5]
    tse_file = file_info_a[6]

    # if this is the first file in the session:
    #
    if session not in done_sessions_a:

        # extract info about this session
        #
        j=0
        for session_info in info_array_a:

            #find this session in info_array_a
            #
            if session_info[0] == patient and session_info[1] == session_num:
                
                eeg_type = session_info[2]
                eeg_sub_type = session_info[3]
                ltm_routine = session_info[4]
                norm_ab = session_info[5]
            
        # if there are seizures in this file:
        #
        if len(events_a) != 0:

            # iterate through all seizure events_a
            #
            i=0
            for event in events_a:
                
                # extract seizure info
                #
                start=event[0]
                stop=event[1]
                label=event[2].upper()

                # if this is the first seizure, print file and sesh info
                #
                if i == 0:
                    print "%d,%d,%s,%s,%s,%s,%s,%s,%s,%d,%d,%s,%.4f,%.4f,%s"\
                        %(print_index,file_index_a,patient,session_num,\
                          file_num,eeg_type,eeg_sub_type,ltm_routine,norm_ab,\
                          num_seiz,seiz_sesh,tse_file,start,stop,label)

                    print_index+=1

                # if this is not the first, only print seizure info
                #
                else:
                    
                    print "%d,%d,,,,,,,,,,%s,%.4f,%.4f,%s"\
                        %(print_index,file_index_a,tse_file,start,stop,label)

                    print_index+=1
                    
                i+=1
        
        # if there are no seizures in this file print only file and sesh info
        #
        else:

            print "%d,%d,%s,%s,%s,%s,%s,%s,%s,%d,%d,%s,,,"\
                %(print_index,file_index_a,patient,session_num,\
                  file_num,eeg_type,eeg_sub_type,ltm_routine,norm_ab,
                  num_seiz,seiz_sesh,tse_file)
            
            print_index+=1

    # if this is not the first file in the session:
    #
    else:

        # if there are seizures in this file
        #
        if len(events_a) != 0:

            # iterate through each seizure event
            #
            i=0
            for event in events_a:

                # extract seizure info
                #
                start=event[0]
                stop=event[1]
                label=event[2].upper()

                # if this is the first seizure print file and seiz info
                #
                if i == 0:
                    print "%d,%d,,,%s,,,,,%d,,%s,%.4f,%.4f,%s"\
                        %(print_index,file_index_a,file_num,num_seiz,\
                          tse_file,start,stop,label)

                    print_index +=1

                # if this is not the first seizure print only seiz info
                #
                else:
                    print "%d,%d,,,,,,,,,,%s,%.4f,%.4f,%s"\
                        %(print_index,file_index_a,tse_file,start,stop,label)

                    print_index+=1
            
                i+=1
                                
        # if there are no seizures in this file print only file info
        #
        else:
            print "%d,%d,,,%s,,,,,%d,,%s,,,"\
                %(print_index,file_index_a,file_num,num_seiz,tse_file)

            print_index+=1

    # end function and update print_index
    #
#    return print_index
    return True
# end script
#

if __name__ == "__main__":

    main(sys.argv[:])

