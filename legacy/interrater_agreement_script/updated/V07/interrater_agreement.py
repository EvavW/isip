#!/usr/bin/env python
# file: $(ISIP)/exp/tuh_eeg/exp_ ......
#
# revision history:
# 20170312
#
# usage:
# nedc_interrater_agreement.py -v --stat_type --tolerance --delta -o ofile
# arguments:
#     --stat_type        : statistics type, define that results should be calculated according to what statistic type.
#                          ( This script supports 1) cohen's Kappa 2) Fleiss Kappa & 3) Ratio based statistics )
#
#     -v                 : verbose mode. Along with printing/outputting end results/tables. This option also allows 
#                           us to see results based on each file.
#     --tolerance        : This option allows us to calculate Miss and FA more rigorously. If seizure events are
#                          over-annotated or missed for more than tolerance value then FA and Miss would be
#                          incremented accordingly. ( checkout the tolerance examples illustrated at the end )
#     --delta            : delta value allows to set/extend a margin for reference files (correct annotation files).
#     -o                 : print results in an output text file. ( both verbose and non-verbose options apply here).
#
# Example: Tolerance (e.g. 5 seconds)
#                                          SEIZURE
#        reference file  <--------------------------------------------->
#        hypothesis file      <-->                <------------>    <------------------>
#              if                 |---(> 5sec)---|                     |---(> 5sec)---|
#        resulting actions:        increment Miss                       increment FA
#
# Example: Delta (e.g. 5 seconds)
#                                                SEIZURE
#        Actual reference:                 <------------------>
#        After applying delta:  <----------------------------------------->
#        Result:                |--(+5)---|                   |---(+5)----|
#
# This script takes required flags as mentioned above and results confusion matrix for annotators as table form.
# 


## import system modules
#
import sys,os,argparse
# for auto completion bu Tab
import glob, readline
# import classes
import Annotators_annot_v07 as A_ANT

## import NEDC modules
#
sys.path.append(os.path.abspath("c:\\"))
import nedc_cmdl_parser as ncp


##----------------------------------------------------------------------------------------------------------
#
# Global variables are listed here
#
##----------------------------------------------------------------------------------------------------------
NEDC_HELP_FILE = ("/data/isip/exp/tuh_eeg/exp_.../scripts/"+
                  "nedc_interrater_agreement.help")
NEDC_USAGE_FILE = ("/data/isip/exp/tuh_eeg/exp_.../scripts/"+
                   "nedc_interrater_agreement.usage")

## define defaults for arguments
#
NEDC_DEF_VERBOSE = False
NEDC_DEF_STAT_TYPE = "ratio"
NEDC_DEF_TOLERANCE = 0
NEDC_DEF_DELTA = 0
NEDC_DEF_OUTPUT = "./results.txt"

## algorithm:
#  get reference files from my annotations and then hypothesis files from annotators' annotations
#  Set a flag for ratio_assessment or Kappa-Statistic assessment
#  First ask for number of annotators and set them to a dictionary.
#  again set a dictionary for individual file and their annotations should be stored inside an array. One can set two seperate arrays for start time and stop time.
#  also use map to use redundant functions for individual dictionary members.

##------------------------------------------------------------------------------------------------------------
#
# The main function starts from here
#
##------------------------------------------------------------------------------------------------------------

## method: main
#
# arguments: none
#
# return: none
#
# This method is the main function
#

