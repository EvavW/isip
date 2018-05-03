#!/bin/bash

filelist=$1 
odir='' 
echo $2 >odir 
newdir='' 
newname='' 
makedirs='' 
makefiles='' 

cat $filelist | while read file ;

do

echo $file | awk -F/ '{print "/" $(NF-4) "/" $(NF-2) "/" $(NF-1) "/"}' >newdir

echo $file | awk -F/ '{

if ( length ($NF) == 6 ) 
print $(NF-2) "_" substr($(NF-1),0,3) "_" substr($NF,0,1) "00" substr($NF,3,5);                                       

else if ( length ($NF) == 7 ) 
print $(NF-2) "_" substr($(NF-1),0,3) "_" substr($NF,0,1) "0" substr($NF,3,6);                                       

else if ( length ($NF) == 8 ) 
print $(NF-2) "_" substr($(NF-1),0,3) "_" substr($NF,0,1) substr($NF,3,7)                            }' >newname

echo -n $(cat odir newdir) >makedirs
cat makedirs | tr -d " \t\n\t" > temp
mv temp makedirs

echo -n $(cat makedirs newname) >makefiles
cat makefiles | tr -d " \t\n\t" > temp
mv temp makefiles

cat makedirs | xargs mkdir -p

cat makefiles

cat $file > $(cat makefiles) 

done

rm newdir makedirs odir newname makefiles

