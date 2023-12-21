#!/bin/bash
#
# Description: Pre-process ERA5 solar radiation
#             

function usage {
    echo "USAGE: bash $0 var"
    echo "   var: Can be ssrd ssrdc"
    exit 1
}

var=$1

for year in $(seq 1959 2022); do
    qsub -v year=${year},var=${var} era5_solar_radiation-job.sh
done
