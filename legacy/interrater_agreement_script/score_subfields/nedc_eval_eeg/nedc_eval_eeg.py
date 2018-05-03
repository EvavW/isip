#!/usr/bin/env python
#
# file: $(NEDC_NFC)/util/python/nedc_eval_eeg/nedc_eval_eeg.py
#
# revision history:
#  20170730 (JP): moved parameter file constants out of this driver
#  20170728 (JP): added error checking for duration
#  20170716 (JP): upgraded to using the new annotation tools.
#  20170527 (JP): added epoch-based scoring
#  20150520 (SZ): modularized the code
#  20170510 (VS): encapsulated the three scoring metrics 
#  20161230 (SL): revision for standards
#  20150619 (SZ): initial version
# 
# usage:
#   nedc_eval_eeg -odir output -parameters parameters ref.list hyp.list
#
# options:
#  -parameters: a parameter file 
#  -odir: the output directory [$PWD/output]
#  -help: display this help message
#
# arguments:
#  ref.list: a list of reference annotations
#  hyp.list: a list of hypothesis 
#
# This script implements several standard scoring algorithms:
#  (1) NIST F4DE: uses NIST-standard keyword search scoring;
#  (2) DP Align: a dynamic programming-based alignment
#  (3) Epoch-based: measures the time-aligned similarity of two annotations;
#  (4) Overlap: implements a measure popular in bioengineering
#  (5) NEDC Time-Aligned Event Scoring: compares time-aligned events.
#  (6) NEDC Inter-rater Agreement Scoring: computes kappa statistics.
#------------------------------------------------------------------------------

# import system modules
#
import os
import re
import sys
import time

# import NEDC support modules
#
import nedc_cmdl_parser as ncp
import nedc_file_tools as nft
import nedc_ann_tools as nat

# import NEDC scoring modules
#
import nedc_eval_nist as nnist
import nedc_eval_dpalign as ndpalign
import nedc_eval_epoch as nepoch
import nedc_eval_ovlp as novlp
import nedc_eval_taes as ntaes
import nedc_eval_ira as nira

#------------------------------------------------------------------------------
#
# global variables are listed here
#
#------------------------------------------------------------------------------

# determine the location of the source code
#
NEDC_NFC = os.environ.get("NEDC_NFC")

# define the help file and usage message
#
HELP_FILE = NEDC_NFC + "/util/python/nedc_eval_eeg/nedc_eval_eeg.help"
USAGE_FILE = NEDC_NFC + "/util/python/nedc_eval_eeg/nedc_eval_eeg.usage"

# define default values for arguments
#
DEF_PFILE = os.environ.get("PWD") + "/nedc_eval_eeg/params.txt"
DEF_ODIR = os.environ.get("PWD") + "/output"

# define the required number of arguments
#
NUM_ARGS = 2

# define the names of the output files
#
NEDC_SUMMARY_FILE = "summary.txt"
NEDC_NIST_FILE = "summary_nist.txt"
NEDC_DPALIGN_FILE = "summary_dpalign.txt"
NEDC_EPOCH_FILE = "summary_epoch.txt"
NEDC_OVLP_FILE = "summary_ovlp.txt"
NEDC_TAES_FILE = "summary_taes.txt"
NEDC_IRA_FILE = "summary_ira.txt"

# define formatting constants
#
NEDC_EVAL_SEP = "=" * 78
NEDC_VERSION = "NEDC Eval EEG (v3.3.0)"

# define paramter file constants
#
NEDC_MAP = "MAP"

#------------------------------------------------------------------------------
#
# the main program starts here
#
#------------------------------------------------------------------------------
# method: main
#
# arguments: none
#
# return: none
#
# This function is the main program.
#
def _eval(reflist, hyplist, odir):

    # declare local variables
    #
    status = True

    # declare default values for command line arguments
    #
    pfile = DEF_PFILE
###    odir = DEF_ODIR

    # set the result file
    #
###    odir = DEF_ODIR

    # set the parameter file
    #
    pfile = DEF_PFILE

    # load the file lists
    #
