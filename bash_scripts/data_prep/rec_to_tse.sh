#!/usr/bin/sh

# rec_to_tse
## Eva von Weltin
### this script creates lbl, lbl_bi, tse, and tse_bi files from rec, rec_bi, 
### rect, and rect_bi files. 

# usage:
## bash rec_to_tse.sh rec.list (should be a list of .rec files)
### there must already be rect, rec_bi, and rect_bi files in the same path
### you can use prep_rec to create these files 

reclist=$1
p=`pwd`
#----------------------------------------------------------------------#
# break rec.list by montage defenition
grep -F "01_tcp" $reclist > 01.list
grep -F "02_tcp" $reclist > 02.list
grep -F "03_tcp" $reclist > 03.list

#----------------------------------------------------------------------#
# declare variables to store parameter files needed for nedc_rec_to_lbl and
# for necd_convert_labels
full_map="/data/isip/tools/haswell/nfc/util/python/nedc_rec_to_lbl/full_map.txt"
bi_map="/data/isip/tools/haswell/nfc/util/python/nedc_rec_to_lbl/bi_map.txt"

ref_map="/data/isip/tools/haswell/nfc/util/python/nedc_rec_to_lbl/ref_montage.txt"
le_map="/data/isip/tools/haswell/nfc/util/python/nedc_rec_to_lbl/le_montage.txt"
ref_a_map="/data/isip/tools/haswell/nfc/util/python/nedc_rec_to_lbl/ref_a_montage.txt"

#----------------------------------------------------------------------#
# rect_bi > lblt_bi > tse_bi 
## change montage lists to point to rect_bi files
sed -i 's/rec$/rect_bi/' 01.list
sed -i 's/rec$/rect_bi/' 02.list
sed -i 's/rec$/rect_bi/' 03.list
## run nedc_rec_to_lbl on each montage list
nedc_rec_to_lbl -map $bi_map -montage $ref_map -rdir $p -odir $p 01.list
nedc_rec_to_lbl -map $bi_map -montage $le_map -rdir $p -odir $p 02.list
nedc_rec_to_lbl -map $bi_map -montage $ref_a_map -rdir $p -odir $p 03.list
## rename lbl files to lblt_bi
find . -name "*.lbl" -exec rename lbl lblt_bi '{}' +
find . -name "*.lblt_bi" > lblt_bi.list
## run nedc_convert_labels on lblt_bi files to get tse_bi files
nedc_convert_labels -tse -ext tse_bi -rdir $p -odir $p lblt_bi.list
find . -name "*.lblt_bi" | xargs rm

#----------------------------------------------------------------------#
# rect > lblt > tse
## change montage lists to point to rect files
sed -i 's/rect_bi$/rect/' 01.list
sed -i 's/rect_bi$/rect/' 02.list
sed -i 's/rect_bi$/rect/' 03.list
## run nedc_rec_to lbl on each montage list
nedc_rec_to_lbl -map $full_map -montage $ref_map -rdir $p -odir $p 01.list
nedc_rec_to_lbl -map $full_map -montage $le_map -rdir $p -odir $p 02.list
nedc_rec_to_lbl -map $full_map -montage $ref_a_map -rdir $p -odir $p 03.list
## rename lbl files to lblt
find . -name "*.lbl" -exec rename lbl lblt '{}' +
find . -name "*.lblt" > lblt.list
## run nedc_convert labels on lblt files to create tse files
nedc_convert_labels -tse -ext tse -rdir $p -odir $p lblt.list
find . -name "*.lblt" | xargs rm

#----------------------------------------------------------------------#
# rec_bi > lbl_bi
## change montage lists to point to rec_bi files
sed -i 's/rect$/rec_bi/' 01.list
sed -i 's/rect$/rec_bi/' 02.list
sed -i 's/rect$/rec_bi/' 03.list
## run nedc_rec_to_lbl on each montage list
nedc_rec_to_lbl -map $bi_map -montage $ref_map -rdir $p -odir $p 01.list
nedc_rec_to_lbl -map $bi_map -montage $le_map -rdir $p -odir $p 02.list
nedc_rec_to_lbl -map $bi_map -montage $ref_a_map -rdir $p -odir $p 03.list
## rename lbl flies to lbl_bi
find . -name "*.lbl" -exec rename lbl lbl_bi '{}' +

#----------------------------------------------------------------------#
# rec > lbl 
## change montage list to point to rec files
sed -i 's/rec_bi$/rec/' 01.list
sed -i 's/rec_bi$/rec/' 02.list
sed -i 's/rec_bi$/rec/' 03.list
## run nedc_rec_to_lbl on each montage list
nedc_rec_to_lbl -map $full_map -montage $ref_map -rdir $p -odir $p 01.list
nedc_rec_to_lbl -map $full_map -montage $le_map -rdir $p -odir $p 02.list
nedc_rec_to_lbl -map $full_map -montage $ref_a_map -rdir $p -odir $p 03.list

#----------------------------------------------------------------------#
rm 01.list 02.list 03.list lblt_bi.list lblt.list
# end
