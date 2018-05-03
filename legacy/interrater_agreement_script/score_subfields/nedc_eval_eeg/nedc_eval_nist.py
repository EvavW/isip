#!/usr/bin/env python            
#
# file: $NEDC_NFC/python/nedc_eval_tools/nedc_eval_nist.py
#                                                                              
# revision history: 
#  20170815 (JP): added another metric: prevalence
#  20170812 (JP): changed the divide by zero checks
#  20170716 (JP): upgraded to using the new annotation tools
#  20170709 (JP): refactored code for the new environment
#  20170702 (JP): added summary scoring; revamped derived metrics
#  20170622 (JP): rewritten to conform to standards
#  20170527 (JP): cosmetic revisions
#  20161230 (SL): revision for standards
#  20160627 (SZ): initial version                                              
#                                                                              
# usage:                                                                       
#  import nedc_eval_nist as nnist                                         
#                                                                              
# This file contains Python code that interfaces our scoring software
# to the NIST KWS scoring software
#------------------------------------------------------------------------------

# import required system modules
#
import os
import sys
import re
from collections import OrderedDict

# import required NEDC modules
#
import nedc_file_tools as nft
import nedc_ann_tools as nat
import nedc_text_tools as ntt

#------------------------------------------------------------------------------
#                                                                              
# define important constants
#                                                                              
#------------------------------------------------------------------------------

# define paramter file constants
#
NIST_F4DE = "NIST_F4DE"

#------------------------------------------------------------------------------
#                                                                              
# the main interface method
#                                                                              
#------------------------------------------------------------------------------

# method: run
#
# arguments:
#  reflist: the reference file list
#  hyplist: the hypothesis file list
#  map: a mapping used to collapse classes during scoring
#  nist_f4de: the NIST scoring algorithm parameters
#  odir: the output directory
#  rfile: the results file (written in odir)
#  fp: a pointer to the output summary file
#
# return: a logical value indicating status
#
# This method runs the NIST scoring software by:
#  (1) creating the necessary inputs
#  (2) running NIST scoring
#  (3) retrieving the results
#
def run(reflist_a, hyplist_a, map_a, nist_f4de_a, odir_a, rfile_a, fp_a):

    # define local variables
    #
    status = True
    nnist = NISTF4DE(nist_f4de_a)

    # create the output directory
    #
    odir = nft.make_fname(odir_a, nnist.output_directory_d)
    status = nft.make_dir(odir)
    if status == False:
        print "%s (%s: %s): error creating directory (%s)" % \
            (sys,argv[0], __name__, "run", odir)
        return False
        
    # create the necessary inputs to run the NIST scoring
    #
    status = nnist.create_input(reflist_a, hyplist_a, map_a, odir)
    if status == False:
        print "%s (%s: %s): error creating input data" % \
            (sys.argv[0], __name__, "run")
        return False

    # run the NIST scoring
    #
    status = nnist.init_score(map_a)
    status = nnist.score(odir)
    if status == False:
        print "%s (%s: %s): error during scoring" % \
            (sys.argv[0], __name__, "run")
        return False

    # fetch the results from the NIST output files
    #
    fname_bsum = nnist.get_ofilename(odir)
    status = nnist.get_results(fname_bsum, map_a)
    if status == False:
        print "%s (%s: %s): error during scoring" % \
            (sys.argv[0], __name__, "run")
        return False

    # compute performance
    #
    status = nnist.compute_performance()
    if status == None:
        print "%s (%s: %s): error computing performance" % \
            (sys.argv[0], __name__, "run")
        return False

    # collect information for scoring and display
    #
    status = nnist.display_results(fp_a)
    if status == False:
        print "%s (%s: %s): error displaying results" % \
            (sys.argv[0], __name__, "run")
        return False

    # exit gracefully
    #
    return status
#
# end of function
    
#------------------------------------------------------------------------------
#                                                                              
# classes are listed here                                                      
#                                                                              
#------------------------------------------------------------------------------

