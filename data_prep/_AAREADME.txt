file: _AAREADME.txt
desc: instructions on using scripts in this directory to prepare seizure and
      other annotations for release and for use in experiments

notes: "version" will be used to refer to the TUSZ version on which you are 
       currently working. this should correspond to a folder at $WORK/version

       your working directory should always be work/version/data_prep. you
       should not be working in work/version/ since this will put raw source
       annotations in jeopardy       		 

       the term "$p" will be used to represent your working directory

       scripts in this directory will be refered to by the name of the 
	file only, i.e. get_list.py for simplicity

       the term "filename path" will refer to part of a file path that 
       	   does not depend on filetype or version number. example:
	   	03_tcp_ar_a/091/00009162/s002_2012_04_09/00009162_s002_t000

       the $WORK variables refers to /data/isip/data/tuh_eeg_seizure/work
       	   it will be referd to simply as "work"
#------------------------------------------------------------------------------#

1. resolve database with spreadsheet:
   	   make sure that the rec files match the annotation spreadsheets
	   the same number of files should be present, same number of files 
	   with seizures, etc.

2. resolve database with tuh_eeg:
   	   make sure that all files are in the correct naming conventions 
	   check that all files have an associated edf file in tuh eeg v1.1.1
	   check for repeats

3. copy rec files from raw_source_annotation into a new data_prep directory:
   	raw_source_annotation files should never have scripts run on them
      	a copy of these files must always be kept safe

4. copy edf files associated with this release to a temporary location:
   	get a list of edf files by getting a list of rec files:
	    find . -name "*.rec" >  edf.list
	and then editing the path in emacs/awk:
	    create a list of commands that copied edf files in tuh eeg v1.1.1 
	    into work/version/edf in a directory structure compatible with 
	    work/version/data_prep:

	    cp /data/isip/data/tuh_eeg/v1.1.1/edf/"filename path" ./work ...
	    /version/edf/"set name + filename path"

5. create lists for use in data prep:
   	  a list of rec files:
	    find `p` -name "*.rec" > rec.list

	  a list of edf files:
	    python get_list.py -rdir ...work/version/data_prep 
	    -odir ...work/version/edf -ext edf rec.list > edf.list
	    * be sure to use check_exist.sh on edf.list to be sure
	    
6. quantize rec:
   	    make sure that the level of precision of each rec files is 
	    consistent with the sampling frequency of the edf file:
	    	       python work/_TOOLS/quantize_rec/quantize_rec.py -rdir
		       $p -odir $p edf.list rec.list
		       	  * note that edf list is passed before rec list

7. remove windows new line characters from the rec files:
   	  cat rec.list | xargs sed -i 's/\r//'

8. remove bckg,intr, and any other non seizure annotations:
   	  python remove_label.py -rdir $p -odir $p -ext rec -label 6 rec.list
	  python remove_label.py -rdir $p -odir $p -ext rec -label 19 rec.list
   	  
9. check rec files:
   	 bash check_rec.sh rec.list edf.list
	 	errors in the first and last second will be fixed by
		full_ann.py you should keep a list of these files so you can
		check later that the errors have been fixed
		
		repeat annotations can be fixed using sort | uniq:
		       cat error.rec | sort | uniq > temp
		       mv temp error.rec

		overlap errors should be investigated individually

10. create rec derivations:
   	  bash prep_rec.sh rec.list edf.list
	       this will create rec_bi, rect, and rect_bi files
	       
	       annotations in the first and last second will be snapped to 
	       1.0000 and duration-1.0000 respectively 

11. manual check:
   	  check that all rec derivations have been created for all files
	  
	  check several files to make sure that all derivations are correct

	  check that rec.list and edf.list are intact and correct

12. create lab files:
   	  * lab is a legacy format that will become completeley obsolete in 
	  the near future

	  bash rec_to_lab.sh rec.list
	       this will create lab,lab_bi,labt,labt_bi,lab_ov,lab_biov
	       ,labt_ovt, and labt_biovt files for old experiments

13. create lbl and tse files:
    	   bash rec_to_tse.sh rec.list
	   	will create lbl, lbl_bi, tse, tse_bi which for the release
		will create channel based tse and tse_bi files for experiments

14. manual check:
    	   check that all lab,lbl,and tse derivations have been created for 
	   all files

	   check several for correctness

15. get a list of tse files:
    	to ensure that the existing edf.list and the new tse.list are in the 
	same order:
	     cp rec.list tse.list
	     
	     sed -i 's/rec/tse/' tse.list

16. check tse files:
    	  bash check_tse.sh tse.list edf.list
	       any errors at this step are serious and may require restaring
	       this process

17. check channel based tse files:
    	  get a list of channel based tse files:
	      find `p` -name "*ch*tse" > chtse.list
	  
	  get a list of associated edf files:
	      python get_list.py -rdir ...work/version/data_prep/ -odir
	      ...work/version/edf/ -ext edf chtse.list > chedf.list
	  
	  bash check_tse.sh chtse.list chedf.list
	  	 again any errors at this step represent a serious error in
		 the data prep process

18. generate statistics:
    	     bash gen_stats.sh tse.list
	     	    use overall tse files not channel based tse files
		    
		    these numbers should be included in the release README

19. generate the spreadsheet:
    	     separate the tse.list by set (dev_test, train, eval):
	     	      grep train tse.list > train.list

    	     python gen_sheet.py -info session_info.csv train.list
	     	    run for each set

		    paste output into existing _SEIZURES set

		    adjust ranges in sum cells on _SEIZURES

		    compare sums to output of gen_stats.sh
