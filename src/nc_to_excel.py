import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
from mask import polygon_to_mask
from namelist import *

# silence the warning note
import warnings
warnings.filterwarnings("ignore")

def nc_to_df(varlist, input_ds, level, mask_da, dfout):
    """
    Convert netcdf data to pandas dataframe
    """
    for var in varlist:
        if var == 'QV':
            inputvar = input_ds[var].sel(level=level,method='nearest').squeeze()
            inputmask = inputvar.where(mask_da)
            output = inputmask.mean(dim=('x','y'),skipna=True)
            dfout[var] = output.values*1000
        else:
            inputvar = input_ds[var].sel(level=level,method='nearest').squeeze()
            inputmask = inputvar.where(mask_da)
            output = inputmask.mean(dim=('x','y'),skipna=True)
            dfout[var] = output.values
        # print(f'Complete {var}')
        
    return None


def write_to_excel(year, month, level, region,
                   mcip_varlist, chem_varlist,):
    
    if month == 'Sep':
        start_date = f'{year}-09-01T00'
        end_date   = f'{year}-09-30T23'
    elif month == 'Jul':
        start_date = f'{year}-07-01T00'
        end_date   = f'{year}-07-31T23'
    
    dfout = pd.DataFrame(
        index=pd.date_range(
            start=start_date, end=end_date, freq='H'
        )
    )
    
    print(f'Processing data in {month}, {year}')
    
    mcip = xr.open_dataset(datadir + f'processed/{month}_{year}/{month}_{year}_mcip.nc')
    chem = xr.open_dataset(datadir + f'processed/{month}_{year}/{month}_{year}_chem.nc')
    
    shp = gpd.read_file(shp_files[f'{region}_adm'])
    lon = chem.longitude
    lat = chem.latitude
    mask    = polygon_to_mask(shp.geometry[0], lon, lat)
    mask_da = xr.DataArray(mask, dims=('y','x'))
    
    nc_to_df(mcip_varlist,mcip,level,mask_da,dfout)
    nc_to_df(chem_varlist,chem,level,mask_da,dfout)
    
    outputpath = datadir + 'Contribution/data/'
    dfout.to_excel(outputpath + f'SIM_{region}_{month}_{year}.xlsx',index=True)
    
    return None

def write_obs_to_excel(year, month, city, city_en, varlist):
    
    if month == 'Sep':
        start_date = f'{year}-09-01T00'
        end_date   = f'{year}-09-30T23'
    elif month == 'Jul':
        start_date = f'{year}-07-01T00'
        end_date   = f'{year}-07-31T23'
    
    dfout = pd.DataFrame(
        index=pd.date_range(
            start=start_date, end=end_date, freq='H'
        )
    )
    print(f'Processing data in {month}, {year}')
    
    sitelocation = pd.read_excel(obs_dir + 'sitelocation.xlsx')
    site_group = sitelocation.groupby('城市')
    city_site = {}
    for group in site_group.groups:
        city_site[group] = site_group.get_group(group)['监测点编码'].values
    
    for var in varlist:
        df = pd.read_excel(obsSep + f'site_{var}_{year}.xlsx',index_col=0)
        citymean = df[city_site[city]].mean(axis=1,skipna=True)
        dfout[var] = citymean.values
        print(f'Complete {var}')
        
    outputpath = datadir + 'Contribution/data/'
    dfout.to_excel(outputpath + f'OBS_{city_en}_{month}_{year}.xlsx',index=True)

    return None