# class: NISTF4DE
#
# This class contains methods to generate input files for NIST scoring and\
# generate output file.
#
class NISTF4DE():

    # method: constructor
    #
    # arguments: none
    #
    # return: none
    #
    def __init__(self, params_a):

        # decode the parameters passed from the parameter file
        #
        self.koefcorrect_d = float(params_a['koefcorrect'])
        self.koefincorrect_d = float(params_a['koefincorrect'])
        self.delta_d = float(params_a['delta'])
        self.probterm_d = float(params_a['probterm'])

        self.fname_kwslist_d = params_a['fname_kwslist']
        self.fname_kwlist_d = params_a['fname_kwlist']
        self.fname_rttm_d = params_a['fname_rttm']
        self.fname_ecf_d = params_a['fname_ecf']
        self.fname_bsum_d = params_a['fname_bsum']
        self.fname_log_d = params_a['fname_log']
        self.output_directory_d = params_a['output_directory']
        self.basename_d = params_a['basename']
        self.command_d = params_a['command']

        # declare a variable to hold a permuted map
        #
        self.pmap_d = {}

        # declare a duration parameter used to calculate the false alarm rate:
        #  we need to know the total duration of the data in secs of each
        #  file for NIST scoreing and the total duration for 
        #  false alarm computations
        #
        self.fdur_d = []
        self.total_dur_d = float(0)

        # declare parameters to track errors:
        #  all algorithms should track the following per label:
        #   substitutions, deletions, insertions, hits, misses
        #   and false alarms.
        #
        self.tp_d = {}
        self.tn_d = {}
        self.fp_d = {}
        self.fn_d = {}

        self.tgt_d = {}
        self.hit_d = {}
        self.mis_d = {}
        self.fal_d = {}
        self.ins_d = {}
        self.del_d = {}

        # additional derived data:
        #  we use class data to store a number of statistical measures
        #
        self.tpr_d = {}
        self.tnr_d = {}
        self.ppv_d = {}
        self.npv_d = {}
        self.fnr_d = {}
        self.fpr_d = {}
        self.fdr_d = {}
        self.for_d = {}
        self.acc_d = {}
        self.msr_d = {}
        self.prv_d = {}
        self.f1s_d = {}
        self.flr_d = {}

        # declare parameters to compute summaries
        #
        self.sum_tp_d = int(0)
        self.sum_tn_d = int(0)
        self.sum_fp_d = int(0)
        self.sum_fn_d = int(0)

        self.sum_tgt_d = int(0)
        self.sum_hit_d = int(0)
        self.sum_mis_d = int(0)
        self.sum_fal_d = int(0)
        self.sum_ins_d = int(0)
        self.sum_del_d = int(0)

        # additional derived data:
        #  we use class data to store a number of statistical measures
        #
        self.sum_tpr_d = float(0)
        self.sum_tnr_d = float(0)
        self.sum_ppv_d = float(0)
        self.sum_npv_d = float(0)
        self.sum_fnr_d = float(0)
        self.sum_fpr_d = float(0)
        self.sum_fdr_d = float(0)
        self.sum_for_d = float(0)
        self.sum_acc_d = float(0)
        self.sum_msr_d = float(0)
        self.sum_prv_d = float(0)
        self.sum_f1s_d = float(0)
        self.sum_flr_d = float(0)

        # algorithm-specific computed data
        #
        self.twv_d = {}
        self.sum_twv_d = float(0)

        # exit gracefully
        #
        
    # method: init_score
    #
    # arguments:
    #  map: a scoring map
    #
    # return: a logical value indicating status
    #
    # This method initializes parameters used to track errors.
    # We use ordered dictionaries that are initialized in the order
    # labels appear in the scoring map.
    #
    def init_score(self, map_a):
        
        # initialize global counters:
        #  note that total_dur_d is computed prior to this to interface
        #  to the NIST software, and should not be resset here.
        #

        # initialiaze parameters to track errors:
        #  these are declared as ordered dictionaries organized
        #  in the order of the scoring map
        #
        self.tp_d = OrderedDict()
        self.tn_d = OrderedDict()
        self.fp_d = OrderedDict()
        self.fn_d = OrderedDict()

        self.tgt_d = OrderedDict()
        self.hit_d = OrderedDict()
        self.mis_d = OrderedDict()
        self.fal_d = OrderedDict()
        self.sub_d = OrderedDict()
        self.ins_d = OrderedDict()
        self.del_d = OrderedDict()

        self.tpr_d = OrderedDict()
        self.tnr_d = OrderedDict()
        self.ppv_d = OrderedDict()
        self.npv_d = OrderedDict()
        self.fnr_d = OrderedDict()
        self.fpr_d = OrderedDict()
        self.fdr_d = OrderedDict()
        self.for_d = OrderedDict()
        self.acc_d = OrderedDict()
        self.msr_d = OrderedDict()
        self.prv_d = OrderedDict()
        self.f1s_d = OrderedDict()
        self.flr_d = OrderedDict()

        # declare parameters to compute summaries
        #
        self.sum_tp_d = int(0)
        self.sum_tn_d = int(0)
        self.sum_fp_d = int(0)
        self.sum_fn_d = int(0)

        self.sum_tgt_d = int(0)
        self.sum_hit_d = int(0)
        self.sum_mis_d = int(0)
        self.sum_fal_d = int(0)
        self.sum_ins_d = int(0)
        self.sum_del_d = int(0)

        self.sum_tpr_d = float(0)
        self.sum_tnr_d = float(0)
        self.sum_ppv_d = float(0)
        self.sum_npv_d = float(0)
        self.sum_fnr_d = float(0)
        self.sum_fpr_d = float(0)
        self.sum_fdr_d = float(0)
        self.sum_for_d = float(0)
        self.sum_msr_d = float(0)
        self.sum_f1s_d = float(0)
        self.sum_flr_d = float(0)

        # declare algorithm-specific paramters
        #
        self.twv_d = OrderedDict()
        self.sum_twv_d = float(0)

        # establish the order of these dictionaries in terms of
        # the scoring map.
        #
        for key in map_a:

            self.tp_d[key] = int(0)
            self.tn_d[key] = int(0)
            self.fp_d[key] = int(0)
            self.fn_d[key] = int(0)

            self.tgt_d[key] = int(0)
            self.hit_d[key] = int(0)
            self.mis_d[key] = int(0)
            self.fal_d[key] = int(0)
            self.ins_d[key] = int(0)
            self.del_d[key] = int(0)

            self.tpr_d[key] = float(0)
            self.tnr_d[key] = float(0)
            self.ppv_d[key] = float(0)
            self.npv_d[key] = float(0)
            self.fnr_d[key] = float(0)
            self.fpr_d[key] = float(0)
            self.fdr_d[key] = float(0)
            self.for_d[key] = float(0)
            self.acc_d[key] = float(0)
            self.msr_d[key] = float(0)
            self.prv_d[key] = float(0)
            self.f1s_d[key] = float(0)
            self.flr_d[key] = float(0)

            self.twv_d[key] = float(0)

        # permute the map: we need this in various places
        #
        self.pmap_d = nft.permute_map(map_a)

        # exit gracefully
        # 
        return True
    #
    # end of method

    # method: get_ofilename
    #
    # arguments:
    #  odir: output directory
    #
    # return:
    #  fname_bsum: the full pathname of the NIST output file
    #
    # This method returns the path of the NIST output file.
    #
    def get_ofilename(self, odir_a):
        return nft.make_fname(odir_a, self.fname_bsum_d)

    # method: create_input
    #
    # arguments:
    #  reflist: filelist of reference files
    #  hyplist: filelist of hypothesis files
    #  map: list of event names to be scored
    #  odir: output directory
    #
    # return: a logical value indicating status
    #
    # This method creates the following files required by the NIST
    # scoring software (in this order): (1) *.kwlist.xml, (2) *.rttm.xml,
    # (3) *.kwslist.xml, (4) *.ecf.xml.
    #
    def create_input(self, reflist_a, hyplist_a, map_a, odir_a):

        # check the reference and hyp file lists
        #
        num_files_ref = len(reflist_a)
        num_files_hyp = len(hyplist_a)

        if num_files_ref < 1 or num_files_hyp < 1 or \
           num_files_ref != num_files_hyp:
            print "%s (%s: %s): mismatched file listsfile list error (%d %d)" \
                % (sys.argv[0], __name__, "create_input", \
                   num_files_ref, num_files_hyp)
            return False

        # generate unique tags for each filename in the annotation list:
        #  the NIST software needs each 'filename' to be unique.
        #
        tags = self.create_unique_tags(reflist_a)

        # generate the kwlist file:
        #  note that we apply the class mapping here
        #
        fname_kwlist = nft.make_fname(odir_a, self.fname_kwlist_d)
        status = self.create_kwlist(fname_kwlist, map_a)
        if status == False:
            print "%s (%s: %s): kwlist creation error (%s)" \
                % (sys.argv[0], __name__, "create_input", self.fname_kwlist_d)
            return False
        
        # generate the rttm file:
        #  we need to permute the map so that lookup is fast
        #
        fname_rttm = nft.make_fname(odir_a, self.fname_rttm_d)
        pmap = nft.permute_map(map_a)
        self.fdur_d = \
		self.create_rttm(fname_rttm, reflist_a, tags, pmap)
        if self.fdur_d == None or len(self.fdur_d) == 0:
            print "%s (%s: %s): rttm creation error (%s)" \
                % (sys.argv[0], __name__, "create_input", self.fname_rttm_d)
            return False
        self.total_dur_d = sum(self.fdur_d)
        
        # generate the kwslist file
        #
        fname_kwslist = nft.make_fname(odir_a, self.fname_kwslist_d)
        status = self.create_kwslist(fname_kwslist, hyplist_a, tags,
                                     map_a, odir_a)
        if status == False:
            print "%s (%s: %s): kwslist creation error (%s)" \
                % (sys.argv[0], __name__, "create_input", self.fname_kwslist_d)
            return False
        
        # generate the ecf file
        #
        fname_ecf = nft.make_fname(odir_a, self.fname_ecf_d)
        status = self.create_ecf(fname_ecf, reflist_a, tags, self.fdur_d,
                                 self.total_dur_d)
        if status == False:
            print "%s (%s: %s): ecf creation error (%s)" \
                % (sys.argv[0], __name__, "create_input", self.fname_ecf_d)
            return False
                
        # exit gracefully
        #
        return status
    #
    # end of method
    
    # method: create_unique_tags
    #
    # arguments:
    #  list: a list of filenames
    #
    # return: a list of unqiue tags
    #
    # This method creates list of tags based on the filename
    # provided. It is assumed that a full pathname is provided,
    # including the directory name. The directory delimiter is replaced
    # with an underscore.
    #
    def create_unique_tags(self, list_a):

        # declare an output list
        #
        tags = []
        
        # loop over list file
        #
        for fname in list_a:
            tags.append(fname.replace(nft.DELIM_SLASH, nft.DELIM_USCORE))

        # exit gracefully
        #
        return tags
    #
    # end of method

    
    # method: create_kwlist
    #
    # arguments:
    #  fname: full pathname of the kwlist file
    #  map: a mapping used to collapse classes for scoring
    #
    # return: a logical value indicating the status
    #
    # This method creates a NIST-formatted XML file known
    # as a keyword list file (kwlist).
    #
    def create_kwlist(self, fname_a,  map_a):
        
       # open the file and write the body tag
       #
       fp = nft.make_fp(fname_a)
       fp.write('<kwlist ecf_filename="%s" version="01" '\
                 'language="english" compareNormalize=""' \
                ' encoding="UTF-8">\n' % self.fname_ecf_d)
      
       # loop over the mapping file and write each term
       #
       for key in map_a:
           fp.write('  <kw kwid="term-%(0)s"><kwtext>%(0)s</kwtext></kw>\n' 
                    % {"0":key})

       # write end of body tag and close the file
       #
       fp.write('</kwlist>')
       fp.close()
       
       # exit gracefully
       #
       return True
    #
    # end of method

    # method: create_rttm
    #
    # arguments:
    #  fname: full pathname of the rttm file
    #  list: a list of filenames for the annotations
    #  tags: a list of unique tags
    #  map: a mapping used to collapse classes for scoring
    #
    # return:
    #  fdur: the duration of each annotations file in secs
    #
    # This method creates a NIST-formatted XML file known
    # as an rttm file. It returns the total duration, which is needed
    # at the top of the ECF file and for false alarm calculations.
    #
    def create_rttm(self, fname_a, list_a, tags_a, map_a):
        
        # initialize local variable
        #
        fdur = []
        counter = 0
        
        # open the file
        #
        fp = nft.make_fp(fname_a)
        
        # loop over the list
        #
        for fname in list_a:

            # generate the list of terms
            #
            events = self.create_terms(fname, map_a)
            if events == None:
                print "%s (%s: %s): error creating terms (%s)" % \
                (sys.argv[0], __name__, "create_rttm", fname_a)
                return None

            # loop over list files and write to the output file
            #
            base = os.path.splitext(tags_a[counter])[0]

            for i in range(len(events)):
                key = next(iter(events[i][2]))
                fp.write('LEXEME %s 1 %12.4f %12.4f %s lex <NA> <NA>\n' 
                         % (base, events[i][0], \
                            float(events[i][1]) - float(events[i][0]), key))

            # save duration of each file
            #
            fdur.append(float(events[-1][1]))
            counter += 1
        
        # close the file
        #
        fp.close()

        # exit gracefully
        #
        return fdur
    #
    # end of method
	
    # method: create_kwslist
    #
    # arguments:
    #  fname: full pathname of the kwslist file
    #  list: a list of filenames for the hypotheses
    #  tags: a list of unique tags
    #  map: a mapping used to collapse classes for scoring
    #  odir: output directory
    #
    # return: a logical value indicating the status
    #
    # This method creates a NIST-formatted XML file known as a kwslist file. 
    #
    def create_kwslist(self, fname_a, list_a, tags_a, map_a, odir_a):
        
        # declare local variables:
        #  tmp is used to accumulate per-term output
        #
        tmp = OrderedDict()
        
        # generate a permuted map to make lookups easy
        #
        pmap = nft.permute_map(map_a)

        # create a temporary file for each event
        #
        for key in map_a:

            # create a dictionary of tmp file names
            #
            tmp[key] = [] 
            tmp[key].append(str('  <detected_kwlist kwid="term-%s" '
                                'search_time="999.0" oov_count="0">' % key))
            
        # loop over filenames
        #
        counter = int(0)
        for fname in list_a:

            # generate a list of terms
            #
            events = self.create_terms(fname, pmap)
            if events == None:
                print "%s (%s: %s): error creating terms (%s)" % \
                (sys.argv[0], __name__, "create_kwslist", fname_a)
                return False

            # loop over the events and print them to the output file
            #
            base = os.path.splitext(tags_a[counter])[0]
            for i in range(len(events)):
                key = next(iter(events[i][2]))
                tmp[key].append(str('    <kw file="%s" channel="1" '
                                    'tbeg="%.4f" dur="%.4f" '
                                    'score="%.4f" decision="YES"/>'
                                    % (base,
                                       float(events[i][0]), \
                                       float(events[i][1]) - \
                                       float(events[i][0]),
                                       float(events[i][2][key]))))
            counter += 1 

        # open the kwslist file, write the data, and close the file
        #
        fp = nft.make_fp(fname_a)
        fp.write('<kwslist kwlist_filename="%s" language="english" '
                 'system_id="">\n\n' % self.fname_kwlist_d)
        for key in tmp:
            for content in tmp[key]:
               fp.write(content + '\n')
            fp.write('  </detected_kwlist>\n\n')   
        fp.write('</kwslist>')
        fp.close()

        # exit gracefully
        #
        return True
    #
    # end of method
        
    # method: create_terms
    #
    # arguments:
    #  fname: full pathname of the file
    #  pmap: a permuted map used to map events to scoring classes
    #
    # return:
    #  events: a data structure containing start/stop_times and events labels
    #
    # This method reads events from a file and maps them.
    #
    def create_terms(self, fname_a, pmap_a = None):
        
        # load the labels
        #
        ann = nat.Annotations()
        if ann.load(fname_a) == None:
            print "%s (%s: %s): error loading annotations (%s)" % \
                (sys.argv[0], __name__, "create_terms", fname_a)
            return None

        # get the events
        #
        events = ann.get()
        if events == None:
            print "%s (%s: %s): error getting annotations (%s)" % \
                (sys.argv[0], __name__, "create_terms", fname_a)
            return None

        # map the events
        #
        if pmap_a != None:
            events_new = []
            for i in range(len(events)):
                events_new.append(events[i])
                for key in events[i][2]:
                    events_new[i][2][pmap_a[key].lower()] = events[i][2][key]
            return events_new

        # else: exit gracefully
        #
        return events
    #
    # end of method         

    # method: create_ecf
    #
    # arguments:
    #  fname: full pathname of the ecf file
    #  list: a list of filenames for the annotations
    #  tags: a list of unique tags
    #  fdur: the duration of each file in secs
    #  total_dur: the total duration in secs of the annotations
    #
    # return: a logical value indicating the status
    #
    # This method creates a NIST-formatted XML file known
    # as an ECF file.
    #
    def create_ecf(self, fname_a, list_a, tags_a, fdur_a, total_dur_a):
       
        # open the file
        #
        fp = nft.make_fp(fname_a)

        # write total duration 
        #
        fp.write('<ecf source_signal_duration="%.4f" language="english" '
                 'version="">\n' %total_dur_a)

        # loops over all entries in the list
        #
        counter = 0
        for fname in list_a:
            fp.write('  <excerpt audio_filename="%s" channel="1" '
                     'tbeg="%.4f" dur="%.4f" source_type="bnews"/>\n'
                     % (tags_a[counter], float(0), float(fdur_a[counter])))
            counter += 1

        # clean up by writing the last line and closing the file
        #
        fp.write('</ecf>')
        fp.close()

        # exit gracefully
        #
        return True
    #
    # end of method

    # method: score
    #
    # arguments:
    #  odir: output directory
    #
    # return: a logical value indicating status
    #
    # This method sets up a command and runs NIST scoring.
    #
    def score(self, odir_a):

        # path to input files
        #
        fname_ecf = nft.make_fname(odir_a, self.fname_ecf_d)
        fname_kwlist = nft.make_fname(odir_a, self.fname_kwlist_d)
        fname_kwslist = nft.make_fname(odir_a, self.fname_kwslist_d)
        fname_rttm = nft.make_fname(odir_a, self.fname_rttm_d)
        fname_log = nft.make_fname(odir_a, self.fname_log_d)
        odir = nft.make_fname(odir_a, self.basename_d)

        # run KWSEval 
        #
        cmd = "KWSEval -e %s -r %s -t %s -s %s -S %s -p %s -k %s -K %s -o -b \
		-d -c -f %s" % (fname_ecf, fname_rttm, fname_kwlist, \
		fname_kwslist, self.delta_d, self.probterm_d, \
		self.koefcorrect_d, self.koefincorrect_d, odir)

        # create a shell file 
        #
        fname_cmd = nft.make_fname(odir_a, self.command_d)
        fp = nft.make_fp(fname_cmd)
        fp.write(cmd)
        fp.close()
        
        # run the command
        #
        rvalue = os.system("sh %s > %s" % (fname_cmd, fname_log))
        
        # exit gracefully
        #
        if rvalue >= 0:
            return True
        else:
            return False;
    #
    # end of method

    # method: get_results
    #
    # arguments:
    #  fname: path to the NIST "bsum" file
    #  map: the class scoring map
    #
    # return: a logical value indicating status
    # 
    # This method reads a NIST-formatted results file and extracts
    # the necessary scoring information that we use to display results.
    # The results are stored in class data.
    #
    def get_results(self, fname_a, map_a):
        
        # read the file into memory
        #
        lines = [line.rstrip(nft.DELIM_NEWLINE) for line in open(fname_a)]
        
        # loop over the contents and extract the necessary information
        #
        ind1 = ntt.first_substring(lines, 'Keyword')
        ind2 = ntt.first_substring(lines, 'Summary  Totals')
        
        for i in range(ind1, ind2):

            # split the line into parts
            #
            parts = (re.sub(r'\s+', '', lines[i])).split('|')
            
            # grab hits, misses, false alarms and twv since
            # these are reported directly in the NIST report
            #
            key = parts[1]
            if len(parts[2]) > 0:
                self.tgt_d[key] = int(parts[2])
                self.hit_d[key] = int(parts[3])
                self.mis_d[key] = int(parts[5])
                self.fal_d[key] = int(parts[4])
                self.twv_d[key] = float(parts[6])
            else:
                self.tgt_d[key] = int(0)
                self.hit_d[key] = int(0)
                self.mis_d[key] = int(0)
                self.fal_d[key] = int(0)
                self.twv_d[key] = float(0)

        # exit gracefully
        #
        return True
    #
    # end of method

    # method: compute_performance
    #
    # arguments: none
    #
    # return: a logical value indicating status
    #
    # This method computes a number of standard measures of performance. The
    # terminology follows these references closely:
    #
    #  https://en.wikipedia.org/wiki/Confusion_matrix
    #  https://en.wikipedia.org/wiki/Precision_and_recall
    #  http://www.dataschool.io/simple-guide-to-confusion-matrix-terminology/
    #
    # The approach taken here for a multi-class problem is to convert the
    # NxN matrix to a 2x2 for each label, and then do the necessary
    # computations.
    #
    # Note that NIST does not give us a confusion matrix (sub_d).
    #
    def compute_performance(self):

        # check for a zero count
        #
        num_total_ref_events = sum(self.tgt_d.values())
        if num_total_ref_events == 0:
            print "%s (%s: %s): number of events is zero (%d %d)" % \
                    (sys.argv[0], __name__, "compute_performance", \
                     num_total_ref_events)
            return None
        
        #----------------------------------------------------------------------
        # (1) The first block of parameters count events such as hits,
        #     missses and false alarms. The NIST algorithm provides
        #     these directly.
        #
        for key1 in self.hit_d:
            self.ins_d[key1] = self.fal_d[key1]
            self.del_d[key1] = self.mis_d[key1]

        #----------------------------------------------------------------------
        # (2) The second block of computations are the derived measures
        #     such as sensitivity. These are computed using a three-step
        #     approach:
        #      (2.2) compute true positives, etc. (tp, tn, fp, fn)
        #      (2.3) compute the derived measures (e.g., sensitivity)
        #
        # loop over all labels
        #
        for key1 in self.hit_d:

            #------------------------------------------------------------------
            # (2.2) The NIST algorithm outputs hits, misses and false alarms
            #       directly. These must be converted to (tp, tn, fp, fn).
            #
            # compute true positives (tp): copy hits
            #
            self.tp_d[key1] = self.hit_d[key1]

            # compute true negatives (tn):
            #  sum the hits that are not the current label
            #
            tn_sum = int(0)
            for key2 in self.hit_d:
                if key1 != key2:
                    tn_sum += self.hit_d[key2]
            self.tn_d[key1] = tn_sum

            # compute false positives (fp): copy false alarms
            #
            self.fp_d[key1] = self.fal_d[key1]

            # compute false negatives (fn): copy misses
            #
            self.fn_d[key1] = self.mis_d[key1]

            # check the health of the confusion matrix
            #
            tp = self.tp_d[key1]
            fp = self.fp_d[key1]
            tn = self.tn_d[key1]
            fn = self.fn_d[key1]
            tdur = self.total_dur_d

            if ((tp + fn) == 0) or ((fp + tn) == 0) or \
               ((tp + fp) == 0) or ((fn + tn) == 0):
                print "%s (%s: %s): " % \
                    (sys.argv[0], __name__, "compute_performance"), \
                    "divide by zero (warning) (%d %d %d %d)" % \
                    (tp, fp, tn, fn)
            elif (round(tdur, ntt.MAX_PRECISION) == 0):
                print "%s (%s: %s): duration is zero (warning) (%f)" % \
                    (sys.argv[0], __name__, "compute_performance", tdur)

            # (2.3) compute derived measures
            #
            if (tp + fn) != 0:
                self.tpr_d[key1] = float(self.tp_d[key1]) / float(tp + fn)
            else:
                self.tpr_d[key1] = float(0)

            if (tn + fp) != 0:
                self.tnr_d[key1] = float(self.tn_d[key1]) / float(tn + fp)
            else:
                self.tnr_d[key1] = float(0)

            if (tp + fp) != 0:
                self.ppv_d[key1] = float(self.tp_d[key1]) / float(tp + fp)
            else:
                self.ppv_d[key1] = float(0)

            if (tn + fn) != 0:
                self.npv_d[key1] = float(self.tn_d[key1]) / float(tn + fn)
            else:
                self.npv_d[key1] = float(0)

            self.fnr_d[key1] = 1 - float(self.tpr_d[key1])
            self.fpr_d[key1] = 1 - float(self.tnr_d[key1])
            self.fdr_d[key1] = 1 - float(self.ppv_d[key1])
            self.for_d[key1] = 1 - float(self.npv_d[key1])

            if (tp + tn + fp + fn) != 0:
                self.acc_d[key1] = float(self.tp_d[key1] + self.tn_d[key1]) / \
                                   (tp + tn + fp + fn)
                self.prv_d[key1] = float(self.tp_d[key1] + self.fn_d[key1]) / \
                                   (tp + tn + fp + fn)
            else:
                self.acc_d[key1] = float(0)
                self.prv_d[key1] = float(0)

            self.msr_d[key1] = 1 - self.acc_d[key1]

            # compute the f1 score:
            #  this has to be done after sensitivity and prec are computed
            #
            f1s_denom = float(self.ppv_d[key1] + self.tpr_d[key1])
            if round(f1s_denom, ntt.MAX_PRECISION) == 0:
                print "%s (%s: %s): f ratio divide by zero (warning) (%s)" % \
                    (sys.argv[0], __name__, "compute_performance", key1)
                self.f1s_d[key1] = float(0)
            else:
                self.f1s_d[key1] = 2.0 * self.ppv_d[key1] * \
                                    self.tpr_d[key1] / f1s_denom

            # compute the false alarm rate
            #
            if (round(tdur, ntt.MAX_PRECISION) == 0):
                print "%s (%s: %s): zero duration (warning) (%s)" % \
                    (sys.argv[0], __name__, "compute_performance", key1)
                self.flr_d[key1] = float(0)
            else:
                self.flr_d[key1] = float(fp) / tdur * (60 * 60 * 24)
        
        #----------------------------------------------------------------------
        # (3) the third block of parameters are the summary values
        #
        self.sum_tgt_d = sum(self.tgt_d.values())
        self.sum_hit_d = sum(self.hit_d.values())
        self.sum_mis_d = sum(self.mis_d.values())
        self.sum_fal_d = sum(self.fal_d.values())
        self.sum_ins_d = sum(self.ins_d.values())
        self.sum_del_d = sum(self.del_d.values())

        self.sum_tp_d = sum(self.tp_d.values())
        self.sum_tn_d = sum(self.tn_d.values())
        self.sum_fp_d = sum(self.fp_d.values())
        self.sum_fn_d = sum(self.fn_d.values())

        if (self.sum_tp_d + self.sum_fn_d) != 0:
            self.sum_tpr_d = float(self.sum_tp_d) / \
                             float(self.sum_tp_d + self.sum_fn_d)
        else:
            self.sum_tpr_d = float(0)

        if (self.sum_tn_d + self.sum_fp_d) != 0:
            self.sum_tnr_d = float(self.sum_tn_d) / \
                             float(self.sum_tn_d + self.sum_fp_d)
        else:
            self.sum_tnr_d = float(0)

        if (self.sum_tp_d + self.sum_fp_d) != 0:
            self.sum_ppv_d = float(self.sum_tp_d) / \
                             float(self.sum_tp_d + self.sum_fp_d)
        else:
            self.sum_ppv_d = float(0)

        if (self.sum_tn_d + self.sum_fn_d) != 0:
            self.sum_npv_d = float(self.sum_tn_d) / \
                             float(self.sum_tn_d + self.sum_fn_d)
        else:
            self.sum_npv_d = float(0)

        self.sum_fnr_d = 1 - float(self.sum_tpr_d)
        self.sum_fpr_d = 1 - float(self.sum_tnr_d)
        self.sum_fdr_d = 1 - float(self.sum_ppv_d)
        self.sum_for_d = 1 - float(self.sum_npv_d)

        if (self.sum_tp_d + self.sum_tn_d + \
            self.sum_fp_d + self.sum_fn_d) != 0:
            self.sum_acc_d = float(self.sum_tp_d + self.sum_tn_d) / \
                             (float(self.sum_tp_d + self.sum_tn_d + \
                                    self.sum_fp_d + self.sum_fn_d))
            self.sum_prv_d = float(self.sum_tp_d + self.sum_fn_d) / \
                             (float(self.sum_tp_d + self.sum_tn_d + \
                                    self.sum_fp_d + self.sum_fn_d))
        else:
            self.sum_acc_d = float(0)
            self.sum_prv_d = float(0)

        self.sum_msr_d = 1 - self.sum_acc_d

        # compute the f1 score
        #
        f1s_denom = self.sum_ppv_d + self.sum_tpr_d
        if round(f1s_denom, ntt.MAX_PRECISION) == 0:
            print "%s (%s: %s): f ratio divide by zero (warning) (%s)" % \
                (sys.argv[0], __name__, "compute_performance", "summary")
            self.sum_f1s_d = float(0)
        else:
            self.sum_f1s_d = 2.0 * self.sum_ppv_d * self.sum_tpr_d / f1s_denom

        # compute the false alarm rate
        #
        if round(self.total_dur_d, ntt.MAX_PRECISION) == 0:
            print "%s (%s: %s): zero duration (warning) (%s)" % \
                (sys.argv[0], __name__, "compute_performance", "summary")
            self.sum_flr_d = float(0)
        else:
            self.sum_flr_d = float(self.sum_fp_d) / self.total_dur_d * \
                             (60 * 60 * 24)

        # compute the summary TWV as the average
        #
        self.sum_twv_d = float(sum(self.twv_d.values())) / len(self.twv_d)

        # exit gracefully
        #
        return True
    #
    # end of method

    # method: display_results
    #
    # arguments:
    #  fp: output file pointer
    #
    # return: a logical value indicating status
    #
    # This method displays all the results in output report.
    #
    def display_results(self, fp_a):

        # write per label header
        #
        fp_a.write(("Per Label Results:\n").upper())
        fp_a.write("\n")

        # per label results: loop over all classes
        #
        for key in self.hit_d:
            fp_a.write((" Label: %s\n" % key).upper())
            fp_a.write("\n")

            fp_a.write("   %30s: %12.0f   <**\n" % \
                       ("Targets", float(self.tgt_d[key])))
            fp_a.write("   %30s: %12.0f   <**\n" % \
                       ("Hits", float(self.hit_d[key])))
            fp_a.write("   %30s: %12.0f   <**\n" % \
                       ("Misses", float(self.mis_d[key])))
            fp_a.write("   %30s: %12.0f   <**\n" % \
                       ("False Alarms", float(self.fal_d[key])))
            fp_a.write("   %30s: %12.0f\n" % \
                       ("Insertions", float(self.ins_d[key])))
            fp_a.write("   %30s: %12.0f\n" % \
                       ("Deletions", float(self.del_d[key])))
            fp_a.write("\n")

            fp_a.write("   %30s: %12.0f\n" % \
                       ("True Positives (TP)", float(self.tp_d[key])))
            fp_a.write("   %30s: %12.0f\n" % \
                       ("True Negatives (TN)", float(self.tn_d[key])))
            fp_a.write("   %30s: %12.0f\n" % \
                       ("False Positives (FP)", float(self.fp_d[key])))
            fp_a.write("   %30s: %12.0f\n" % \
                       ("False Negatives (FN)", float(self.fn_d[key])))
            fp_a.write("\n")

            fp_a.write("   %30s: %12.4f%%\n" % \
                       ("Sensitivity (TPR, Recall)", self.tpr_d[key] * 100.0))
            fp_a.write("   %30s: %12.4f%%\n" % \
                       ("Specificity (TNR)", self.tnr_d[key] * 100.0))
            fp_a.write("   %30s: %12.4f%%\n" % \
                       ("Precision (PPV)", self.ppv_d[key] * 100.0))
            fp_a.write("   %30s: %12.4f%%\n" % \
                       ("Negative Pred. Value (NPV)", self.npv_d[key] * 100.0))
            fp_a.write("   %30s: %12.4f%%\n" % \
                       ("Miss Rate (FNR)", self.fnr_d[key] * 100.0))
            fp_a.write("   %30s: %12.4f%%\n" % \
                       ("False Positive Rate (FPR)", self.fpr_d[key] * 100.0))
            fp_a.write("   %30s: %12.4f%%\n" % \
                       ("False Discovery Rate (FDR)", self.fdr_d[key] * 100.0))
            fp_a.write("   %30s: %12.4f%%\n" % \
                       ("False Omission Rate (FOR)", self.for_d[key] * 100.0))
            fp_a.write("   %30s: %12.4f%%\n" % \
                       ("Accuracy", self.acc_d[key] * 100.0))
            fp_a.write("   %30s: %12.4f%%\n" % \
                       ("Misclassification Rate", self.msr_d[key] * 100.0))
            fp_a.write("   %30s: %12.4f%%\n" % \
                       ("Prevalence", self.prv_d[key] * 100.0))
            fp_a.write("   %30s: %12.4f\n" % \
                       ("F1 Score (F Ratio)", self.f1s_d[key]))
            fp_a.write("   %30s: %12.4f per 24 hours\n" % \
                       ("False Alarm Rate", self.flr_d[key]))
            fp_a.write("   %30s: %12.4f   <**\n" % \
                       ("TWV", self.twv_d[key]))
            fp_a.write("\n")

        # display a summary of the results
        #
        fp_a.write(("Summary:\n").upper())
        fp_a.write("\n")

        # display the standard derived values
        #
        fp_a.write("   %30s: %12.0f\n" % \
                   ("Total", float(self.sum_tgt_d)))
        fp_a.write("   %30s: %12.0f\n" % \
                   ("Hits", float(self.sum_hit_d)))
        fp_a.write("   %30s: %12.0f\n" % \
                   ("Misses", float(self.sum_mis_d)))
        fp_a.write("   %30s: %12.0f\n" % \
                   ("False Alarms", float(self.sum_fal_d)))
        fp_a.write("   %30s: %12.0f\n" % \
                   ("Insertions", float(self.sum_ins_d)))
        fp_a.write("   %30s: %12.0f\n" % \
                   ("Deletions", float(self.sum_del_d)))
        fp_a.write("\n")

        fp_a.write("   %30s: %12.0f\n" % \
                   ("True Positives(TP)", float(self.sum_tp_d)))
        fp_a.write("   %30s: %12.0f\n" % \
                   ("False Positives (FP)", float(self.sum_fp_d)))
        fp_a.write("\n")

        fp_a.write("   %30s: %12.4f%%\n" % \
                   ("Sensitivity (TPR, Recall)", self.sum_tpr_d * 100.0))
        fp_a.write("   %30s: %12.4f%%\n" % \
                   ("Miss Rate (FNR)", self.sum_fnr_d * 100.0))
        fp_a.write("   %30s: %12.4f%%\n" % \
                   ("Accuracy", self.sum_acc_d * 100.0))
        fp_a.write("   %30s: %12.4f%%\n" % \
                   ("Misclassification Rate", self.sum_msr_d * 100.0))
        fp_a.write("   %30s: %12.4f%%\n" % \
                   ("Prevalence", self.sum_prv_d * 100.0))
        fp_a.write("   %30s: %12.4f\n" % \
                   ("F1 Score", self.sum_f1s_d))
        fp_a.write("\n")

        # display the overall false alarm rate
        #
        fp_a.write("   %30s: %12.4f secs\n" % \
                   ("Total Duration", self.total_dur_d))
        fp_a.write("   %30s: %12.4f events\n" % \
                   ("Total False Alarms", self.sum_fp_d))
        fp_a.write("   %30s: %12.4f per 24 hours\n" % \
                   ("Total False Alarm Rate", self.sum_flr_d))
        fp_a.write("\n")

        # display the actual twv
        #
        fp_a.write("   %30s: %12.4f   <**\n" % \
                   ("Average TWV", self.sum_twv_d))
        fp_a.write("\n")

        # exit gracefully
        #
        return True
    #
    # end of method

# end of file 
#

