#!/bin/bash

#input variables
filelist=$1


while read file; do #loop through 

    first="3600"
    second="7200"
    third="10800"
    fourth="14400"

    rec_00=$(echo $file | awk '{print substr($1,1,length($1)-4)"_00.rec"}')
    rec_01=$(echo $file | awk '{print substr($1,1,length($1)-4)"_01.rec"}')
    rec_02=$(echo $file | awk '{print substr($1,1,length($1)-4)"_02.rec"}')
    rec_03=$(echo $file | awk '{print substr($1,1,length($1)-4)"_03.rec"}')
    rec_04=$(echo $file | awk '{print substr($1,1,length($1)-4)"_04.rec"}')

    while read line; do
       
	channel=$(echo $line | awk 'BEGIN {FS=","} {print $1}')
	label=$(echo $line | awk 'BEGIN {FS=","} {print $4}')
	start=$(echo $line | awk 'BEGIN {FS=","} {print $2}')
	stop=$(echo $line | awk 'BEGIN {FS=","} {print $3}')
	# ** check annotation
	if (( $(echo "$stop <= $start" | bc -l) )); then
	    echo "error: annotation error in "$line
        fi
	# **
#--------------------------------------------------------------------------#
	if (( $(echo "$start <$first" | bc -l) ));then
	    #if 0 <= $start < $first
	    if (( $(echo "$stop < $first" | bc -l) )); then
		# both start and stop are less than first
		echo $line >> $rec_00
	    elif (( $(echo "$stop > $first" | bc -l) )); then
		diff=$(echo "scale=4; $stop-$first" | bc -l)
		echo $channel","$start",3599,"$label >> $rec_00
		echo $channel",1,"$diff","$label >> $rec_01
	    fi 
#--------------------------------------------------------------------------#
	elif (( $(echo "$start <$second" | bc -l) ));then
	    # substract an hour from start and stop
	    new_start=$(echo "scale=4; $start-$first" | bc -l)
	    new_stop=$(echo "scale=4; $stop-$first" | bc -l)
	    
	    if (( $(echo "$new_stop < $first" | bc -l) )); then
		# both start and stop are less than first
		echo $channel","$new_start","$new_stop","$label >> $rec_01
	    elif (( $(echo "$stop > $first" | bc -l) )); then
		diff=$(echo "scale=4; $new_stop-$first" | bc -l)
		echo $channel","$new_start",3599,"$label >> $rec_01
		echo $channel",1,"$diff","$label >> $rec_02
	    fi
#--------------------------------------------------------------------------#
	elif (( $(echo "$start <$third" | bc -l) ));then
	    # substract two hours from start and stop
	    new_start=$(echo "scale=4; $start-$second" | bc -l)
	    new_stop=$(echo "scale=4; $stop-$second" | bc -l)
	    
	    if (( $(echo "$new_stop < $first" | bc -l) )); then
		# both start and stop are less than first
		echo $channel","$new_start","$new_stop","$label >> $rec_02
	    elif (( $(echo "$stop > $first" | bc -l) )); then
		diff=$(echo "scale=4; $new_stop-$first" | bc -l)
		echo $channel","$new_start",3599,"$label >> $rec_02
		echo $channel",1,"$diff","$label >> $rec_03
	    fi
#--------------------------------------------------------------------------#
	elif (( $(echo "$start <$fourth" | bc -l) ));then
	    # substract three hours from start and stop
	    new_start=$(echo "scale=4; $start-$third" | bc -l)
	    new_stop=$(echo "scale=4; $stop-$third" | bc -l)
	    
	    if (( $(echo "$new_stop < $first" | bc -l) )); then
		# both start and stop are less than first
		echo $channel","$new_start","$new_stop","$label >> $rec_03
	    elif (( $(echo "$stop > $first" | bc -l) )); then
		diff=$(echo "scale=4; $new_stop-$first" | bc -l)
		echo $channel","$new_start",3599,"$label >> $rec_03
		echo $channel",1,"$diff","$label >> $rec_04
	    fi

	 fi # start < first,second,third,fourth

    done < $file # feed in each line(annotation) of the file

done < $filelist # feed in each file from the file list
