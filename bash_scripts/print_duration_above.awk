# awk script to return every annotation descibing a seizure event above and
# below certain limits (in seconds) and with a certain annotation label
# usage:
# single file:
      # awk -f print_duration_above.awk example.txt
             # add variable assignments before example.txt
#directory:
      # find . -name "*.extension" -exec awk -f print_duration_above.awk {} +
             # add variable assignments before {}
#----------------------------------------------------------------

BEGIN {
    
    lower=0; # print all seizures equal to or above ()seconds
    upper=1000000000000000000000000; # print all equal to or below ()seconds
    label=7; # print all seizures with this label
    # channel=$* #add in option to search for a specific channel. defualt 
    # variable should be??

    FS=","} 
{if (($ 4== label) && ($3-$2 >= lower) && ($3-$2 <= upper)) 
		     
	print "(" $1","$2","$3","$4 ") " $3-$2 " :"FILENAME}


#--------------------------------------------------------------------
# to count events: send output to results.txt
   # grep "^(21" | wc
