#!/usr/bin/env python

# file: $NEDC_NFC/class/python/nedc_eval_tools/nedc_eval_taes.py
#
# revision history:
#  20170815 (JP): added another metric: prevalence
#  20170812 (JP): changed the divide by zero checks
#  20170716 (JP): upgraded to using the new annotation tools
#  20170710 (JP): refactored code
#  20170702 (JP): added summary scoring; revamped the derived metrics
#  20170625 (VS): initial version
#  20170627 (VS): second optimized version
#
# usage:
#  import nedc_eval_taes as ntaes
#
# This file implements NEDC's Time-Aligned Event scoring algorithm.
#------------------------------------------------------------------------------

# import required system modules
#
import os
import sys
from collections import OrderedDict

# import required NEDC modules
#
import nedc_file_tools as nft
import nedc_ann_tools as nat
import nedc_text_tools as ntt
import nedc_display_tools as ndt

#------------------------------------------------------------------------------
#
# define important constants
#
#------------------------------------------------------------------------------

# define paramter file constants
#
NEDC_TAES = "NEDC_TAES"

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
#  nedc_taes: the NEDC time-aligned scoring algorithm parameters
#  odir: the output directory
#  rfile: the results file (written in odir)
#  fp: a pointer to the output summary file
#
# return: a logical value indicating status
#
# This method runs the NEDC time-aligned scoring algorithm by:
#  (1) loading the annotations
#  (2) scoring them
#  (3) displaying the results
#
def run(reflist_a, hyplist_a, map_a, nedc_taes_a, odir_a, rfile_a, fp_a):

    # define local variables
    #
    status = True
    ntaes = NedcTAES(nedc_taes_a)

    # load the reference and hyp file lists into memory
    #
    num_files_ref = len(reflist_a)
    num_files_hyp = len(hyplist_a)

    if num_files_ref < 1 or num_files_hyp < 1 or \
       num_files_ref != num_files_hyp:
        print "%s (%s: %s): file list error (%s %s)" % \
            (sys.argv[0], __name__, "run", reflist_a, hyplist_a)
        return False

    # run time-aligned scoring
    #
    status = ntaes.init_score(map_a)
    status = ntaes.score(reflist_a, hyplist_a, map_a, rfile_a)
    if status == False:
        print "%s (%s: %s): error during scoring" % \
            (sys.argv[0], __name__, "run")
        return False

    # compute performance
    #
    cnf = ntaes.compute_performance()
    if status == None:
        print "%s (%s: %s): error computing performance" % \
            (sys.argv[0], __name__, "run")
        return False

    # collect information for scoring and display
    #
    status = ntaes.display_results(fp_a)
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

