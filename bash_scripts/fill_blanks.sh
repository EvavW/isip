#!/usr/bin/sh

flist=$1 # should be a list of tse files WITHOUT tse header
edflist=$2

# iterate through file list
while read file; do

    get_edf=$(echo $file | awk '{print substr($1,length($1)-27,length($1)-3)}' | awk 'BEGIN{FS="_"} {print $1"_"$2"_"$3}')
    edf=$(cat $edflist | grep $get_edf)
    edf_dur=$(nedc_print_duration $edf | grep secs | awk '{print $3}'| awk 'BEGIN {FS="."} {print $1}')
    #print filename
    echo $file
    
    # sort according to start and stop time
    sort -t"," -k1n,1 -k2n,2 $file -o $file

    ann_arr=() #declare annotation array
    #iterate through each line in the file and append the line 
    ## to ann_arr
    while read line; do
	ann_arr+=("`echo $line`")
    done < $file # feed in file

    i="0" #declare array iterator
    for ann in "${ann_arr[@]}"; do
	j=$((i+1)) #position of next annotation
	# if there is only one annotation in the file...
	if [[ "${#ann_arr[@]}" == "1" ]]; then
	    # annotate null from 0 to annotation start time
	    stop=`echo $ann | awk '{print $1}'`
            echo "0.0000 "$stop" null 1.000" >>temp.tse
	    echo $ann >>temp.tse
	# if there is more than one annotation and this is the first...    
	elif [[ "$i" == "0" ]]; then
	    # annotate null from 0 to first ann start time
	    stop=`echo $ann | awk '{print $1}'`
	    echo "0.0000 "$stop" null 1.000" >>temp.tse
	    echo $ann >>temp.tse
	    # annotate null from first end time to next start time
	    start=`echo ${ann_arr[i]} | awk '{print $2}'`
	    stop=`echo ${ann_arr[j]} | awk '{print $1}'`
	    echo $start" "$stop" null 1.000" >>temp.tse
	# if there is more than one annotation and this is the last...    
	elif [[ "$i" == "$((${#ann_arr[@]}-1))" ]]; then
	    echo $ann >>temp.tse
	    #annotate from last end time to the end of the file
	    start=`echo ${ann_arr[i]} | awk '{print $2}'`
	    echo $start" "$edf_dur".0000 null 1.0000" >> temp.tse
	# if there is more than one annotation and this is not
	## the first or the last
	else
	    # annotate from this stop time to next start time
	    echo $ann >>temp.tse
	    start=`echo ${ann_arr[i]} | awk '{print $2}'`
	    stop=`echo ${ann_arr[j]} | awk '{print $1}'`
	    echo $start" "$stop" null 1.000" >>temp.tse
	fi

    let "i++" # iterate ann array position
    done
    
    #send output file to input file
    mv temp.tse $file

done < $flist # feed in list of files