def main():

    ## construct the full path of the help and usage files
    #
    help_file = NEDC_HELP_FILE
    usage_file = NEDC_USAGE_FILE

    verbose_flag = NEDC_DEF_VERBOSE
    stat_type = NEDC_DEF_STAT_TYPE
    tolerance = NEDC_DEF_TOLERANCE
    delta = NEDC_DEF_DELTA
    output_file = NEDC_DEF_OUTPUT

    ## create a command line parser
    #
    parser = ncp.CommandLineParser(usage_file, help_file)

    ## define command line arguments
    #
    parser.add_argument("--verbose", "-v", action = "store_true")
    parser.add_argument("--stat_type", type = str)
    parser.add_argument("--tolerance", type = int)
    parser.add_argument("--delta", type = int)
    parser.add_argument("--ofile", "-o", type = str)

    ## parse the command line
    #
    args = parser.parse_args()

    ## set and check values received from arguments to variables
    #
    ## the verbose flag
    #
    if args.verbose :
        verbose_flag = True
    else:
        verbose_flag = False
        
    ## statistics type
    #
    if args.stat_type is not None:
        stat_type = args.stat_type

    ## tolerance value
    #
    if args.tolerance is not None:
        tolerance = args.tolerance

    ## delta value
    #
    if args.delta is not None:
        delta = args.delta

    ## output/result file
    #
    if args.ofile is not None:
        output_file = args.ofile

    if os.path.exists(output_file):
        os.remove(output_file)

        ## open files
        #
    fo = open(output_file,'a')
    fo.write("The results of interrater agreement is as follows: \n")
    global fo, output_file
        
    ## end of argument definition
    #
    
    
    ## Set flags for selecting ratio based or Kappa Statistics based interrater agreement
    ## ratio based performance would provide a complete table of individual's performance with respect to each other and the reference which would be me (Vinit, by default).
    ## Kappa statistics based script would not be a good approach if annotators are not proficient enough because it uses no reference
    #


    
    #########################################################################################################################
    # parser = argparse.ArgumentParser()                                                                                  # #
    #                                                                                                                     # #
    # parser.add_argument("--stat_type", type=str, help=" select statistics type by entering either 'Kappa' or 'Ratio' ") # #
    #                                                                                                                     # #
    # args = parser.parse_args()                                                                                          # #
    #                                                                                                                     # #
    #                                                                                                                     # #
    # print args.stat_type                                                                                                # #
    # if args.stat_type == None:                                                                                          # #
    #     ratio_flag = True                                                                                               # #
    #                                                                                                                       #
    #                                                                                                                       #
    #                                                                                                                       #
    # elif args.stat_type.lower() == "kappa":                                                                               #
    #     kappa_flag = True                                                                                                 #
    #     print " Kappa Flag is True"                                                                                       #
    #                                                                                                                       #
    # elif args.stat_type.lower() == "ratio":                                                                               #
    #     ratio_flag = True                                                                                                 #
    #     print " Ratio Flag is True"                                                                                       #
    #                                                                                                                       #
    # else:                                                                                                                 #
    #     print "flag set is not Kappa or Ratio , add proper flag by command: --stat_type 'flag' "                          #
    #     print "Set correct flag, neither Kappa or Ratio has been entered"                                                 #
    #     sys.exit(1)                                                                                                       #
    #########################################################################################################################

    
## Enable autocompletion for raw_input command (by tab)
#
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(complete)
    


    
## add all the annotators name in dictionary before starting process.
#
    i = 0
    Annotators = dict()
    
    while True:

        annotator = raw_input("Add annotator's name, to end the sequence, type '.', to start over from the beginning, type 'begin' ")

        if annotator == ".":
            break

        elif annotator == "begin":
            main()

        else:
            annotator_filelist = raw_input("Provide %s's filelist: "%annotator)
            Annotators['%s'%annotator] = annotator_filelist


    ## ask for a reference's name wrt what the whole annotations would be assessed..
    #
    if stat_type != "ratio":
        reference_name = raw_input("Add a reference's name wrt what the whole annotations would be assessed:  ")

        ## call function Annotator files, which compares annotator's files among each other (annotator vs. reference)
        ## and provides the comparison
        #
        results_dict = Annotators_files(Annotators, reference_name,verbose_flag, tolerance, delta)



        for _annotator, results in results_dict.iteritems():
            print _annotator, "*****"
            print results, "*****"
        ## Calculate specificity and sensitivity from here
        #
            
    elif stat_type == "ratio":
###          work left to do, each annotator should be compared with each other; as a consequence this flag should provide multiple tables for each annotator as a reference.....
        reference_name = raw_input("Add a reference's name wrt what the whole annotations would be assessed:  ")
        print Annotators, " annotators"

        fo.write('--------------------------------  Sensitivity & Specificity  -------------------------------------------')
        for annotator_name, annotator_file in Annotators.iteritems():
###            import pdb;pdb.set_trace()
            exec("%s_as_ref_results_dict = Annotators_files(Annotators, '%s', verbose_flag, tolerance, delta)"%(annotator_name, annotator_name))
            exec("sensitivity_wrt_%s = calculate_sensitivity(%s_as_ref_results_dict)"%(annotator_name,annotator_name))
            exec("print(sensitivity_wrt_%s)"%annotator_name)
            fo.write('\n')
            exec("fo.write('w.r.t. %s as reference (Sensitivity):\t')"%annotator_name)
###            exec("for key,value in results_wrt_%s.iteritems(): fo.write('%s : %s\n'%(key,value))"%annotator_name)
###            exec("for key,value in results_wrt_%s.iteritems():fo.write(key)"%annotator_name)
            exec("results = '\t'.join(str(key)+ ':'+ str(value) + '%%' for key,value in sensitivity_wrt_%s.items())"%annotator_name)
            exec("fo.write(results)")


            exec("specificity_wrt_%s = calculate_specificity(%s_as_ref_results_dict)"%(annotator_name,annotator_name))
            exec("print(specificity_wrt_%s)"%annotator_name)
            fo.write('\n')
            exec("fo.write('w.r.t. %s as reference (Specificity):\t')"%annotator_name)