###    reflist = nft.get_flist(reflist)
###    hyplist = nft.get_flist(hyplist)

    # check for mismatched file lists:
    #  note that we do this here so it is done only once, rather than
    #  in each scoring method
    #
    if (reflist == None) or (hyplist == None):
        print  "%s (%s: %s): error loading filelists"\
            % (sys.argv[0], __name__, "main")
        exit (-1)
    elif len(reflist) != len(hyplist):
        print  "%s (%s: %s): (ref: %d) and (hyp: %d) have different lengths" \
            % (sys.argv[0], __name__, "main", len(reflist), len(hyplist))
        exit (-1)
    elif nat.compare_durations(reflist, hyplist) == False:
        print  "%s (%s: %s): ref/hyplists do not have matching durations" \
            % (sys.argv[0], __name__, "main")
        exit (-1)

    # load the scoring map
    #
    tmpmap = nft.load_parameters(pfile, NEDC_MAP)
    if (tmpmap == None):
        print  "%s (%s: %s): error loading the scoring map (%s)" % \
            (sys.argv[0], __name__, "main", pfile)
        exit (-1)

    # convert the map
    #
    scmap = nft.generate_map(tmpmap)
    if (scmap == None):
        print  "%s (%s: %s): error converting the map" % \
            (sys.argv[0], __name__, "main")
        print tmpmap
        exit (-1)

    # create the output directory and the output summary file
    #               
    print " ... creating the output directory ..."
    if nft.make_dir(odir) == False:
        print  "%s (%s: %s): error creating output directory (%s)" \
            % (sys.argv[0], __name__, "main", odir)
        exit (-1)

    fname = nft.make_fname(odir, NEDC_SUMMARY_FILE)
    fp = nft.make_fp(fname)

    # print the header of the summary file showing the relevant information
    #
    fp.write("%s\n%s\n\n" % (NEDC_EVAL_SEP, NEDC_VERSION))
    fp.write(" File: %s\n" % fname) 
    fp.write(" Date: %s\n\n" % time.strftime("%c"))
    fp.write(" Parameter File: %s\n\n" % pfile)
    fp.write(" Data:\n")
    fp.write("  Ref: %s\n" % reflist)
    fp.write("  Hyp: %s\n\n" % hyplist)

    # execute NIST scoring
    #    
    print " ... executing NIST ATWV scoring ..."
    fp.write("%s\n%s\n\n" % \
             (NEDC_EVAL_SEP, \
              ("NIST ATWV Scoring Summary (f4de_3.3.1):").upper()))
    nist_f4de = nft.load_parameters(pfile, nnist.NIST_F4DE)
    status = nnist.run(reflist, hyplist, scmap, nist_f4de,
                       odir, NEDC_NIST_FILE, fp)
    if status == False:
        print  "%s (%s: %s): error in NIST scoring" % \
            (sys.argv[0], __name__, "main")
        exit (-1)    

    # execute dp alignment scoring
    #
    print " ... executing NEDC DP Alignment scoring ..."
    fp.write("%s\n%s\n\n" % \
             (NEDC_EVAL_SEP, \
              ("NEDC DP Alignment Scoring Summary (v2.0.0):").upper()))
    fname = nft.make_fname(odir, NEDC_DPALIGN_FILE)
    nedc_dpalign = nft.load_parameters(pfile, ndpalign.NEDC_DPALIGN)
    status = ndpalign.run(reflist, hyplist, scmap, nedc_dpalign,
                          odir, fname, fp)
    if status == False:
        print  "%s (%s: %s): error in DP Alignment scoring" % \
            (sys.argv[0], __name__, "main")
        exit (-1)
    
    # execute NEDC epoch-based scoring
    #
    print " ... executing NEDC Epoch scoring ..."
    fp.write("%s\n%s\n\n" % (NEDC_EVAL_SEP, \
                             "NEDC Epoch Scoring Summary (v2.0.0):"))
    fname = nft.make_fname(odir, NEDC_EPOCH_FILE)
    nedc_epoch = nft.load_parameters(pfile, nepoch.NEDC_EPOCH)
    status = nepoch.run(reflist, hyplist, scmap, nedc_epoch,
                        odir, fname, fp)
    if status == False:
        print  "%s (%s: %s): error in EPOCH scoring" % \
            (sys.argv[0], __name__, "main")
        exit (-1)
    
    # execute overlap scoring
    #
    print " ... executing NEDC Overlap scoring ..."
    fp.write("%s\n%s\n\n" % (NEDC_EVAL_SEP, \
                             "NEDC Overlap Scoring Summary (v2.0.0):"))
    fname = nft.make_fname(odir, NEDC_OVLP_FILE)
    nedc_ovlp = nft.load_parameters(pfile, novlp.NEDC_OVLP)
    status = novlp.run(reflist, hyplist, scmap, nedc_ovlp,
                       odir, fname, fp)
    if status == False:
        print  "%s (%s: %s): error in OVERLAP scoring" % \
            (sys.argv[0], __name__, "main")
        exit (-1)
    
    # execute time-aligned event scoring
    #
    print " ... executing NEDC Time-Aligned Event scoring ..."
    fp.write("%s\n%s\n\n" % (NEDC_EVAL_SEP, \
                             "NEDC TAES Scoring Summary (v2.0.0):"))
    fname = nft.make_fname(odir, NEDC_TAES_FILE)
    nedc_taes = nft.load_parameters(pfile, ntaes.NEDC_TAES)
    status = ntaes.run(reflist, hyplist, scmap, nedc_taes,
                       odir, fname, fp)
    if status == False:
        print  "%s (%s: %s): error in TIME-ALIGNED Event scoring" % \
            (sys.argv[0], __name__, "main")
        exit (-1)

    print " ... executing NEDC IRA scoring ..."
    fp.write("%s\n%s\n\n" % (NEDC_EVAL_SEP, \
                             "NEDC Inter-Rater Agreement Summary (v2.0.0):"))
    nedc_ira = nft.load_parameters(pfile, nira.NEDC_IRA)
    status = nira.run(reflist, hyplist, scmap, nedc_ira, odir, fp)
    if status == False:
        print  "%s (%s: %s): error in IRA scoring" % \
            (sys.argv[0], __name__, "main")
        exit (-1)

    # print the final message to the summary file, close it and exit
    #
    print " ... done ..."
    fp.write("%s\nNEDC EEG Eval Successfully Completed on %s\n%s\n" \
             % (NEDC_EVAL_SEP, time.strftime("%c"), NEDC_EVAL_SEP))
    
    # close the output file
    #
    fp.close()

    # end of main
    #
    
#
# end of main

