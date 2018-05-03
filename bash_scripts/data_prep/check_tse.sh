#!/bin/bash

#check_tse.sh
#Checks tse files to make sure that stop time of each event is greater than start time and that 
#total duration of all events adds up to total duration of the edf file. 
#tse files should be fully annotated
#Eva von Weltin

#input variables
tselist=$1
edflist=$2


while read file; do #loop through each tse file in the list

    # get duration of the associated edf file
    get_edf=$(echo $file | awk '{print substr($1,length($1)-27,length($1)-3)}' | awk 'BEGIN{FS="_"} {print $1"_"$2"_"$3}')
    edf=$(cat $edflist | grep $get_edf)
    edf_dur=$(nedc_print_duration $edf | grep secs | awk '{print $3}'| awk 'BEGIN {FS="."} {print $1}')
    ann_dur=0

    #decare and populate two arrays for start and stop times
    start_arr=($(awk '{if ($4=="1.0000") print $1}' $file))
    stop_arr=($(awk '{if ($4=="1.0000") print $2}' $file))

    # loop through start array and check that stop time is greater than start time
    i=1
    size=$(echo "${#start_arr[@]}" )
    while [ $i -lt $size ];
    do
	if [[ $(echo "scale=4; (${start_arr[i]}*1)/1" | bc) != $(echo "scale=4; (${stop_arr[i-1]}*1)/1" | bc) ]]; then
	    echo $file": ""${start_arr[i]}" "${stop_arr[i-1]}"
        fi
	let "i++"
       
    done

    # loop through start array and check that duration of each event adds up to total duration of the edf file
    i=0
    size=$(echo "${#start_arr[@]}" )
    while [ $i -lt $size ];
    do
	ann_time=$(echo "${stop_arr[i]}-${start_arr[i]}" | bc)
	ann_dur=$(echo "$ann_dur+$ann_time" | bc)
	let "i++"
    done

    ann_dur=$(echo $ann_dur | awk 'BEGIN {FS="."} { print $1}')

    if [[ "$edf_dur" != "$ann_dur" ]]; then

	echo $file": duration of annotation != edf duration"
    fi

done < $tselist # feed in each file from the file list
