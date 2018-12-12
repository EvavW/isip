#!/usr/bin/sh

reclist=$1
edflist=$2

# define scale for the duration of seizure events from which the trigger
# duration will be calculated
#
SEIZ_SCALE=60

# check input arguments
#
if [ $(cat $reclist | head -n 1 | \
    awk '{print substr($1,length($1)-3,length($1))}') != ".rec" ]; then
    echo "first input should be a list of .rec files"
    exit 1
fi
if [ $(cat $edflist | head -n 1 | \
    awk '{print substr($1,length($1)-3,length($1))}') != ".edf" ]; then
    echo "second input should be a list of .edf files"
    exit 1
fi

# convert lists into arrays
#
rec_arr=($(cat $reclist))
edf_arr=($(cat $edflist))

# loop through the files
#
i=0
for file in "${rec_arr[@]}"; do

    # sort the rec file
    #
    sort -t"," -k1n,1 -k2n,2 $file -o $file

    # initiate array to store post_stop_trig values
    #
    last_stop=()

    # get edf and its duration
    #
    edf=${edf_arr[i]}
    edf_dur=$(nedc_print_duration $edf | grep secs | \
	awk '{print $3}'| awk 'BEGIN {FS="."} {print $1}')
    
    # decare and populate two arrays for start and stop times
    #
    start_arr=($(awk 'BEGIN {FS=","} {print $2}' $file))
    stop_arr=($(awk 'BEGIN {FS=","} {print $3}' $file))

    # declare and populate arrays for channel number and label
    #
    channel_arr=($(awk 'BEGIN {FS=","} {print $1}' $file))
    label_arr=($(awk 'BEGIN {FS=","} {print $4}' $file))

    # loop through the start and stop arrays
    #
    j=0
    size=${#start_arr[@]}
    
    while [ $j -lt $size ]; do 
	
	# define annotation components for this event
	#
	channel=${channel_arr[j]}
	start=${start_arr[j]}
	stop=${stop_arr[j]}
	label=${label_arr[j]}

	# get the trigger duration from the precentage of the duration of
	# the event out of 60 seconds (SEIZ_SCALE)
	#
	event_dur=$( echo "scale=4; $stop-$start" | bc)
	percent=$(printf "%.*f\n" 1 \
	    $(echo "scale=2;$event_dur/$SEIZ_SCALE"|bc -l))
	trig_dur=$(echo "$percent * 10" | bc)

	# min and max trigger durations are 1 and 10
	#
	if (( $(echo "$trig_dur < 1" | bc))); then
	    trig_dur=1
	
	elif (( $(echo "$trig_dur > 10" | bc))); then
	    trig_dur=10
	fi

	# set default trigger values
	# adjust start and stop values
	#
	pre_trig_start=$(echo "scale=4; $start - ($trig_dur/2)" | bc -l)
	pre_trig_stop=$(echo "scale=4; $start + $trig_dur/2" | bc -l)
	start=$pre_trig_stop

	post_trig_start=$(echo "scale=4; $stop - $trig_dur/2" | bc -l)
	post_trig_stop=$(echo "scale=4; $stop + $trig_dur/2" | bc -l)
	stop=$post_trig_start

	# check if post_trig_stop in within the last second
	#
	if (( $(echo "$post_trig_stop > ($edf_dur-1)" |bc -l))); then
	    
	    ovlp=$(echo "scale=4; $post_trig_stop - ($edf_dur-1)" | bc -l)
	    
	    post_trig_stop=$(echo "scale=4; $post_trig_stop-$ovlp" | bc -l)
	    post_trig_start=$(echo "scale=4; $post_trig_start-$ovlp" \
		| bc -l)

	    stop=$(echo "scale=4; $stop-$ovlp" | bc -l)
	  
	fi

	# check if pre_trig_start ovlps with the previous post_trig_stop
	#
	if [ "$j" != "0" ]; then


	    if (( $(echo "$pre_trig_stop < ${last_stop[j-1]}"| bc -l))); then

		if [ "$channel" == "${channel_arr[j-1]}" ]; then

		    ovlp=$(echo "${last_stop[j-1]} - $pre_trig_start" | \
			bc -l)

		    pre_trig_start=$(echo "scale=4; $pre_trig_start+$ovlp"| \
			bc -l)
		    pre_trig_stop=$(echo "scale=4; $pre_trig_stop+$ovlp" | \
			bc -l)
		    start=$(echo "scale=4; $start+$ovlp" | bc -l)
		   
		fi

	    fi

	fi
	# check if pre_trig_start is before the first second
	#
	if (( $(echo "scale=4; $pre_trig_start < 1" | bc -l))); then

	    ovlp=$(echo "scale=4; 1 - $pre_trig_start" | bc -l)

	    pre_trig_start=$(echo "scale=4; $pre_trig_start+$ovlp" | bc -l)
	    pre_trig_stop=$(echo "scale=4; $pre_trig_stop+$ovlp" | bc -l)

	    start=$(echo "scale=4; $start+$ovlp" | bc -l)

	fi
	
	# clear the rec file
	#
	> $file

	# write new annotations to the rec file
	#
	echo $channel","$pre_trig_start","$pre_trig_stop",27" >> $file
	echo $channel","$start","$stop",0" >> $file
	echo $channel","$post_trig_start","$post_trig_stop",27" >> $file

	# append post_trig_stop to last_stop array
	#
        last_stop+=($post_trig_stop)

	# iterate event number
	#
	let "j++"

    done
    
    # iterate file number
    #
    let "i++"

done

# end 
#
