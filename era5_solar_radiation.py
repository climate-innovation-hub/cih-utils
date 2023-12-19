"""Command line program for pre-processing ERA5 solar radiation."""

import argparse

import numpy as np
import xarray as xr
import xcdat
import xesmf as xe
import cmdline_provenance as cmdprov


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


def joules_to_watts(da):
    """Convert from Joules to Watts"""

    input_units = da.attrs["units"]
    input_freq = xr.infer_freq(da.indexes['time'][0:3])[0]
    assert input_freq == 'D'

    seconds_in_day = 60 * 60 * 24
    with xr.set_options(keep_attrs=True):
        da = da / seconds_in_day
    da.attrs['units'] = da.attrs['units'].replace('J', 'W')

    return da


def main(args):
    """Run the program."""

    ds_in = xcdat.open_mfdataset(args.radiation_files)
    ds_in = ds_in.rename({'latitude': 'lat', 'longitude': 'lon'})
    ds_in = ds_in.sel({'lat': slice(-9, -45), 'lon': slice(111, 157)})

    ds_out = regrid_to_agcd(ds_in, args.var)
    ds_out = ds_out.resample(time='D').mean('time', keep_attrs=True)
    ds_out[args.var] = joules_to_watts(ds_out[args.var])
    ds_out.attrs['history'] = cmdprov.new_log()
    ds_out.to_netcdf(
        args.outfile,
        encoding={args.var: {'least_significant_digit': 2, 'zlib': True}}
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )     
    parser.add_argument(
        "radiation_files",
        nargs='*',
        type=str,
        help="input solar radiation files (hourly time frequency)"
    )
    parser.add_argument(
        "var",
        choices=('ssrd', 'ssrdc'),
        type=str,
        help="input variable"
    )
    parser.add_argument(
        "outfile",
        type=str,
        help="output file name"
    )
    args = parser.parse_args()
    main(args)
