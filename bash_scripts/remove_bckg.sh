#!/bin/bash

#this script removes all background annotations from rec files 

filelist=$1

cat $filelist | while read file;

do

#uses an awk script called find_bckg.awk which prints only seizure annotations

     awk -f /data/isip/data/tuh_eeg_seizure/work/_TOOLS/bash_scripts/find_bckg.awk $file >$temp.txt 

mv $temp.txt $file

#can be changed to output to a new file rather than overwrite the old
  #>$file.limited

done

