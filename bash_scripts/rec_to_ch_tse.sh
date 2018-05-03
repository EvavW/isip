#!/bin/bash

#input variables
filelist=$1

# this script does not add headers to tse files!!! 
## you must remove all existing tse before running this script. They will be appended to!!

while read file; do #loop through 

    while read line; do

	channel=$(echo $line | awk 'BEGIN {FS=","} {print $1}')
	start=$(echo $line | awk 'BEGIN {FS=","} {print $2}')
	stop=$(echo $line | awk 'BEGIN {FS=","} {print $3}')
	num_label=$(echo $line | awk 'BEGIN {FS=","} {print $4}')

	label=$(echo $num_label | sed 's/^0$/null/' | sed 's/^6$/bckg/' | sed 's/^21$/eyem/'  | sed 's/^22$/chew/' | sed 's/^23$/shiv/' | sed 's/^24$/musc/' | sed 's/^25$/elpp/' | sed 's/^26$/elst/' | sed 's/^7$/seiz/' | sed 's/^8$/fnsz/' | sed 's/^9$/gnsz/' | sed 's/^10$/spsz/' | sed 's/^11$/cpsz/' | sed 's/^12$/absz/' | sed 's/^13$/tnsz/' | sed 's/^14$/cnsz/' | sed 's/^15$/tcsz/' | sed 's/^16$/atsz/' | sed 's/^17$/mysz/')
	
	out_file=$(echo $file | awk -v channel="$channel" '{if (channel < 10) print substr($1,1,length($1)-4)"_ch00"channel".tse"; else print substr($1,1,length($1)-4)"_ch0"channel".tse"}')

	echo  $start" "$stop" "$label" 1.0000" >> $out_file
	
	done < $file

    done < $filelist # feed in each file from the file list
