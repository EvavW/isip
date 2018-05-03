#!/usr/bin/sh

## usage: bash teseiz_info.sh flist(rect.list)
#

## collect the first argument after script name
#
flist=$1

## read through all the lines in file (presumably rect) list
#
while read line; do

 echo $line # print each line which are filenames
 
 ## loop through all class number of seizure (7 to 18)
 #
 for lab_id in {7..18}; do

  ## look for label id following by end of line character ($)
  #
  cmd=`grep ",$lab_id$" $line | wc -l`

  ## ignore zero collected events
  #
  if [ $cmd != 0 ] 
  then
   ## divide total collected channel based events by 22 to get actual events per file
   #
   term_events=`expr $cmd / 22`
   echo There are $term_events number of events/terms with class id $lab_id # print class no. with collected no. of events
  fi

 done

done <$flist # feed in the filelist from here...
 
