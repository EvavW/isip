#!/usr/bin/sh

# rec_to_lab
# MUST BE RUN FROM TOP LEVEL DIR WHERE REC FILES ARE LOCATED
# this lab creates lab, labt, lab_bi, labt_bi, lab_ov, lab_biov, labt_ov, and
# labt_biov files from rec, rect_bi, rect, and rec_bi files. 
#
# usage:
# bash rec_to_lab rec.list (should be a list of rec files.)
# there must already be rect, rec_bi, and rect_bi files in the path
# you can create these files with rec_prep.sh
#
# Eva von Weltin
# 20180523

# input variables
#
reclist=$1
p=`pwd`

# check input arguments
#
if [ $(cat $reclist | head -n 1 | awk '{print substr($1,length($1)-3,length($1))}') != ".rec" ]; then

    echo "first input should be a list of .rec files"
    exit 1

fi


# create variables to store path to script and parameter file used
#
convert="/data/isip/exp/tuh_eeg/exp_0647/nfc/util/python/nedc_convert_label/nedc_convert_label.py"
map="/data/isip/exp/tuh_eeg/exp_0647/nfc/util/python/nedc_convert_label/overall_labels_comp.txt"

# rect_bi > labt_bi 
# rect_bi > labt_biov > lab_biov
#

# change rec.list to point to rect_bi files
#
sed -i 's/rec$/rect_bi/' $reclist

# run legacy nedc_convert_labels on rect_bi files
#
python $convert -cmap $map -out_fmt lab -rdir $p -odir $p $reclist

# rename lab files to labt_bi
#
find . -name "*.lab" -exec rename lab labt_bi '{}' +

# run legacy nedc_convert_labels with agg option on rect_bi
#
python $convert -cmap $map -out_fmt lab -rdir $p -odir $p -aggregate $reclist 

# rename lab_ov files to labt_biov
#
find . -name "*.lab_ov" -exec rename lab_ov labt_biov '{}' +

# copy labt_biov files into lab_biov files
#
cp_array=(`find . -name "*.labt_biov"`)

for i in "${cp_array[@]}"; do

    new=`echo $i | awk '{print substr($1, 1, length($1)-9)"lab_biov"}'`
    cp $i $new

done

# rect > labt 
# rect > labt_ov > lab_ov
#

# change rec.list to point to rect files
#
sed -i 's/rect_bi$/rect/' $reclist

# run legacy nedc_convert_labels on rect files
#
python $convert -cmap $map -out_fmt lab -rdir $p -odir $p $reclist

# rename lab files to labt
#
find . -name "*.lab" -exec rename lab labt '{}' +

# run legacy nedc_convert_labels with agg option on rect files
#
python $convert -cmap $map -out_fmt lab -rdir $p -odir $p -aggregate $reclist 

# rename lab_ov files to labt_ov
#
find . -name "*.lab_ov" -exec rename lab_ov labt_ov '{}' +

# copy labt_ov files into lab_ov files
#
cp_array=(`find . -name "*.labt_ov"`)

for i in "${cp_array[@]}"; do

    new=`echo $i | awk '{print substr($1, 1, length($1)-7)"lab_ov"}'`
    cp $i $new

done

# rec_bi > lab_bi
#

# change rec.list to point to rec_bi files
#
sed -i 's/rect$/rec_bi/' $reclist

# run legacy nedc_convert_labels with agg option on rec_bi files
#
python $convert -cmap $map -out_fmt lab -rdir $p -odir $p $reclist

# rename rec files to rec_bi
#
find . -name "*.lab" -exec rename lab lab_bi '{}' +

# rec > lab 
#

# change rec.list to point to rec files
#
sed -i 's/rec_bi$/rec/' $reclist

# run legacy nedc_convert_labels on rec files
#
python $convert -cmap $map -out_fmt lab -rdir $p -odir $p $reclist

#end
