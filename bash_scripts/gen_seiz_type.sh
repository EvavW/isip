#!/bin/bash


filelist=$1

cat $filelist | while read file ;

do


if [ -s $file ]
then

cat $file | awk                                                                 'BEGIN {FS=","}                                                                 {if (($1 == 0) && ($4 == 6)) print "0";                                       else if (($1 == 0) && ($4 == 7)) print "seiz";                                 else if (($1 == 0) && ($4 == 8)) print "fnsz";                                 else if (($1 == 0) && ($4 == 9)) print "gnsz";                                 else if (($1 == 0) && ($4 == 10)) print "spsz";                                else if (($1 == 0) && ($4 == 11)) print "cpsz";                                else if (($1 == 0) && ($4 == 12)) print "absz";                                else if (($1 == 0) && ($4 == 13)) print "tnsz";                                else if (($1 == 0) && ($4 == 14)) print "cnsz";                                else if (($1 == 0) && ($4 == 15)) print "tcsz";                                else if (($1 == 0) && ($4 == 16)) print "atsz";                                else if (($1 == 0) && ($4 == 17)) print "mysz";                                          }' 

else 
echo "0"

fi

done

