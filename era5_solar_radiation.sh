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
python=/g/data/xv83/dbi599/miniconda3/envs/npcp/bin/python

for year in $(seq 1959 2022); do
    infiles=(/g/data/rt52/era5/single-levels/reanalysis/${var}/${year}/*.nc)
    outfile=/g/data/wp00/data/observations/ERA5/${var}/daily/${var}_ERA-5_day_aus0.05_${year}.nc
    command="${python} era5_solar_radiation.py ${infiles[@]} ${var} ${outfile}"
    echo ${command}
    ${command}
done