# class: NedcTAES
#
# This class contains methods that execute the time-aligned event-based 
# scoring algorithm. This approach computes fractional counts of matches,
# providing more resolution than the overlap method.
#
class NedcTAES():
    
    # method: constructor
    # 
    # arguments: none
    #
    # return: none
    #
    def __init__(self, params_a):

        # decode the parameters passed from the parameter file
        #

        # declare a variable to hold a permuted map
        #
        self.pmap_d = {}

        # declare a duration parameter used to calculate the false alarm rate:
        #  we need to know the total duration of the data in secs
        #
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

        # declare parameters to hold per file output
        #
        self.rfile_d = None

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
        
        # initialize global counters
        #
        self.total_dur_d = float(0)

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

        # permute the map: we need this in various places
        #
        self.pmap_d = nft.permute_map(map_a)

        # exit gracefully
        # 
        return True
    #
    # end of method

    # method: score
    #
    # arguments:
    #  files_ref: a reference file list
    #  files_hyp: a hypothesis file list
    #  map: a scoring map
    #  rfile: a file that contains per file scoring results
    #
    # return: a logical value indicating status
    #
    # This method computes a confusion matrix.
    #
    def score(self, files_ref_a, files_hyp_a, map_a, rfile_a):
        
        # declare local variables
        #
        status = True
        ann = nat.Annotations()

        # create the results file
        #
        self.rfile_d = nft.make_fp(rfile_a)

        # loop over all files
        #
        for i in range(len(files_ref_a)):

            # load the reference annotations
            #
            if ann.load(files_ref_a[i]) == False:
                print "%s (%s: %s): error loading annotation for file (%s)" % \
                    (sys.argv[0], __name__, "score", files_ref_a[i])
                return False

            # get the ref events
            #
            events_ref = ann.get()
            if events_ref == None:
                print "%s (%s: %s): error getting annotations (%s)" % \
                    (sys.argv[0], __name__, "score", files_ref_a[i])
                return False

            # load the hypothesis annotations
            #
            if ann.load(files_hyp_a[i]) == False:
                print "%s (%s: %s): error loading annotation for file (%s)" % \
                    (sys.argv[0], __name__, "score", files_hyp_a[i])
                return False

            # get the hyp events
            #
            events_hyp = ann.get()
            if events_hyp == None:
                print "%s (%s: %s): error getting annotations (%s)" % \
                    (sys.argv[0], __name__, "score", files_hyp_a[i])
                return False

            # pudate the total duration
            #
            self.total_dur_d += events_ref[-1][1]

            # map the annotations before scoring:
            #  only extract the first label and convert to a pure list
            #
            ann_ref = []
            for event in events_ref:
                key = next(iter(event[2]))
                ann_ref.append([event[0], event[1], \
                                self.pmap_d[key], event[2][key]])
                
            ann_hyp = []
            for event in events_hyp:
                key = next(iter(event[2]))
                ann_hyp.append([event[0], event[1], \
                                self.pmap_d[key], event[2][key]])

            # add this to the confusion matrix
            #
            refo, hypo, hit, mis, fal = self.compute(ann_ref, ann_hyp)
            if refo == None:
                print "%s (%s: %s): error computing confusion matrix (%s %s)" % \
                    (sys.argv[0], __name__, "score", \
                     files_ref_a[i], files_hyp_a[i])
                return False

            # output the files to the per file results file
            #
            self.rfile_d.write("%5d: %s\n" % (i, files_ref_a[i]))
            self.rfile_d.write("%5s  %s\n" % ("", files_hyp_a[i]))
            self.rfile_d.write("  Ref: %s\n" % ' '.join(refo))
            self.rfile_d.write("  Hyp: %s\n" % ' '.join(hypo))
            self.rfile_d.write("%6s (Hits: %.4f  Miss: %.4f  False Alarms: %.4f  Total: %.4f)\n" \
                               % ("", hit, mis, fal, \
                                  mis + fal))
            self.rfile_d.write("\n")

        # close the file
        #
        self.rfile_d.close()

        # exit gracefully
        # 
        return True
    #
    # end of method

    # method: compute
    #
    # arguments:
    #  ref: reference annotation
    #  hyp: hypothesis annotation
    #  
    # return:
    #  refo: the output aligned ref string
    #  hypo: the output aligned hyp string
    #  hit: the number of hits
    #  mis: the number of misses
    #  fal: the number of false alarms
    #
    # this method loops through reference and hypothesis annotations to 
    # collect partial and absolute hit, miss and false alarms.
    #
    def compute(self, ref_a, hyp_a):

        # check to make sure the annotations match:
        #  since these are floating point values for times, we
        #  do a simple sanity check to make sure the end times
        #  are close (within 1 microsecond)
        #
        if round(ref_a[-1][1], 3) != round(hyp_a[-1][1], 3):
            return False

        # prime the output strings with null characters
        #
        refo = []
        hypo = []
        prev_flag = False
        prev_fa = 0

        # initialize hmf variables to collect absolute and partial values
        #
        hit = float(0)
        mis = float(0)
        fal = float(0)

        # stop times are required to collect fa for overlapping events.
        # this dictionary contains a label and a stop time.
        #
        tstop_prev = dict()
        
        # generate flags for hypothesis and reference values to indicate
        # whether an event is used once or not (for detection)
        #
        hflags = []
        rflags = []
        for i in range(len(hyp_a)):
            hflags.append(True)
        for i in range(len(ref_a)):
            rflags.append(True)

        # loop over event in reference
        #
        for event in ref_a:
            self.tgt_d[event[2]] += 1            
            refo.append(event[2])
            
            # initialize the "previous stop time" dict
            # with none value
            #
            if event[2] not in tstop_prev:
                tstop_prev[event[2]] = None

            # collect hyp events which are in overlap with ref event
            #
            labels, starts, stops, flags, ind \
                = self.get_events(event[0], event[1], hyp_a, hflags)
