
sequeunce of running codes in order to get files correctly

	  - Use sed on all the files to remove line retrun '\r' character.	  
	  - First, All the annotations should be sorted properly, seizure events should start from 0 to end ( not randomly in
	    	time-scale )
	  - Remove all the unnecessary files like low confiently annotated files, tiny files, unpruned ones from the list.
	  - First create a rec files' list for absolute location
	  - run remove_backgrounds.py on them -> which will convert annotation in .2 decimal point precision 
	    	and will remove all the backgrounds (6 after last delimiter)
	  - Run script called find_seiz_start_time_and_replace_with_1_sec_if_lessthan_zero.py from directory 
	    	"correction_for_seiz_start_less_than_one_sec/"
	    	to correct all the annotation which actually starts before 1 second. This script will convert them, starting 
		from 1st second.
	  - Use comman_seiz_class_make.py to convert multiclass seizure file to bi-class seizure file (for Meysam's Experiment)
	    	Commnet all the write and move options from the script first to first confirm that all files are valid.
		(Few bad files were observed without class number at the end of rec file, also with the name "None" sometimes)
	  - run script find_rec_files_with_problem.py (at /data/isip/exp/tuh_eeg/exp_0667/) now this script has been moved
	      	and find out the annotation to this current location
	        files which starts with 0 seconds for seizure. Change it to something like 0.3 or 0.6..
		This should be done on same rec_files' list defined above.
	  - run numpy_full_annot_solution.py on the very same list of rec files -> This will provide you continues 
	    	annotation for seizure and background but this annotation could have repeatative annotation
		i.e. start time and stop time to be the same
	  - Again run the find_rec_files_with_problems and fix them.
	  - run bash (emacs.list) which should be rec file list for sorting purpose. modify it according to the emacs.list
	  - finally run correct_repeatation.py on the very same list to correc the annotation.
	  - Eventually sort and uniq every single entry to avoid repeatation and again run emacs.list for better observation
	    	(emacs.list not necessary though)
	  - Finally, run the script called crosscheck_rec_after_processing.py to confirm there is no problem in rec files at all.
