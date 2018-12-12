#!/usr/bin/sh

# rec_to_tse 
# MUST BE RUN FROM TOP LEVEL DIR WHERE REC FILES ARE LOCATED
# this script creates lbl, lbl_bi, tse, and tse_bi files from rec, rec_bi, 
# rect, and rect_bi files. 
#
# usage:
# bash rec_to_tse.sh rec.list (should be a list of .rec files)
# there must already be rect, rec_bi, and rect_bi files in the same path
# you can use prep_rec to create these files 
#
# Eva von Weltin
# 20180523

# get input variables
#
reclist=$1
p=`pwd`

# exit script if any errors are encountered
#set -e

# define utility variables
# 
rec_to_chtse="/data/isip/data/tuh_eeg_seizure/work/_TOOLS/data_prep/rec_to_chtse/rec_to_chtse.py"
mfile="/data/isip/data/tuh_eeg_seizure/work/_TOOLS/data_prep/rec_to_chtse/map.txt"
full_map="/data/isip/tools/master/nfc/util/python/nedc_rec_to_lbl/full_map.txt"
bi_map="/data/isip/tools/master/nfc/util/python/nedc_rec_to_lbl/bi_map.txt"

ref_map="/data/isip/tools/master/nfc/util/python/nedc_rec_to_lbl/ref_montage.txt"
le_map="/data/isip/tools/master/nfc/util/python/nedc_rec_to_lbl/le_montage.txt"
ref_a_map="/data/isip/tools/master/nfc/util/python/nedc_rec_to_lbl/ref_a_montage.txt"

# check input arguments
#
if [ $(cat $reclist | head -n 1 | awk '{print substr($1,length($1)-3,length($1))}') != ".rec" ]; then

    echo "first input should be a list of .rec files"
    exit 1

fi

# break rec.list by montage definition
#
grep -F "01_tcp" $reclist > 01.list
grep -F "02_tcp" $reclist > 02.list
grep -F "03_tcp" $reclist > 03.list

# rect_bi > lblt_bi > tse_bi 
#

# change montage lists to point to rect_bi files
#
sed -i 's/rec$/rect_bi/' 01.list
sed -i 's/rec$/rect_bi/' 02.list
sed -i 's/rec$/rect_bi/' 03.list

# run nedc_rec_to_lbl on each montage list
#
nedc_rec_to_lbl -map $bi_map -montage $ref_map -rdir $p -odir $p -ext lblt_bi 01.list
nedc_rec_to_lbl -map $bi_map -montage $le_map -rdir $p -odir $p -ext lblt_bi 02.list
nedc_rec_to_lbl -map $bi_map -montage $ref_a_map -rdir $p -odir $p -ext lblt_bi 03.list

# run nedc_convert_labels on lblt_bi files to get tse_bi files
# remove lblt_bi files they are only used to create tse_bi
#
find . -name "*.lblt_bi" > lblt_bi.list
nedc_convert_labels -tse -ext tse_bi -rdir $p -odir $p lblt_bi.list
find . -name "*.lblt_bi" | xargs rm

# rect > lblt > tse
#

# change montage lists to point to rect files
#
sed -i 's/rect_bi$/rect/' 01.list
sed -i 's/rect_bi$/rect/' 02.list
sed -i 's/rect_bi$/rect/' 03.list

# run nedc_rec_to_lbl on each montage list
#
nedc_rec_to_lbl -map $full_map -montage $ref_map -rdir $p -odir $p -ext lblt 01.list
nedc_rec_to_lbl -map $full_map -montage $le_map -rdir $p -odir $p -ext lblt 02.list
nedc_rec_to_lbl -map $full_map -montage $ref_a_map -rdir $p -odir $p -ext lblt 03.list

# run nedc_convert labels on lblt files to create tse files
# remove lblt files they are only used to create tse
#
find . -name "*.lblt" > lblt.list
nedc_convert_labels -tse -ext tse -rdir $p -odir $p lblt.list
find . -name "*.lblt" | xargs rm

# rec_bi > lbl_bi
#

# change montage lists to point to rec_bi files
#
sed -i 's/rect$/rec_bi/' 01.list
sed -i 's/rect$/rec_bi/' 02.list
sed -i 's/rect$/rec_bi/' 03.list

# run nedc_rec_to_lbl on each montage list
#
nedc_rec_to_lbl -map $bi_map -montage $ref_map -rdir $p -odir $p -ext lbl_bi 01.list
nedc_rec_to_lbl -map $bi_map -montage $le_map -rdir $p -odir $p -ext lbl_bi 02.list
nedc_rec_to_lbl -map $bi_map -montage $ref_a_map -rdir $p -odir $p -ext lbl_bi 03.list

# rec > lbl 
#

# change montage list to point to rec files
#
sed -i 's/rec_bi$/rec/' 01.list
sed -i 's/rec_bi$/rec/' 02.list
sed -i 's/rec_bi$/rec/' 03.list

# run nedc_rec_to_lbl on each montage list
#
nedc_rec_to_lbl -map $full_map -montage $ref_map -rdir $p -odir $p 01.list
nedc_rec_to_lbl -map $full_map -montage $le_map -rdir $p -odir $p 02.list
nedc_rec_to_lbl -map $full_map -montage $ref_a_map -rdir $p -odir $p 03.list

# rec > ch_tse
#

# rec_bi > ch_tse_bi
#
sed -i 's/rec$/rec_bi/' $reclist

python $rec_to_chtse -rdir $p -odir $p -ext tse_bi -mfile $mfile $reclist

sed -i 's/rec_bi$/rec/' $reclist

python $rec_to_chtse -rdir $p -odir $p -ext tse -mfile $mfile $reclist

# housekeeping
#
rm 01.list 02.list 03.list lblt_bi.list lblt.list

# end
#
