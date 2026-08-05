#!/bin/bash

# URL for the S&P 500 CSV
URL="https://raw.githubusercontent.com/datasets/s-and-p-500-companies/refs/heads/main/data/constituents.csv"

# Fetch and parse the CSV
# Using FPAT to correctly handle commas inside quotes (like in the Headquarters column)
curl -sL "$URL" | awk -v FPAT='([^,]*)|("[^"]*")' '
NR > 1 {
    # Founded year is column 8
    if (match($8, /[0-9]{4}/)) {
        year = substr($8, RSTART, 4)
        name = $2
        hq = $5
        
        # clean up quotes
        gsub(/"/, "", name)
        gsub(/"/, "", hq)
        
        printf "%s|%s|%s\n", year, name, hq
    }
}' | sort -n | awk -F'|' '
BEGIN {
    printf "%-8s %-40s %s\n", "Founded", "Company Name", "Headquarters"
}
{
    printf "%-8s %-40s %s\n", $1, $2, $3
}'
