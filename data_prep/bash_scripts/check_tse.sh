#!/bin/bash

# check_tse.sh
# Checks tse files to make sure that stop time of each event is greater than 
# start time and that 
# total duration of all events adds up to total duration of the edf file. 
# tse files should be fully annotated
#
# usage: bash check_tse.sh tse.list edf.list
#
# Eva von Weltin
# 20180523

# input variables
#
tselist=$1
edflist=$2

# check input arguments
#
if [ $(cat $tselist | head -n 1 | awk '{print substr($1,length($1)-3,length($1))}') != ".tse" ]; then

    echo "first input should be a list of .tse files"
    exit 1

fi

if [ $(cat $edflist | head -n 1 | awk '{print substr($1,length($1)-3,length($1))}') != ".edf" ]; then

    echo "second input should be a list of .edf files"
    exit 1

fi

# convert lists into arrays
#
tse_arr=($(cat $tselist))
edf_arr=($(cat $edflist))

#loop through each tse file in the list
#
i=0
for file in "${tse_arr[@]}"; do
    
    # clear variables between each file
    #
    ann_time=0
    ann_dur=0
    
    # get duration of the associated edf file
    #
    edf=${edf_arr[i]}
    edf_dur=$(nedc_print_duration $edf | grep secs | awk '{print $3}'| awk 'BEGIN {FS="."} {print $1}')

    # declare and populate two arrays for start and stop times
    #
    start_arr=($(awk '{if ($4=="1.0000") print $1}' $file))
    stop_arr=($(awk '{if ($4=="1.0000") print $2}' $file))

    # loop through start array and check that stop time is greater than start 
    # time
    #
    j=1
    size=$(echo "${#start_arr[@]}" )
    while [ $j -lt $size ]; do

	if [[ $(echo "scale=4; (${start_arr[j]}*1)/1" | bc) != \
	    $(echo "scale=4; (${stop_arr[j-1]}*1)/1" | bc) ]]; then
	    
	    echo $file": ""${start_arr[j]}" "${stop_arr[j-1]}"

        fi

	let "j++"
       
    done

    # loop through start array and check that duration of each event adds up 
    # to total duration of the edf file
    #
    j=0
    size=$(echo "${#start_arr[@]}" )

    while [ $j -lt $size ]; do

	ann_time=$(echo "${stop_arr[j]}-${start_arr[j]}" | bc)
	ann_dur=$(echo "$ann_dur+$ann_time" | bc)
	let "j++"

    done
    # fix how it is split
    ann_dur=$(echo $ann_dur | awk 'BEGIN {FS="."} { print $1}')

    if [[ "$edf_dur" != "$ann_dur" ]]; then

	echo $file": duration of annotation != edf duration"

    fi

# iterate file number
#
let "i++"

done

# end
#
