#!/usr/bin/sh

flist=$1

while read file; do 

    sed -i 's/,1$/spsw/' $file
    sed -i 's/,2$/gped/' $file
    sed -i 's/,3$/pled/' $file
    sed -i 's/,4$/eyem/' $file
    sed -i 's/,5$/artf/' $file
    sed -i 's/,6$/bckg/' $file

done < $flist
