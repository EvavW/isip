#!/usr/bin/env python

# file: $NEDC_NFC/class/python/nedc_eval_tools/nedc_eval_ira.py
#
# revision history:
#  20170815 (JP): added another metric: prevalence
#  20170812 (JP): changed the divide by zero checks
#  20170716 (JP): upgraded to using the new annotation tools
#  20170702 (JP): added summary scoring; revamped the derived metrics
#  20170625 (JP): rewrote it based on our new specs
#
# usage:
#  import nedc_eval_ira as nira
#
# This file implements NEDC's inter-rater agreement scoring algorithm. This
# code essentially runs epoch-based scoring at a fine time resolution,
# and then evaluates the resulting confusion matrix using the Kappa
# statistic.
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
NEDC_IRA = "NEDC_IRA"

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
#  nedc_ira: the NEDC IRA scoring algorithm parameters
#  odir: the output directory
#  fp: a pointer to the output summary file
#
# return: a logical value indicating status
#
# This method runs the NEDC IRA scoring algorithm by:
#  (1) loading the annotations
#  (2) scoring them using an epoch-based approach
#  (3) evaluating the resulting confusion matrix
#  (4) displaying the results
#
def run(reflist_a, hyplist_a, map_a, nedc_ira_a, odir_a, fp_a):

    # define local variables
    #
    status = True
    nira = NedcIra(nedc_ira_a)

    # load the reference and hyp file lists into memory
    #
    num_files_ref = len(reflist_a)
    num_files_hyp = len(hyplist_a)

    if num_files_ref < 1 or num_files_hyp < 1 or \
       num_files_ref != num_files_hyp:
        print "%s (%s: %s): file list error (%s %s)" % \
            (sys.argv[0], __name__, "run", reflist_a, hyplist_a)
        return False

    # run ira scoring
    #
    status = nira.init_score(map_a)
    status = nira.score(reflist_a, hyplist_a, map_a)
    if status == False:
        print "%s (%s: %s): error during scoring" % \
            (sys.argv[0], __name__, "run")
        return False

    # compute agreement
    #
    cnf = nira.compute_agreement()
    if status == False:
        print "%s (%s: %s): error computing agreement" % \
            (sys.argv[0], __name__, "run")
        return False

    # collect information for scoring and display
    #
    header, tbl = ndt.create_table(cnf)
    status = nira.display_results("NEDC IRA Confusion Matrix",
                                  header, tbl, fp_a)
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

