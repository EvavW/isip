#!/bin/bash

# pass a list of tse files. lower directories must be in the same directory 
# format as tuh eeg v1.1.0
# example: ./dev_test/02_tcp_le/056/00005625/s001_2009_03_31/00005625_s001_t001.tse
#
# this will output basic seizure based stats seperated by database. you can 
# change where the database name is located depending on whether you do/do not 
# have an edf directory.
#
# usage: bash gen_stats.sh tse.list
#
# Eva von Weltin
# 20180523

# input variables
#
tselist=$1

# check input arguments
#
if [ $(cat $tselist | head -n 1 | awk '{print substr($1,length($1)-3,length($1))}') != ".tse" ]; then

    echo "first input should be a list of .tse files"
    exit 1

fi

# get a list of top sets (eval, train, etc)
#
# change the number at $(NF-N) to change where the database name is located
#
sets=($(echo $tselist | xargs cat | awk 'BEGIN {FS="/"} {print $(NF-5)}' | 
	sort |uniq))

#loop through each set. This is the main loop of the script
#
for set in "${sets[@]}"; do
    
    #get a list of tse files that are in this set
    #
    tse_arr=($(echo $tselist | xargs cat | grep "$set"))

    # count total number of files, sessions, and patients
    #
    all_files=$(echo ${#tse_arr[@]})

    all_sessions=$(echo ${tse_arr[@]} | sed 's/ /\n/g' | 
	awk 'BEGIN {FS="/"} {print $NF}' | 
	awk 'BEGIN {FS="_"} {print $1"_"$2}' | sort | uniq | wc -l)

    all_patients=$(echo ${tse_arr[@]} | sed 's/ /\n/g' | 
	awk 'BEGIN {FS="/"} {print $(NF-2)}' | sort | uniq |wc -l)

    # initialize variables for use in file loop
    #
    total_dur=0
    seiz_files=()
    num_seiz=0
    seiz_dur=0
    seiz_file_dur=0
    
    #loop through all files in the set.
    #
    for file in "${tse_arr[@]}"; do

	# add to total duration
	#
	file_dur=$(tail -n 1 $file | awk '{print $2}')
	total_dur=$(echo "$total_dur +$file_dur" | bc)

	# get number of seizures in this file
	#
	file_seiz=$(grep "1.0000" $file | grep -v bckg | wc -l)

	# if there are seizures in this file
	#
        if (( $(echo "$file_seiz != 0" | bc ) )); then

	    # add duration of the file to total duration of files with seizures
	    #
	    seiz_file_dur=$(echo "$seiz_file_dur +$file_dur" | bc)
	    
	    # add the duration of each seizure event in the file to seiz_arr
	    #
	   this_seiz_dur=$(grep "1.0000" $file | grep -v bckg | 
	       awk '{print $2"-"$1}' | bc -l | awk '{printf $1"+"}' | 
	       awk '{print substr($1,1,length($1)-1)}' | bc)

	   seiz_dur=$(echo "$seiz_dur + $this_seiz_dur" | bc)

	    #add to the total number of seizures
	    #
	    num_seiz=$(echo "$num_seiz + $file_seiz" | bc)

	    #add to the array of files with seizures
	    #
	    seiz_files+=($file)
	 
	fi

     done

    # count number of seizure sessions and patients
    #
    seiz_sessions=$(echo ${seiz_files[@]}| sed 's/ /\n/g' | 
	awk 'BEGIN {FS="/"} {print substr($NF,1,length($NF)-9)}' | sort | 
	uniq | wc -l)

    seiz_patients=$(echo ${seiz_files[@]}| sed 's/ /\n/g' | 
	awk 'BEGIN {FS="/"} {print $(NF-2)}' | sort | uniq | wc -l)

    #print stats for this database
    #
    echo $set":"
    echo "total files: "$all_files
    echo "total sessions: "$all_sessions
    echo "total patients: "$all_patients
    echo ""
    echo "files with seizures: "${#seiz_files[@]}
    echo "sessions with seizures: "$seiz_sessions
    echo "patients with seizures: "$seiz_patients
    echo "total number of seizures: "$num_seiz
    echo ""
    echo "total seizure duration: "$seiz_dur" secs ("$(echo "scale=4;($seiz_dur/$total_dur)*100" | bc -l)"%)"
    echo "total background duration: "$(echo "$total_dur - $seiz_dur" | bc -l )" secs"
    echo "total duration: "$total_dur" secs"
    echo "total duration of files with seizures: "$seiz_file_dur" secs ("$(echo "scale=4;($seiz_file_dur/$total_dur)*100" | bc -l)"%)"
    echo "-----------------------------"
    echo ""

done 

# end 
#
