#!/usr/bin/sh

## collect the first argument after script name
#
rec=$1 #all files
sesh_info=$2 #session info in csv format

sort -t"," -k1n,1 -k2n,2 $rec -o $rec

get_first=(`sed 's/_x//' $rec | awk '{print substr($1, 1, length($1)-23)}' | sort | uniq`)
files=(`awk '{print $1}' $rec`)
for i in "${get_first[@]}"; do

    first+=("`grep -m 1 $i $rec`")

done

for i in "${files[@]}"; do
    
    seiz_per_file+=("`grep "^0," $i | grep -cv ",6$"`")

done 

for sesh in "${get_first[@]}"; do
    num_seiz="0"
    i="0"
    for file in "${files[@]}"; do
	
	check=`echo $file | sed 's/_x//' | awk '{print substr($1, 1, length($1)-23)}'`
	if [[ "$sesh" == "$check" ]]; then
	    
	    let "num_seiz+=${seiz_per_file[$i]}"
	
	fi
	let "i++"	
    done
    seiz_per_sesh+=("`echo $num_seiz`")
done

containsFile () {
    local e match="$1"
    shift
    for e; do [[ "$e" == "$match" ]] && return 1; done
    return 0
}

file_number="1"
while read line; do
    containsFile "$line" "${first[@]}"
    if [[ "$?" != "0" ]]; then
	this_seiz_file=`grep "^0," $line | grep -cv ",6$"`
	ident=`echo $line | sed 's/_a//' | awk 'BEGIN {FS="_"} {print substr($5,4,length($5))","$6}'`
	file=`echo $line | sed 's/_a//' | awk 'BEGIN {FS="_"} {print substr($7,1,4)}'`
	i="0"
	for sesh in "${get_first[@]}"; do
	    check=`echo $sesh | sed 's/_a//' | awk 'BEGIN {FS="/"} {print $4","substr($5,1,4)}'`
	    if [[ "$ident" == "$check" ]]; then
		this_seiz_sesh=`echo ${seiz_per_sesh["$i"]}`
	    fi
	    let "i++"
	done
	if [[ "$this_seiz_file" != "0" ]];then
	    while read anno; do
		

	    done <$line
	fi
    fi
    let "file_number++"
done <$rec # feed in the filelist from here...