###            import pdb;pdb.set_trace()
            # compute errors when an event in the reference matches
            # at least one label in the hypothesis
            #

            hit_partial = float(0)
            fa_partial = float(0)


            if event[2] in labels:

                # loop through all the event overlapped over a particular 
                # reference event and collect hit, miss, fa information
                # related to that class
                #
                
                ## define a buffer flag for overlapping events
                #

                for i in range(len(labels)):

                    # ignore all events which are not same as the ref label
                    #
                    if labels[i] == event[2]:
                        p_hit, p_miss, p_fa \
                            = self.compute_partial(float(event[0]),
                                                   float(event[1]),
                                                   float(starts[i]),
                                                   float(stops[i]),
                                                   flags[i],
                                                   tstop_prev[event[2]],
                                                   prev_fa)
                        
                        # accumulate hits per one ref events
                        # this will add up partial hits for situations such as
                        # ref: <----------------->
                        # hyp:   <-->  <-->   <----->
                        #

                        hit_partial += p_hit
                        fa_partial += p_fa
                        
                        ### editedV
                        # save the last fa value
                        #
                        prev_fa = p_fa
                        prev_flag = flags[i]

                        # hyp event is used now
                        #
                        hflags[ind[i]] = False

                if flags[i] == True:
                    mis_partial = (1.0 - hit_partial)
                else:
                    mis_partial = p_miss

                # update the HMF confusion matrix values
                #
                self.hit_d[event[2]] += hit_partial
                self.fal_d[event[2]] += fa_partial
                self.mis_d[event[2]] += mis_partial
                
                # collect info related to file
                #
                hit += hit_partial
                fal += fa_partial
                mis += mis_partial


            # detect absolute (no overlap) misses
            #
            else:
                self.mis_d[event[2]] += 1.0
                mis += 1.0

            # save previous stop times in a dictionary to calculate fa
            #
            tstop_prev[event[2]] = float(event[1])
            

        # loop over the hyp annotation to collect false alarms
        #
        for event in hyp_a:
            hypo.append(event[2])

            # get overlapping events from the reference
            #
            labels, starts, stops, garb1, garb2 \
                = self.get_events(event[0], event[1], ref_a, rflags)

            # detect absolute fas
            #
            if event[2] not in labels:
                self.fal_d[event[2]] += 1.0
                fal += 1.0

        # exit gracefully
        #
        return (refo, hypo, hit, mis, fal)
    #
    # end of method

    # method: compute_partial
    #
    # arguments:
    #  start_r: start time of ref event
    #  stop_r: stop time of ref event
    #  start_h: start time of hyp event
    #  stop_h: stop time of hyp event
    #  flag: flag that suggests that event has previously used
    #  tstop_prev: previous stop time of a recent class
    #
    # return:
    #  hit: calculated fractional number of hits
    #  miss: calculated fractional number of misses
    #  fa: calculated fractional number of false alarms
    #
    # This method calculates hits, misses and false alarms
    #  for detected hyp events by comparing it with duration
    #  of reference/hypothesis events and computing the amount
    #  of overlap between the two.
    #
    def compute_partial(self, start_r_a, stop_r_a, start_h_a, stop_h_a,
                        flag_a, tstop_prev_a, prev_fa_a):