# class: NedcIra
#
# This class contains methods that execute the ira-based scoring algorithm.
#
class NedcIra():
    
    # method: constructor
    # 
    # arguments: none
    #
    # return: none
    #
    def __init__(self, params_a):

        # decode the parameters passed from the parameter file
        #
        self.epoch_dur_d = float(params_a['epoch_duration'])

        # declare a variable to hold a permuted map
        #
        self.pmap_d = {}

        # declare a duration parameter used to calculate the false alarm rate:
        #  we need to know the total duration of the data in secs
        #
        self.total_dur_d = float(0)

        # declare parameters to compute agreeement
        #
        self.sub_d = {}

        # additional derived data:
        #  we use class data to store a number of statistical measures
        #
        self.kappa_d = {}
        self.mkappa_d = float(0)

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

        # initialiaze parameters to compute agreement
        #  these are declared as ordered dictionaries organized
        #  in the order of the scoring map
        #
        self.sub_d = OrderedDict()
        self.kappa_d = OrderedDict()
        self.mkappa_d = float(0)

        # establish the order of these dictionaries in terms of
        # the scoring map.
        #
        for key in map_a:
            self.sub_d[key] = OrderedDict()
            for key2 in map_a:
                self.sub_d[key][key2] = int(0)

            self.kappa_d[key] = float(0)

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
    #
    # return: a logical value indicating status
    #
    # This method computes a confusion matrix.
    #
    def score(self, files_ref_a, files_hyp_a, map_a):
        
        # declare local variables
        #
        status = True
        ann = nat.Annotations()

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

            # update the total duration
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
            status = self.compute(ann_ref, ann_hyp, self.epoch_dur_d)
            if status == False:
                print "%s (%s: %s): error computing confusion matrix (%s %s)" % \
                    (sys.argv[0], __name__, "score", \
                     files_ref_a[i], files_hyp_a[i])
                return False

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
    #  dur: the duration of time used to sample the annotations
    #  
    # return:
    #  refo: the output aligned ref string
    #  hypo: the output aligned hyp string
    #
    #
    # this method iterates over the reference annotation, sampling it at
    # times spaced by dur secs, and compares labels to the corresponding
    # label in the hypothesis.
    #
    def compute(self, ref_a, hyp_a, dur_a):

        # check to make sure the annotations match:
        #  since these are floating point values for times, we
        #  do a simple sanity check to make sure the end times
        #  are close (within 1 microsecond)
        #
        if round(ref_a[-1][1], 3) != round(hyp_a[-1][1], 3):
            return False

        # loop over the reference annotation starting at the middle
        # of the first interval.
        #
        dur_by_2 = dur_a / float(2.0)
        curr_time = dur_a / float(2.0)
        start_time = float(0)
        stop_time = ref_a[-1][1]
        i = 0

        while curr_time <= stop_time:

            # convert time to an index
            #
            j = self.time_to_index(curr_time, ref_a)
            k = self.time_to_index(curr_time, hyp_a)

            # increment the substitution matrix
            #
            self.sub_d[ref_a[j][2]][hyp_a[k][2]] += int(1)

            # increment time:
            #  do this using an integer counter to avoid roundoff error
            #
            i += 1
            curr_time = dur_by_2 + i * dur_a

        # exit gracefully
        #
        return True
    #
    # end of method

    # method: time_to_index
    #
    # arguments:
    #  val: a floating point value of time in secs
    #  ann: a list of annotation events
    #
    # return: an integer index
    #
    # This method finds the annotation corresponding to a value of time.
    #
    def time_to_index(self, val_a, ann_a):

        # loop over the annotation
        #
        counter = 0
        for entry in ann_a:
            if (val_a >= entry[0]) & (val_a <= entry[1]):
                return counter
            else:
                counter += 1

        # exit ungracefully:
        #  no match was found, which is a problem
        #
        return int(-1)
    #
    # end of method

    # method: compute_agreement
    #
    # arguments: none
    #
    # return:
    #  cnf: a confusion matrix
    #
    # This method computes Cohen's Kappa statistic for the confusion matrix.
    # It iterates over each label and computes the label against all other
    # classes. This is a classic Kappa statistic calculation described here:
    #
    #  https://en.wikipedia.org/wiki/Cohen%27s_kappa#Example
    #
    # Other relevant references include:
    #
    #  https://en.wikipedia.org/wiki/Confusion_matrix
    #  https://en.wikipedia.org/wiki/Precision_and_recall
    #  http://www.dataschool.io/simple-guide-to-confusion-matrix-terminology/
    #
    # Then it computes a Kappa statistic for the entire matrix following the
    # procedure described here:
    #
    #  https://www.harrisgeospatial.com/docs/CalculatingConfusionMatrices.html
    #
    def compute_agreement(self):

        # loop over all labels:
        #  note that the confusion matrix is square by definition,
        #  so loop counters can be interchanged.
        #
        for label in self.sub_d:

            # compute the elements of the "yes/no" matrix
            #
            a = float(self.sub_d[label][label])
            b = float(0)
            c = float(0)
            d = float(0)
            for label2 in self.sub_d[label]:
                if label != label2:
                    b += float(self.sub_d[label][label2])
                    c += float(self.sub_d[label2][label])
                    d += float(self.sub_d[label2][label2])

            # compute the intermediate probabilities
            #
            denom = a + b + c + d
            if denom == float(0):
                print "%s (%s: %s): error computing intermediate probabilities (%s)" % \
                    (sys.argv[0], __name__, "compute_agreement", label)
                p_o = float(0)
                p_yes = float(0)
                p_no = float(0)
                p_e = float(0)
            else:
                p_o   = (a + d) / (a + b + c + d)
                p_yes = (a + b) / (a + b + c + d) * (a + c) / (a + b + c + d)
                p_no  = (c + d) / (a + b + c + d) * (b + d) / (a + b + c + d)
                p_e   = p_yes + p_no

            # compute the final statistic
            #
            num = float(p_o - p_e)
            denom = float(1) - p_e
            if (denom == float(0)) and (num != float(0)):
                print "%s (%s: %s): error computing kappa statistic (%s)" % \
                    (sys.argv[0], __name__, "compute_agreement", label)
                self.kappa_d[label] = 0
            elif denom == float(0):
                self.kappa_d[label] = float(1.0)
            else:
                self.kappa_d[label] = float((p_o - p_e) / (1 - p_e))

        # compute a Kappa statistic over the entire matrix:
        #  (1) compute the sum of the rows and columns
        #  (2) sum of the diagonal
        #  (3) sum of the matrix
        #  (4) sum of the product of the rows and colums sums
        #
        sum_rows = OrderedDict()
        for label1 in self.sub_d:
            sum_rows[label1] = int(0)
        sum_cols = OrderedDict()
        flbl = next(iter(self.sub_d))
        for label1 in self.sub_d[flbl]:
            sum_cols[label1] = int(0)

        sum_M = int(0)
        for label1 in self.sub_d:
            sum_M += self.sub_d[label1][label1]
            for label2 in self.sub_d[label1]:
                sum_rows[label1] += self.sub_d[label1][label2]
                sum_cols[label2] += self.sub_d[label1][label2]

        sum_N = int(0)
        sum_gc = int(0)
        for label1 in self.sub_d:
            sum_N += sum_rows[label1]
            sum_gc += sum_rows[label1] * sum_cols[label1]

        # (5) compute multi-class Kappa statistic
        #
        num = sum_N * sum_M - sum_gc
        denom = sum_N * sum_N - sum_gc
        if (denom == int(0)) and (num == int(0)):
            self.mkappa_d = float(1)
        elif denom == int(0):
            print "%s (%s: %s): error computing the multi-class kappa statistic (%f %f)" % \
                (sys.argv[0], __name__, "compute_agreement", label, \
                 num, denom)
            self.mkappa_d = 0
        else:
            self.mkappa_d = float(num) / float(denom)

        # exit gracefully
        #
        return self.sub_d
    #
    # end of method

    # method: display_results
    #
    # arguments:
    #  title: the title of the confusion table
    #  headers: the headers associated with the columns of the matrix
    #  tbl: the table to be printed
    #  fp: output file pointer
    #
    # return: a logical value indicating status
    #
    # This method displays all the results in output report.
    #
    def display_results(self, title_a, headers_a, tbl_a, fp_a):

        # declare a format length:
        #  we use this variable to make sure the output lines up.
        #  it is the length of the fixed portion of the per label
        #  output format ("Label: " + "   " + "Kappa" = 15 characters
        #
        fmt_len = int(15)

        # print complete table in output file
        #
        ndt.print_table(title_a, headers_a, tbl_a,
                                "%10s", "%12.2f", "%6.2f", fp_a)
        fp_a.write("\n")

        # write per label header
        #
        fp_a.write(("Per Label Results:\n").upper())

        # per label results: loop over all classes
        #
        max_lab_len = int(max(map(len, self.kappa_d)))
        for key in self.kappa_d:
            fp_a.write(" Label: %*s   Kappa: %12.4f\n" % \
                       (max_lab_len, key, self.kappa_d[key]))
        fp_a.write("\n")

        # write the multi-class Kappa statistic
        #
        tot_len = max_lab_len + fmt_len
        fp_a.write(("Summary:\n").upper())
        fp_a.write(" %*s: %12.4f\n" % \
                   (tot_len, "Multi-Class Kappa", self.mkappa_d))
        fp_a.write("\n")

        # exit gracefully
        #
        return True
    #
    # end of method

# end of file
#
