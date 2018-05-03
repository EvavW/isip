import sys,os,argparse
# for auto completion bu Tab
import glob, readline
# import classes
import Annotators_annot_v03 as A_ANT

## algorithm:
#  get reference files from my annotations and then hypothesis files from annotators' annotations
#  Set a flag for ratio_assessment or Kappa-Statistic assessment
#  First ask for number of annotators and set them to a dictionary.
#  again set a dictionary for individual file and their annotations should be stored inside an array. One can set two seperate arrays for start time and stop time.
#  also use map to use redundant functions for individual dictionary members.

def main():

## Set flags for selecting ratio based or Kappa Statistics based interrater agreement
## ratio based performance would provide a complete table of individual's performance with respect to each other and the reference which would be me (Vinit, by default).
## Kappa statistics based script would not be a good approach if annotators are not proficient enough because it uses no reference
#


    parser = argparse.ArgumentParser()

    parser.add_argument("--stat_type", type=str, help=" select statistics type by entering either 'Kappa' or 'Ratio' ")

    args = parser.parse_args()


    print args.stat_type
    if args.stat_type == None:
        ratio_flag = True


    elif args.stat_type.lower() == "kappa":
        kappa_flag = True
        print " Kappa Flag is True"

    elif args.stat_type.lower() == "ratio":
        ratio_flag = True
        print " Ratio Flag is True"

    else:
        print "flag set is not Kappa or Ratio , add proper flag by command: --stat_type 'flag' "
        print "Set correct flag, neither Kappa or Ratio has been entered"
        sys.exit(1)

    
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

    reference_name = raw_input("Add a reference's name wrt what the whole annotations would be assessed:  ")
    Annotators_files(Annotators, reference_name)


## Annotators are added to a dictionary with numbers as keys
#

def Annotators_files(annot_dict, reference_name):
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


        exec("print %s_filelist"%annotators)
        ###print Vinit_filelist

        ## collecting all the annotation files from individual annotators and sending the list to
        ## a perticular function which can collect everything.
        #

        exec("Annotators_list.append(%s.name)"%annotators)
        exec("Annotators_corresponding_filelist.append(%s_filelist)"%annotators)
        
        exec("annot_filelist = %s_filelist"%annotators)
        execute_files_4_individuals(('%s'%annotators),annot_filelist)

    print Annotators_list
    print Annotators_corresponding_filelist

    Annot_operations = A_ANT.compare_annotation_files()
    results_dict = Annot_operations.prepare_annotator_filelist(Annotators_list, Annotators_corresponding_filelist, reference_name)

    print results_dict, " main func"

    
    for _annotator, results in results_dict.iteritems():
        print _annotator
        print results



    
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

            
   
    





## for autocompletion by Tab
#

def complete(text, state):
    return (glob.glob(text+'*')+[None])[state]



if __name__=="__main__": main()
