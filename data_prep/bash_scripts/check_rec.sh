#!/bin/bash

# check_rec.sh
# usage: bash check_rec.sh rec.list edf.list
# Checks rec files to make sure that:
# stop time of each event is greater than start time (needs a manual fix)
# there are no overlapping annotations (needs a manual fix)
# first annotation does not begin before 1 sec (can be fixed with full ann)
# last annotation ends before the last second (can be fixed with full ann)
# there are no repeated annotations (these can be fixed with sort | uniq)
# rec files do not need to be fully annotated. See check_tse.sh to evaluate 
# fully annotated files.
#
# Eva von Weltin
# 20180523

# input variables
#
reclist=$1
edflist=$2

# check input arguments
#
if [ $(cat $reclist | head -n 1 | awk '{print substr($1,length($1)-3,length($1))}') != ".rec" ]; then

    echo "first input should be a list of .rec files"
    exit 1

fi

if [ $(cat $edflist | head -n 1 | awk '{print substr($1,length($1)-3,length($1))}') != ".edf" ]; then

    echo "second input should be a list of .edf files"
    exit 1

fi

# convert lists into arrays
#
rec_arr=($(cat $reclist))
edf_arr=($(cat $edflist))

# loop through the list of rec files
#
i=0
for file in "${rec_arr[@]}"; do

# an empty file cannot have any of these issues, skip them
#
if [ -s $file ]; then
	
    # sort the file by channel and start time
    #
    sort -t"," -k1n,1 -k2n,2 $file -o $file

    # check for repeats
    #
    if (( $(sort $file | uniq -d |wc -l | awk '{print $1" > 0"}' | bc) )); then

	echo "ERROR: repeat annotations: $file"

    fi	
 
    # get duration of the associated edf file
    #
    edf=${edf_arr[i]}
    edf_dur=$(nedc_print_duration $edf | grep secs | awk '{print $3}'| \
	awk 'BEGIN {FS="."} {print $1}')
    ann_dur=0

    # declare and populate two arrays for start and stop times
    #
    start_arr=($(awk 'BEGIN {FS=","} {print $2}' $file))
    stop_arr=($(awk 'BEGIN {FS=","} {print $3}' $file))
    chan_arr=($(awk 'BEGIN {FS=","} {print $1}' $file))

    # determine montage definition based on file path
    #
    montage=$(echo  $file  awk 'BEGIN {FS="/"} {print $(NF-5)}')
    
    if [ "$montage" == "01_tcp_ar" ] || [ "$montage" == "02_tcp_le" ]; then
	
	chan_num=21

    elif [ "$montage" == "03_tcp_ar_a" ] || [ "$montage" == "04_tcp_le_a" ]; 
    then
	
	chan_num=19
	
    fi

    for value in $(seq 0 $chan_num); do

	temp=$(echo "check_$value")
	declare "${temp}"=0

    done

    # check first second
    #
    if (( $(echo "${start_arr[0]} < 1" | bc -l ) )); then

	echo "ERROR: begins before first second: $file"

    fi

    # check last second
    #
    size=$(echo "${#stop_arr[@]}" )
    size=$((size-1))
    last=$(echo "${stop_arr[size]}")
    if (($(echo "$last > ($edf_dur-1)" | bc -l ))); then

	echo "ERROR: ends during last second: $file"

    fi

    # loop through stop array
    #
    j=0
    size=$(echo "${#stop_arr[@]}" )
    while [ $j -lt $size ];
    do
	# pad with zeros
	#
	start=$(echo "scale=4; (${start_arr[j]}*1)/1" | bc)
	stop=$(echo "scale=4; (${stop_arr[j]}*1)/1" | bc)
	channel=$(echo ${chan_arr[j]})

	# check whether every stop time is greater than start time
	#
	if (( $(echo "$start >= $stop" | bc -l) )); then

	    echo "ERROR: start > stop: $file"

	fi

	# check for overlapping annotations on each channel
	#
	for chan in $(seq 0 $chan_num); do
	    
	    # check which channel this event is occuring on
	    #
	    if [ "$channel" == "$chan" ]; then

		# check if this channel should exist
		#
		if (( $(echo "$channel > $chan_num" | bc) )); then

		    echo "ERROR: incorrect montage definition: $file"

		fi

		# access existing list of annotations for this channel
		#
		check_var=$(echo "check_$chan")
		check_prev=$(echo "${!check_var}")
		
		# if this start time is greater than the previous stop time,
		# add this annotation to list of existing annotations
		#

		# only check if there actually is a previous annotation
		#
		if [ $check_prev != 0 ]; then

		    if (( $(echo "$start > $check_prev" | bc -l) )); then

			declare "${check_var}"=$(echo $start)
			
			# print an error if there is an overlap
			#
		    else

			echo "ERROR: Overlapping Annotations on $value channel: $file"
		    fi    
		 
		fi

	    fi

	done

	# iterate event array
	#
	let "j++"

    done

fi

# iterate file number
#
let "i++"

done

# end
#
