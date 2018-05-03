
# import NEDC modules
#
import nedc_cmdl_parser as ncp
import nedc_eval_tools as ntools
import ConfigParser

# import system modules
#
import os,re
import sys

#---------------------------------------------------------
#
# global variables are listed here
#
#---------------------------------------------------------

# define the help file and usage message
#
NEDC_HELP_FILE = ("/util/python/nedc_rescore_nist/nedc_rescore_nist.help")
NEDC_USAGE_FILE = ("/util/python/nedc_rescore_nist/nedc_rescore_nist.usage")

NEDC_LIST = ''
NEDC_DEF_RDIR=''
NEDC_DEF_ODIR = os.environ.get("PWD")
NEDC_DEF_MFILE=''

# default extensions
#
NEDC_DEF_EDFEXT='.ehyp'

NEDC_DEF_MAKEDIRS_ERROR=17
#------------------------------------------------------------------------------
#
# the main program starts here
#
#------------------------------------------------------------------------------


def main(argv):

     # construct the full path of the help and usage files
    #
    help_file = os.environ.get("NEDC_NFC") + NEDC_HELP_FILE
    usage_file = os.environ.get("NEDC_NFC") + NEDC_USAGE_FILE

    # declare default values for command line arguments
    #
    ilist_a = NEDC_LIST
    mfile_a = NEDC_DEF_MFILE
    rdir_a = NEDC_DEF_RDIR
    odir_a = NEDC_DEF_ODIR
    
    # create a command line parser
    #
    parser = ncp.CommandLineParser(usage_file, help_file)
    
    # define the command line arguments
    #
    parser.add_argument("ilist",  type = str, nargs='*')
    parser.add_argument("-rdir", "-r", type = str)
    parser.add_argument("-odir", "-o", type = str)
    parser.add_argument("-mfile", "-m", type =str)
	
    # parse the command line
    #
    args = parser.parse_args()
    
    # set and check values received from arguments to variables
    #
    # the output argument which is the full path of the output directory
    #
    if args.odir is not None:
        odir_a = args.odir
                
    # the replace argument which is an extension to the output path
    #
    if args.rdir is not None:
        rdir_a = args.rdir

		
    # the input argument which is list or a list of .lab files
    #
    if args.ilist is not None:
        list_a = args.ilist[0]

    # a mapping file controlling how scoring is done
    #
    if args.mfile is not None:
        mfile_a = args.mfile

    # check if labfiles_a list is empty
    #
    if list_a == []:
        parser.print_usage()
        exit(-1)

    # load the parameter file
    #
    scmap, nist_f4de, nedc_dpalign, nedc_epoch, nedc_ovlp, nedc_taes, \
        nedc_ira= ntools.nedc_eval_load_params(mfile_a)        
        
    i = 0
    with open(list_a,'rb') as f:
        for fline in f:
            print "filename is: ", fline
            filename = fline.strip()

            start_list = []
            stop_list = []
            event_list = []
            score_list = []
            sorted_start_list = []
            sorted_stop_list = []
            soretd_event_list = []
            sorted_score_list = []

            with open(filename, 'rb') as f_cont:


                for line in f_cont:
                    print "line is: ", line
                    # find start and stop times on each line
                    #
                    parts = line.split()
                    
                    start_list.append(int(parts[0]))
                    stop_list.append(int(parts[1]))

                    for key, values in scmap.iteritems():
                        for value in values:
                            if value.lower() == parts[2].lower():
                                event_list.append(key.lower())
                    
                    if len(parts) != 4:
                        score_list.append(1)

                    else:
                        score_list.append(float(parts[3]))
                sorted_start_list, sorted_stop_list, sorted_event_list, \
                    sorted_score_list= zip(*sorted(zip(start_list, stop_list, \
                                                       event_list, score_list)))
                # end of for
                #
                start_list = []
                stop_list = []
                event_list = []
                score_list = []

                # if term is true all concurrent same epoches will be marged
                #    and created a long term
                #
                i = 0
                # loop over to find the consecutive events
                #
                while i < len(sorted_start_list):
                    status = False
                    sum_score = float(0)
                    ave_score = float(0)

                    # find the current start time , stop time, event, and
                    # probability
                    #
                    currnt_start = sorted_start_list[i]
                    currnt_stop = sorted_stop_list[i]
                    current_event = sorted_event_list[i]
                    current_score = sorted_score_list[i]
                    sum_score = sum_score + float(current_score)

                    j = i + 1

                    # find consecutive events and attach them to make a term
                    #
                    num_cons_t = 1
                    while j < len(sorted_start_list) and \
                          current_event.lower() == \
                          sorted_event_list[j].lower() :
                        status = True
                        num_cons_t += 1      

                        currnt_stop = sorted_stop_list[j]
                        sum_score = sum_score + float(sorted_score_list[j])

                        j += 1

                    # end of while

                    # if the flag status is true
                    #
                    if status:

                        # find the average score of each term
                        #
                        ave_score = sum_score / (num_cons_t)
                        i = j
                    else:
                        ave_score = float(current_score)
                        i += 1
                    # end of if       
                    
                    start_list.append(round(currnt_start/float(100000)))
                    stop_list. append(round(currnt_stop/float(100000)))
                    event_list.append(current_event.lower())
                    score_list.append(ave_score)
   
                    
                print "------------> start: ", start_list
                print "------------> stop: ", stop_list
                print "------------> event: ", event_list
                print "------------> score: ", score_list


                ofile_path = (f_cont.name).replace(rdir_a, odir_a)
                ofile_path = ofile_path.replace(os.path.splitext(os.path.basename(f_cont.name))[1],(".tse"))
            
                ofile_dir = os.path.dirname(ofile_path)
                try:
                    os.makedirs(ofile_dir)
                except OSError as e:
                    if e.errno != NEDC_DEF_MAKEDIRS_ERROR:
                        raise

                # save the output in hyp file.
                #
                target = open(ofile_path, 'w')
                target.write("# example: foo.tse\n#\n")
                target.write("version = tse_v1.0.0\n\n")
                target.write("# data starts here\n#\n")

                for i in range(len(start_list)):

                    target.write("%04.4f" % float(start_list[i]))
                    target.write("\t")
                    target.write("%04.4f" % float(stop_list[i]))
                    target.write("\t")
                    target.write("%s" % (str(event_list[i])))
                    target.write("\t")
                    target.write("%.6f" % float(score_list[i]))
                    target.write("\n")

                



if __name__=="__main__":main(sys.argv[:])
