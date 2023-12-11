"""Command line program for calculating ERA5 relative humidity."""

import argparse

import numpy as np
import xcdat
import metpy
import xesmf as xe
import cmdline_provenance as cmdprov


def hurs_from_dewpoint(da_temperature, da_dewpoint, outvar):
    """Calculate a daily relative humidity variable from hourly dew point temperature."""
    
    temperature = da_temperature.metpy.quantify()
    temperature = temperature.metpy.convert_units('degC')
    
    dewpoint = da_dewpoint.metpy.quantify()
    dewpoint = dewpoint.metpy.convert_units('degC')
    
    hurs = metpy.calc.relative_humidity_from_dewpoint(temperature, dewpoint)
    hurs = hurs.metpy.convert_units('percent')
    
    da_hurs = hurs.metpy.dequantify()

    if outvar == 'hurs':
        da_hurs = da_hurs.resample(time='D').mean('time', keep_attrs=True)
        da_hurs.attrs['long_name'] = 'Near-Surface Relative Humidity'
    elif outvar == 'hursmax':
        da_hurs = da_hurs.resample(time='D').max('time', keep_attrs=True)
        da_hurs.attrs['long_name'] = 'Daily Maximum Near-Surface Relative Humidity'
    elif outvar == 'hursmin':
        da_hurs = da_hurs.resample(time='D').min('time', keep_attrs=True)
        da_hurs.attrs['long_name'] = 'Daily Minimum Near-Surface Relative Humidity'

    da_hurs.name = outvar
    da_hurs.attrs['standard_name'] = 'relative_humidity'
    da_hurs.attrs['units'] = '%' 
    
    ds_hurs = da_hurs.to_dataset()
    ds_hurs['time'].attrs['long_name'] = 'time'
    ds_hurs['time'].attrs['standard_name'] = 'time'
    
    return ds_hurs


def regrid_to_agcd(input_ds, var):
    """Regrid to the AGCD grid"""
    
    lats = np.round(np.arange(-44.5, -9.99, 0.05), decimals=2)
    lons = np.round(np.arange(112, 156.26, 0.05), decimals=2)
    agcd_grid = xcdat.create_grid(lats, lons)
    
    output_ds = input_ds.regridder.horizontal(
        var,
        agcd_grid,
        tool='xesmf',
        method='bilinear'
    )
    output_ds['lat'].attrs['long_name'] = 'Latitude'
    output_ds['lat'].attrs['standard_name'] = 'latitude'
    output_ds['lon'].attrs['long_name'] = 'Longitude'
    output_ds['lon'].attrs['standard_name'] = 'longitude'
    
    return output_ds


def main(args):
    """Run the program."""

    ds_temperature = xcdat.open_mfdataset(args.temperature_files)
    ds_temperature = ds_temperature.rename({'latitude': 'lat', 'longitude': 'lon'})
    ds_temperature = ds_temperature.sel({'lat': slice(-9, -45), 'lon': slice(111, 157)})

    ds_dewpoint = xcdat.open_mfdataset(args.dewpoint_files)
    ds_dewpoint = ds_dewpoint.rename({'latitude': 'lat', 'longitude': 'lon'})
    ds_dewpoint = ds_dewpoint.sel({'lat': slice(-9, -45), 'lon': slice(111, 157)})

    ds_rh = hurs_from_dewpoint(ds_temperature['t2m'], ds_dewpoint['d2m'], args.outvar)
    ds_rh = regrid_to_agcd(ds_rh, args.outvar)

    ds_rh.attrs['history'] = cmdprov.new_log()
    ds_rh.to_netcdf(
        args.outfile,
#        encoding={args.outvar: {'least_significant_digit': 2, 'zlib': True}}
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )     
    parser.add_argument(
        "outvar",
        choices=('hurs', 'hursmax', 'hursmin'),
        type=str,
        help="output variable"
    )
    parser.add_argument(
        "outfile",
        type=str,
        help="output file name"
    )
    parser.add_argument(
        "--temperature_files",
        nargs='*',
        type=str,
        help="input temperature files (hourly time frequency)"
    )
    parser.add_argument(
        "--dewpoint_files",
        nargs='*',
        type=str,
        help="input dewpoint temperature files (hourly time frequency)"
    )
    args = parser.parse_args()
    main(args)
