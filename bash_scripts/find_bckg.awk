
#used by a the bash script remove_bckg.
#prints all non-background annotations in a file

BEGIN {

    FS="," } { if ($4 != 6) print $1","$2","$3","$4 } 
