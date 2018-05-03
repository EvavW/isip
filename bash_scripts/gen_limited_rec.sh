#!/bin/bash

#this script removes all annotations that do no describe seizures that are
#60 seconds or longer (this can be changed below!)

#usage:

# bash gen_limited_rec.sh rec.list lower label
# e.g. bash gen_limited_rec.sh eval_rec.list 10 8 
# will overwrite files so that they only contain seizure events that are equal
# to or above 10 seconds and have an fnsz(8) label. 
# default lower = 60
# default label = 7

filelist=$1
lower=$2 #lower limit for the duration of seizures that you want to keep
label=$3 #annotation label for the events that you want to keep

cat $filelist | while read file ;

do

#send bash variables to awk
#if no label is given, make it 7
#if no lower limit is given, make it 60 seconds
#if annotation is above lower limit and matches label; print to temp file
#overwrite input file with temp file content
cat $file | awk -v lower="$lower" -v label="$label"                             'BEGIN {FS=","}                                                                 {if (length(label) == 0) label=7}                                              {if (length(lower) == 0) lower=60}                                             {if (($4 == label) && ($3-$2 >=lower)) print $1","$2","$3","$4 }' >$temp.txt

mv $temp.txt $file
#can be changed to output to a new file rather than overwrite the old
  #>$file.limited

done

