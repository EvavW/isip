#!/bin/env python


import os, sys
import numpy as np
import math
import argparse
import logging
import re
import subprocess
import threading

import score_subfields_cls as ssc

import nedc_eval_eeg.nedc_eval_eeg as eval_eeg


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def send_email(message, subject, email_id):

    try:
        subprocess.Popen(
            'echo "{message}" | mail -s "{subject}" {email}'.format(
                message = message,
                subject = subject,
                email = email_id), shell = True)
    except Exception as e:
        logger.info("Unable to send mail due to error:\n {error}".format(
            error = str(e)))
        pass


def main():
    print os.environ.get("PWD") + r"/" + sys.argv[0]
    print "beginning the scoring"
    
    ## This arguments should be collected from the configuration file.
    #
    funcname = eval_eeg._eval
    args = ["/data/isip/exp/tuh_eeg/exp_2148/agg.list", "/data/isip/exp/tuh_eeg/exp_2148/gold_stand.list"]

    ## define a score function object
    #
    score_f = ssc.score_fields(funcname, sep_fields = True, autosort = True)
    
    ## pass all the arguments
    score_f(args[0], args[1])










if __name__ == "__main__":main()
