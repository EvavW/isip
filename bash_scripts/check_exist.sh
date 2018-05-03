#!/bin/bash

# this script checks that all files in a list of files exist.
# the directory that you run this script from have a list called 
# check.list (CHANGE THIS)
#------------------------------------
#read <$1
#for line in $1

check=$1

cat $check | while read line ;

do

if ! [ -f $line ]  
    then
    echo $line "does not exist"
    echo $line >> does_not_exist.list

#elif [ -f $line ]
  #  then
   # echo $line "exists"
fi
    
done