###        import pdb;pdb.set_trace()
        # initialize local variables
        #
        ref_dur = stop_r_a - start_r_a
        hyp_dur = stop_h_a - start_h_a
        hit = float(0)
        fa = float(0)
        miss = float(0)

        #----------------------------------------------------------------------
        # deal explicitly with the four types of overlaps that can occur
        #----------------------------------------------------------------------

        # (1) for pre-prediction event
        #     ref:         <--------------------->
        #     hyp:   <---------------->
        #
        if start_h_a <= start_r_a and stop_h_a <= stop_r_a:
            hit = (stop_h_a - start_r_a) / ref_dur
            if ((start_r_a - start_h_a) / ref_dur) < 1.0:
                fa = ((start_r_a - start_h_a) / ref_dur)
            else:
                fa = ((start_r_a - start_h_a) / hyp_dur)

        # (2) for post-prediction event
        #     ref:         <--------------------->
        #     hyp:                  <-------------------->
        #
        elif start_h_a >= start_r_a and stop_h_a >= stop_r_a:

            # case 1: for single overlapping event
            #
            if flag_a:
                hit = (stop_r_a - start_h_a) / ref_dur                       
                if ((stop_h_a - stop_r_a) / ref_dur) < 1.0:
                    fa = ((stop_h_a - stop_r_a) / ref_dur)
                else:
                    fa = ((stop_h_a - stop_r_a) / hyp_dur)


            # case 2: for multiple overlapping events
            #  handle multiple ref events inside one long hyp event
            #  ref: <---------->    <----->   <------->
            #  hyp:        <----------------------------->
            #
            else:
                miss = 1.0
                curr_fa = abs((tstop_prev_a - start_r_a) / hyp_dur)  ### editedV
                if prev_fa_a + curr_fa >= 1.0:
                    fa = 1.0 - prev_fa_a
                else:
                    fa = curr_fa

        # (3) for over-prediction event
        #     ref:              <------->
        #     hyp:        <------------------->
        #
        elif start_h_a < start_r_a and stop_h_a > stop_r_a:
            
            # case 1: for single overlapping event
            #
            if flag_a:
                hit = 1.0
                fa = ((stop_h_a - stop_r_a) + (start_r_a - start_h_a)) /\
                     hyp_dur

            # case 2: for multiple overlapping events
            #  handle multiple ref events inside one long hyp event
            #  ref:          <----->   <--->  <---> <-->
            #  hyp:        <----------------------------->
            #
            else:
                miss = 1.0
                curr_fa = abs((tstop_prev_a - start_r_a) / hyp_dur)  ### editedV
                if prev_fa_a + curr_fa >= 1.0:
                    fa = 1.0 - prev_fa_a
                else:
                    fa = curr_fa
        
        # (4) for under-prediction event
        #     ref:        <--------------------->
        #     hyp:            <------>
        #
        else:
            hit = (stop_h_a - start_h_a) / ref_dur

        # exit gracefully
        #
        return (hit, miss, fa)
    #
    # end of method
        
    # method: get_events
    # 
    # arguments:
    #  start: start time
    #  stop: stop_time
    #  events: a list of events
    #  flags: event flags
    #
    # return:
    #  labels: the labels that overlap with the start and stop time
    #  starts: a list of start times
    #  stops: a list of stop times
    #  flags: flag corresponds to each event in labels
    #  ind: collected corresponding index in events_a
    #
    # this method returns a list of events that fall within a specified
    # range of time along with detection flag and correspondind index
    # of main event list (i.e. here events_a)
    #
    def get_events(self, start_a, stop_a, events_a, flags_a):

        # declare output variables
        #
        labels = []
        starts = []
        stops = []
        flags = []
        ind = []

        # loop over all events
        #
        for i in range(len(events_a)):

            # if the event overlaps partially with the interval,
            # it is a match. this means:
            #              start               stop
            #   |------------|<---------------->|-------------|
            #          |---------- event -----|
            #
            if (events_a[i][1] > start_a) and (events_a[i][0] < stop_a):
                starts.append(events_a[i][0])
                stops.append(events_a[i][1])
                labels.append(events_a[i][2])
                ind.append(i)
                flags.append(flags_a[i])

        # exit gracefully
        #
        return [labels, starts, stops, flags, ind]
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
        #     missses and false alarms. The overlap algorithm provides
        #     these directly.
        #
        for key1 in self.hit_d:
            self.ins_d[key1] = self.fal_d[key1]
            self.del_d[key1] = self.mis_d[key1]

        #----------------------------------------------------------------------
        # (2) The second block of computations are the derived measures
        #     such as sensitivity. These are computed using a two-step
        #     approach:
        #      (2.2) compute true positives, etc. (tp, tn, fp, fn)
        #      (2.3) compute the derived measures (e.g., sensitivity)
        #
        # loop over all labels
        #
        for key1 in self.hit_d:

            #------------------------------------------------------------------
            # (2.2) The overlap algorithm outputs hits, misses and false alarms
            #       directly. These must be converted to (tp, tn, fp, fn).
            #
            # compute true positives (tp)
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
###            import pdb;pdb.set_trace()
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

            ### editedV   ## fpr calculation looks incorrect for TAES scores...
            #
            self.fpr_d[key1] = float(self.fp_d[key1])
            
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
        ### editedV updated the floating point strings to 12.2 from 12.0
        #

        for key in self.hit_d:
            fp_a.write((" Label: %s\n" % key).upper())
            fp_a.write("\n")

            fp_a.write("   %30s: %12.2f   <**\n" % \
                       ("Targets", float(self.tgt_d[key])))
            fp_a.write("   %30s: %12.2f   <**\n" % \
                       ("Hits", float(self.hit_d[key])))
            fp_a.write("   %30s: %12.2f   <**\n" % \
                       ("Misses", float(self.mis_d[key])))
            fp_a.write("   %30s: %12.2f   <**\n" % \
                       ("False Alarms", float(self.fal_d[key])))
            fp_a.write("   %30s: %12.2f\n" % \
                       ("Insertions", float(self.ins_d[key])))
            fp_a.write("   %30s: %12.2f\n" % \
                       ("Deletions", float(self.del_d[key])))
            fp_a.write("\n")

            fp_a.write("   %30s: %12.2f\n" % \
                       ("True Positives (TP)", float(self.tp_d[key])))
            fp_a.write("   %30s: %12.2f\n" % \
                       ("True Negatives (TN)", float(self.tn_d[key])))
            fp_a.write("   %30s: %12.2f\n" % \
                       ("False Positives (FP)", float(self.fp_d[key])))
            fp_a.write("   %30s: %12.2f\n" % \
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
            fp_a.write("\n")

        # display a summary of the results
        #
        fp_a.write(("Summary:\n").upper())
        fp_a.write("\n")

        # display the standard derived values
        #
        fp_a.write("   %30s: %12.0f   <**\n" % \
                   ("Total", float(self.sum_tgt_d)))
        fp_a.write("   %30s: %12.0f   <**\n" % \
                   ("Hits", float(self.sum_hit_d)))
        fp_a.write("   %30s: %12.0f   <**\n" % \
                   ("Misses", float(self.sum_mis_d)))
        fp_a.write("   %30s: %12.0f   <**\n" % \
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

        # exit gracefully
        #
        return True
    #
    # end of method

# end of file
#
