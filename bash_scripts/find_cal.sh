#!/usr/bin/sh

## usage: bash annotate_calibration.list flist(edf.list)
#

## collect the first argument after script name
#
flist=$1

## read through all the lines in file list. Should be edf files.
#
while read line; do
    start=$2 #start second not sample

    # if start second is not specified, initialize to 0
    if [ -z "$start" ]; then
	start=0
    fi
    # get sampling frequency from print header   
    sample_freq=`nedc_print_header $line | grep hdr_sample_frequency  | awk '{print substr($3, 1, length($3)-2)}'`
    start=$((start*$((sample_freq))))
    # get duration of recording from print duration
    duration=`nedc_print_duration $line | grep secs | awk '{print substr($3, 1, length($3)-3)}'` 
    num=$((duration*$((sample_freq))))
    
    ch0_array=(`nedc_print_signal -chan 18 -start 0 -num $num $line | awk '{print substr($4, 1, length($4)-1)}'`)
    ch1_array=(`nedc_print_signal -chan 19 -start 0 -num $num $line | awk '{print substr($4, 1, length($4)-1)}'`)

    for ((i=start;i<=num;i++));do
	ch0=`echo "${ch0_array[i]}" | awk '{if($1>=0) { print $1} else {print $1*-1 }}'`
	ch1=`echo "${ch1_array[i]}" | awk '{if($1>=0) { print $1} else {print $1*-1 }}'`
	diff=`echo "scale=4; $ch0-$ch1" | bc -l | awk '{if($1>=0) { print $1} else {print $\
1*-1 }}'`
	if (( $(echo "$diff > 10" | bc -l)));then
	    break
	fi
    done

    # if they differed after the first 5 samples
    if [[ $i -gt $((start+4)) ]]; then
        echo $line "sample: " $i
        echo "scale=6; ($i/$sample_freq)" | bc -l
    fi
    # if they never differed, then whole file is calibration
    if [[ $i == $num ]]; then
        echo $line "sample: " $i " **whole file is calibration**"
        echo "scale=6; ($num/$sample_freq)" | bc -l
    fi

done <$flist # feed in the filelist from here...
