import sys
import re

"""
examples:
$ python check_rec.py rec_file_no_errors.rec
No errors in  rec_file_no_errors.rec

$ python check_rec.py rec_file_with_errors.rec
error in line 53
error in line 204
"""

line_count = 0
errors_found = False

with open(sys.argv[1]) as rec_file:
    for line in rec_file:
        line_count += 1
        line_no_white_space = re.sub(r"\s", "", line)
        segments = line_no_white_space.split(",")

        have_all_fields_test = (len(segments) is 4)
        if have_all_fields_test:
            all_fields_meaningful_test = (segments[0] != "" and
                                          segments[1] != "" and
                                          segments[2] != "" and
                                          segments[3] != "")

        if not (have_all_fields_test and all_fields_meaningful_test):
            errors_found = True
            print "error in line", line_count

    if errors_found is False:
        print "No errors in", sys.argv[1]
