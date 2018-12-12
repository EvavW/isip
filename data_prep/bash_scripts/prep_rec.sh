#!/usr/bin/sh

# prep_rec 
# MUST BE RUN FROM TOP LEVEL DIR WHERE REC FILES ARE LOCATED
# Eva von Weltin
# this script takes raw .rec files and generates fully annotated rec_bi, rect,
# and rect_bi files
# also pass a list of edf files in same sorted order as rec list
# use check_rec before using this script!!!
#
# usage: 
# bash prep_rec.sh rec.list edf.list (should be a list of .rec files and 
# corresponding .edf files)
#
# Eva von Weltin
# 20180523

# input variables
#
reclist=$1
edflist=$2
p=`pwd`

# exit script if any errors are encountered
set -e

# check input arguments
#
if [ $(cat $reclist | head -n 1 | awk '{print substr($1,length($1)-3,length($1))}') != ".rec" ]; then

    echo "first input should be a list of .rec files"
    exit 1

fi

if [ $(cat $edflist | head -n 1 | awk '{print substr($1,length($1)-3,length($1))}') != ".edf" ]; then

    echo "second input should be a list of .edf files"
    exit 1

fi

# declare variables for utility script names/locations
#
DATA_PREP="/data/isip/data/tuh_eeg_seizure/work/_TOOLS/data_prep/"
rm_bckg=$(echo $DATA_PREP"remove_label/remove_label.py")
make_biclass=$(echo $DATA_PREP"make_biclass/make_biclass.py")
rec_to_rect=$(echo $DATA_PREP"rec_to_rect/rec_to_rect.py")
full_ann=$(echo $DATA_PREP"full_ann/full_ann.py")

# sort rec files
#
while read file; do
    
    sort -t"," -k1n,1 -k2n,2 $file -o $file

done < $reclist

# remove intr annotations
#
python $rm_bckg -rdir $p -odir $p -label 19 $reclist 

# convert rec to rect
#
python $rec_to_rect -rdir $p -odir $p -ext rect $reclist

# fully annotate rec and rect files
# will remove any existing bckg annotations
# will snap any annotations in the first or last second to the nearest second
#
python $full_ann -rdir $p -odir $p -ext rec $reclist $edflist

sed -i 's/rec$/rect/' $reclist

python $full_ann -rdir $p -odir $p -ext rect $reclist $edflist

sed -i 's/rect$/rec/' $reclist

# create rec_bi and rect_bi files
#
python $make_biclass -rdir $p -odir $p -ext rec_bi $reclist

sed -i 's/rec$/rect/' $reclist

python $make_biclass -rdir $p -odir $p -ext rect_bi $reclist

sed -i 's/rect$/rec/' $reclist

# sort all files
#
while read line; do
    
    sort -t"," -k1n,1 -k2n,2 $line -o $line
    sed -i 's/rec$/rect/' $line
    sort -t"," -k1n,1 -k2n,2 $line -o $line
    sed -i 's/rect$/rect_bi/' $line
    sort -t"," -k1n,1 -k2n,2 $line -o $line
    sed -i 's/rect_bi$/rec_bi/' $line
    sort -t"," -k1n,1 -k2n,2 $line -o $line

done <$reclist # feed in rec files
