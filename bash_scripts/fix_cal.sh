#!/usr/bin/sh

## usage: bash annotate_calibration.list flist(edf.list)
#

## collect the first argument after script name
#
flist=$1

## read through all the lines in file (presumably rect) list
#
while read line; do

echo $line
    
 sample_freq=`nedc_print_header $line | grep hdr_sample_frequency  | awk '{print substr($3, 1, length($3)-2)}'`
 duration=`nedc_print_duration $line | grep secs | awk '{print substr($3, 1, length($3)-3)}'` 
 ch0=0
 ch1=0
 start=0
 end_cal=-1
 rec_file=`echo $line | awk '{print substr($1, 1, length($1)-3)"rec" }'`
 end_cal=` cat $rec_file | awk 'BEGIN {FS=","}{print int($3)}'`
 start=$((end_cal*$((sample_freq))))
   while [[ $ch0 == $ch1 && $end_cal != $duration ]];do
    
    ch0=`nedc_print_signal -chan 0 -start $start -num 1 $line | tail -n 1 | awk '{print substr($4, 1, length($4)-1)}'`

    ch1=`nedc_print_signal -chan 1 -start $start -num 1 $line | tail  -n 1  | awk '{print substr($4, 1, length($4)-1)}'`

    start=$((start+=1))
    end_cal=`echo "scale=4; ($start/$sample_freq)" | bc -l`

   done
      echo "0,0.0000,$end_cal,30" >$rec_file

done <$flist # feed in the filelist from here...
