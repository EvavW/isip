# single file:
      # awk -f view_annotation.ask example.txt
             # add variable assignments before example.txt

BEGIN {
    FS=","
    start_sec=($2-start_min);
    end_min=$3/60;
    end=($3-end_min);

    } 
{print $1","int(int($2)/60)":"int($2-60*(int($2/60)))","int(int($3)/60)":"int($3-60*(int($3/60)))","$4}
