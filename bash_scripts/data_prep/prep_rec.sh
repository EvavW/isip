#!/usr/bin/sh

# prep_rec 
## Eva von Weltin
### this script takes raw .rec files and generates full annotated rec_bi, rect,
### and rect_bi files

#usage : 
## bash prep_rec.sh rec.list edf.list (should be a list of .rec files and corresponding .edf files)

reclist=$1
p=`pwd`
#----------------------------------------------------------------------#
#declare variables for utility script names/locations
rm_bckg="/data/isip/data/tuh_eeg_seizure/work/_TOOLS/bash_scripts/remove_bckg.sh"
corr_repeat="/data/isip/data/tuh_eeg_seizure/work/_TOOLS/data_prep/correct_repeats.py"
find_prob="/data/isip/data/tuh_eeg_seizure/work/_TOOLS/data_prep/find_rec_files_with_problems.py"
fix_first="/data/isip/data/tuh_eeg_seizure/work/_TOOLS/data_prep/fix_first_second.py"
make_bi="/data/isip/data/tuh_eeg_seizure/work/_TOOLS/data_prep/make_biclass.py"
rec_to_rect="/data/isip/data/tuh_eeg_seizure/work/_TOOLS/data_prep/rec_to_rect.py"
full_anno="/data/isip/data/tuh_eeg_seizure/work/_TOOLS/data_prep/full_annotation.py"
quant="/data/isip/data/tuh_eeg_seizure/work/_TOOLS/quantize_rec/quantize_rec.py"

#----------------------------------------------------------------------#
#clean up rec files and check+fix errors
bash $rm_bckg $reclist
python $corr_repeat $reclist
python $find_prob $reclist
python $fix_first $reclist

#----------------------------------------------------------------------#
# sort rec files and copy them into rec_bi files
while read line; do
    
    sed -i 's/\r//' $line
    sort -t"," -k1n,1 -k2n,2 $line -o $line
    new=`echo $line | awk '{print $1"_bi"}'`
    cp $line $new

done <$reclist

#----------------------------------------------------------------------#
# make rec_bi files biclass
find . -name "*.rec_bi" > rec_bi.list
python $make_bi rec_bi.list

#----------------------------------------------------------------------#
#create rect and rect_bi files
find . -name "*.rec" > make_term.list
find . -name "*.rec_bi" >>make_term.list
python $rec_to_rect make_term.list

#----------------------------------------------------------------------#
#generate full annotations for all files
find . -name "*.rec*" > make_full.list
python $full_anno make_full.list

#----------------------------------------------------------------------#
# sort files
while read line; do
    
    sort -t"," -k1n,1 -k2n,2 $line -o $line

done <make_full.list

#----------------------------------------------------------------------#
rm make_term.list make_full.list rec_bi.list _file_problems.list tmp.x tmp.xx
#end