###            exec("for key,value in results_wrt_%s.iteritems(): fo.write('%s : %s\n'%(key,value))"%annotator_name)
###            exec("for key,value in results_wrt_%s.iteritems():fo.write(key)"%annotator_name)
            exec("results = '\t'.join(str(key)+ ':'+ str(value) + '%%' for key,value in specificity_wrt_%s.items())"%annotator_name)
            exec("fo.write(results)")

            
#            fo.write(":")
#            exec("fo.write(str(value))")


        print " individual's results "

        

    

## Annotators are added to a dictionary with numbers as keys
#

def Annotators_files(annot_dict, reference_name, verbose_flag, tolerance, delta):
## Get the list of files and associate that with individual annotators
#
    Annotators_list = []
    Annotators_corresponding_filelist = []
    
    for annotators, annot_file in annot_dict.iteritems():
        exec("%s = A_ANT.annot_info('%s','%s')"%(annotators,annotators, annot_file))

        ## all annotators and their associated files are created here...
        ## Run a for loop to separate files and create a list of files for each annotator
        #

        op = open('%s'%annot_file,'r').read()
        exec("%s_filelist = op.split(%s)"%(annotators,"\n"))


        exec("vprint(%s_filelist,%s)"%(annotators,verbose_flag))
        ###print Vinit_filelist

        ## collecting all the annotation files from individual annotators and sending the list to
        ## a perticular function which can collect everything.
        #

        exec("Annotators_list.append(%s.name)"%annotators)
        exec("Annotators_corresponding_filelist.append(%s_filelist)"%annotators)
        
        exec("annot_filelist = %s_filelist"%annotators)
        execute_files_4_individuals(('%s'%annotators),annot_filelist)

    vprint(Annotators_list,verbose_flag)
    vprint(Annotators_corresponding_filelist,verbose_flag)

    Annot_operations = A_ANT.compare_annotation_files(verbose_flag,tolerance,delta,output_file)
    results_dict = Annot_operations.prepare_annotator_filelist(Annotators_list, Annotators_corresponding_filelist, reference_name)
    vprint(results_dict,verbose_flag)

    return results_dict

    
def execute_files_4_individuals(annotator,annot_filelist):

    ## run a loop through each list assigned to each annotator
    #
    for filenames in annot_filelist:
        if filenames == '':
            break

        ## sort all the files by its first field
        #
### Conversion of files to sorted version is required from here...
        

        
        ## define a variable's name for an array where start and stop times for seizures
        ## would be saved
        #
        array_name_splitted = filenames.split(r'/')
        array_name = '_'.join(array_name_splitted)
        ###print array_name


        
        ## Open the annotation file and read its content
        #
        op = open(filenames,'r').read()
        file_cont = op.split('\n')

        for lines in file_cont:
            if lines == "":
                break



def calculate_sensitivity(Annotator_as_ref_results_dict):
    sensitivity_dict = {}
    for _annotator , ann_results in Annotator_as_ref_results_dict.iteritems():
        separate_results = ann_results.split(',')
        _ann_hit = float(separate_results[0])
        _ann_miss = float(separate_results[1])
        _ann_FA = float(separate_results[2])

        ## calculate sensitivity in percentage
        #
        calculated_sensitivity = 100*_ann_hit / (_ann_hit + _ann_miss)
        sensitivity_dict[_annotator] = "%.2f"%calculated_sensitivity


    return sensitivity_dict

def calculate_specificity(Annotator_as_ref_results_dict):
    specificity_dict = {}
    for _annotator, ann_results in Annotator_as_ref_results_dict.iteritems():
        separate_results = ann_results.split(',')

        _ann_seiz_FA_epochs = float(separate_results[6])
        _ref_epochs = float(separate_results[4])
        _hyp_epochs = float(separate_results[5])

        ## calculate specificity in percentage
        #
        calculated_specificity = 100*( 1 - (_ann_seiz_FA_epochs / _ref_epochs))
        if calculated_specificity > 100:
            calculated_specificity = 100.0
        
        specificity_dict[_annotator] = "%.2f"%calculated_specificity

    return specificity_dict
                                            
        


   
## function for verbose mode
#
def vprint(string,verbose_flag):
    if verbose_flag == True:
        print string




        
## for autocompletion by Tab
#

def complete(text, state):
    return (glob.glob(text+'*')+[None])[state]



if __name__=="__main__": main()
