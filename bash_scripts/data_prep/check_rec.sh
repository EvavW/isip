#!/bin/bash

#check_rec.sh
#Checks rec files to make sure that:
#stop time of each event is greater than start time
#there are no overlapping annotations
#first annotation does not begin before 1 sec
#last annotation ends before the last second
#there are no repeated annotations
#??if fnsz, there are less than 12 channels. If gnsz, there are more than 12 channels??
#rec files do not need to be fully annoted. see check_tse.sh to evaluate fully annotated files.
#Eva von Weltin

#input variables
reclist=$1
edflist=$2


while read file; do #loop through each tse file in the list

    #sort the file by channel and start time
    sort -t"," -k1n,1 -k2n,2 $file -o $file

    #check for repeats
    if (( $(sort $file | uniq -d |wc -l | awk '{print $1" > 0"}' |bc)));then
	echo "ERROR: repeat annotations: $file"
	exit 1
    fi	
 
    #get duration of the associated edf file
    get_edf=$(echo $file | awk '{print substr($1,length($1)-27,length($1)-3)}' | awk 'BEGIN{FS="_"} {print $1"_"$2"_"$3}')
    edf=$(cat $edflist | grep $get_edf)
    edf_dur=$(nedc_print_duration $edf | grep secs | awk '{print $3}'| awk 'BEGIN {FS="."} {print $1}')
    ann_dur=0

    #decare and populate two arrays for start and stop times
    start_arr=($(awk 'BEGIN {FS=","} {print $2}' $file))
    stop_arr=($(awk 'BEGIN {FS=","} {print $3}' $file))
    chan_arr=($(awk 'BEGIN {FS=","} {print $1}' $file))

    for value in {0..21}; do
	temp=$(echo "check_$value")
	declare "${temp}"=0
    done
    
    #check first second
    if (( $(echo "${start_arr[0]} < 1" | bc -l )));then
	echo "ERROR: begins before first second: $file"
	exit 1
    fi

    #check last second
    size=$(echo "${#stop_arr[@]}" )
    size=$((size-1))
    last=$(echo "${stop_arr[size]}")
    if (( $(echo "$last > ($edf_dur-1)" | bc -l )));then
	echo "ERROR: ends during last second: $file"
	exit 1
    fi

    # loop through stop array
    i=0
    size=$(echo "${#stop_arr[@]}" )
    while [ $i -lt $size ];
    do
	#pad with zeros
	start=$(echo "scale=4; (${start_arr[i]}*1)/1" |bc)
	stop=$(echo "scale=4; (${stop_arr[i]}*1)/1" |bc)
	channel=$(echo ${chan_arr[i]})

	#check every stop time is greater than start time
	if (( $(echo "$start >= $stop" | bc -l))); then
	    echo "ERROR: start > stop: $file"
	    exit 1
	fi
	
	# check for overlapping annotations on each channel
	for value in {0..21}; do
	    if [ "$channel" == "$value" ]; then
		check_var=$(echo "check_$value")
		check=$(echo "${!check_var}")
		if (( $(echo "$start > $check" | bc -l))); then
		    declare "${check_var}"=$(echo $start)
		else
		    echo "ERROR: Overlapping Annotations on $value channel: $file"
		    exit 1
		fi    
	    fi
	done

	let "i++"
    done

done < $reclist # feed in each file from the file list
