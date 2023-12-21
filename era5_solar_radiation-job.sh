#!/bin/bash
#PBS -P xv83
#PBS -q normal
#PBS -l walltime=1:00:00
#PBS -l mem=5GB
#PBS -l storage=gdata/xv83+gdata/rt52+gdata/wp00
#PBS -l wd
#PBS -v var,year
#
__conda_setup="$('/g/data/xv83/dbi599/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/g/data/xv83/dbi599/miniconda3/etc/profile.d/conda.sh" ]; then
        . "/g/data/xv83/dbi599/miniconda3/etc/profile.d/conda.sh"
    else
        export PATH="/g/data/xv83/dbi599/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup

conda activate npcp

python=/g/data/xv83/dbi599/miniconda3/envs/npcp/bin/python
infiles=(/g/data/rt52/era5/single-levels/reanalysis/${var}/${year}/*.nc)
outfile=/g/data/wp00/data/observations/ERA5/${var}/daily/${var}_ERA-5_day_aus0.05_${year}.nc
command="${python} /home/599/dbi599/cih-utils/era5_solar_radiation.py ${infiles[@]} ${var} ${outfile}"
echo ${command}
${command}


