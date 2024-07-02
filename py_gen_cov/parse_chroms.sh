#!/bin/bash

### Script to parse out the chromosome names from the reference names ###

# Check for the input
display_help() {
    echo ""
    echo "USAGE: $0 [OPTIONS]"
    echo ""
    echo "OPTIONS"
    echo "  -h, --help"
    echo "      display these options"
    echo "  -b, --bed"
    echo "      Input file"
    echo ""
    echo "EXAMPLE"
    echo "  $0 -b input bed"
    echo ""
    exit
}

if [[ -z "${1}" ]]
then
	echo "Please provide an input"
	display_help
	exit 1
fi

# Set up a quick parser
while [ "$#" -gt 0 ]
do
    ARGUMENTS="$1"
    case $ARGUMENTS in
        -h|--help)
			display_help
			exit 0
			shift
			;;
        -b|--bed)
			echo 
			BED="$2"
			shift 2
			;;
		*)
            echo "Unknown argument: $ARGUMENTS"
            display_help
            exit 1
            ;;
    esac
done

printf "Processing '${BED}' by editing in-place ... "

awk '/chromosome=/ {
    for(i=1;i<=NF;i++) {
        if ($i ~ /chromosome=\w+/) {
            split($i, a, "=")
            chr_num = a[5]
        }
    }
    print $1, chr_num
}' $BED | awk -F ";" '{print $1}' > ./chrom_ids.txt


cat ./chrom_ids.txt | while read line
do
    i=$(echo $line | awk '{print $1}')
    n=$(echo $line | awk '{print $2}')
    sed -i "s/${i}/${n}/g" $BED
done

rm -f ./chrom_ids.txt

echo "completed"
