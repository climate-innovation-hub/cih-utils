#!/bin/bash
#
# Description: Calculate ERA5 relative humidity
#             

function usage {
    echo "USAGE: bash $0 var"
    echo "   var: Can be hurs, hursmax or hursmin"
    exit 1
}

outvar=$1
python=/g/data/xv83/dbi599/miniconda3/envs/npcp/bin/python

for year in $(seq 1940 2022); do
    t2m_files=(/g/data/rt52/era5/single-levels/reanalysis/2t/${year}/*.nc)
    d2m_files=(/g/data/rt52/era5/single-levels/reanalysis/2d/${year}/*.nc)
    outfile=/g/data/wp00/users/dbi599/observations/ERA5/hurs/daily/${outvar}_ERA-5_day_aus0.05_${year}.nc
    command="${python} era5_relative_humidity.py ${outvar} ${outfile} --temperature_files ${t2m_files[@]} --dewpoint_files ${d2m_files[@]}"
    echo ${command}
    #${command}
done
