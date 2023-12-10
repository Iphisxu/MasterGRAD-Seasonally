import xarray as xr
import numpy as np
import pandas as pd

import sys
sys.path.append('../../src/')
from namelist import *

def process_mcip(year, month):
    # set time range
    STR = get_STR(year,month)
    END = get_END(year,month)
    times=pd.date_range(STR,END,freq='h')
    print('Processing MCIP for [ ' + month + ', ' + str(year) + ' ]')

    grid = xr.open_dataset('D:/Data/Graduation/GRID/GRIDCRO2D_D03.nc')
    mcip = xr.open_dataset(f'D:/Data/Graduation/COMBINE/{month}/COMBINE_ACONC_CN3GD_152X110_{year}_noAPM_mcip.nc')
    wind = xr.open_dataset(f'D:/Data/Graduation/COMBINE/{month}/COMBINE_ACONC_CN3GD_152X110_{year}_wind.nc')

    # convert layer to pressure
    preslevel=np.array(
        [1.,     0.9979, 0.9956, 0.9931, 0.9904, 0.9875, 0.9844, 0.9807, 0.9763, 0.9711,
            0.9649, 0.9575, 0.9488, 0.9385, 0.9263, 0.912,  0.8951, 0.8753, 0.8521, 0.8251,
            0.7937, 0.7597, 0.7229, 0.6883, 0.641,  0.596,  0.5484, 0.4985, 0.4467, 0.3934,
            0.3393, 0.285,  0.2316, 0.1801, 0.1324, 0.0903, 0.0542, 0.0241,]
        )
    pres = preslevel*950+50
    
    print('Calculating RH ...')

    # calculate saturation vapor pressure (es)
    es = 6.112 * np.exp((17.67 * mcip.AIR_TMP) / (mcip.AIR_TMP + 243.5))
    # calculate vapor pressure (e)
    e = mcip.PRES * mcip.QV / (0.622 + 0.378 * mcip.QV)
    # calculate relative humidity (RH)
    RH = e / es * 100

    print('Creating dataset ...')

    days=1 # set spin-up days
    dataset=xr.Dataset(
        data_vars=dict(
            # ! vars from mcip
            QV=(['time','level','y','x'],mcip.QV[days*24-8:-8-1,:21,:,:].data,{'long name':'Water Vapor Mixing Ratio','units':'kg kg-1'}),
            RH=(['time','level','y','x'],RH[days*24-8:-8-1,:21,:,:].data,{'long name':'Relative Humidity on Surface','units':'%'}),
            SFC_TMP=(['time','level','y','x'],mcip.SFC_TMP[days*24-8:-8-1,:21,:,:].data,{'long name':'Surface Temperature','units':'deg C'}),
            AIR_TMP=(['time','level','y','x'],mcip.AIR_TMP[days*24-8:-8-1,:21,:,:].data,{'long name':'Air Temperature','units':'deg C'}),
            PBLH=(['time','level','y','x'],mcip.PBLH[days*24-8:-8-1,:21,:,:].data,{'long name':'Planet Boundary Layer Height','units':'m'}),
            SOL_RAD=(['time','level','y','x'],mcip.SOL_RAD[days*24-8:-8-1,:21,:,:].data,{'long name':'Solar Radiation','units':'W m-2'}),
            PRES=(['time','level','y','x'],mcip.PRES[days*24-8:-8-1,:21,:,:].data,{'long name':'Air Pressure','units':'hPa'}),
            precip=(['time','level','y','x'],mcip.precip[days*24-8:-8-1,:21,:,:].data,{'long name':'Precipitation','units':'cm'}),
            WSPD10=(['time','level','y','x'],mcip.WSPD10[days*24-8:-8-1,:21,:,:].data,{'long name':'Wind Speed 10m','units':'m s-1'}),
            WDIR10=(['time','level','y','x'],mcip.WDIR10[days*24-8:-8-1,:21,:,:].data,{'long name':'Wind Direction','units':'deg'}),
            CloudFRAC=(['time','level','y','x'],mcip.CloudFRAC[days*24-8:-8-1,:21,:,:].data,{'long name':'Cloud Fraction','units':'1'}),
            # ! vars from wind
            uwind=(['time','level','y','x'],wind.UWind[days*24-8:-8-1,:21,:-1,:-1].data,{'long name':'U-direction Horizontal Wind Speed','units':'m s-1'}),
            vwind=(['time','level','y','x'],wind.VWind[days*24-8:-8-1,:21,:-1,:-1].data,{'long name':'V-direction Horizontal Wind Speed','units':'m s-1'}),
        ),
        coords=dict(
            time=times,
            level=pres[:21],
            latitude=(['y','x'],grid.LAT[0,0,:,:].data),
            longitude=(['y','x'],grid.LON[0,0,:,:].data),
        ),
        attrs=dict(
            name=f'GRAD_{month}_{year}',
            grid='CN3GD_152X110',
            createtime=pd.Timestamp.now().strftime('%Y-%m-%d'),
        ),
    )

    print('Export compressed file ...')
    
    compression=dict(zlib=True,complevel=5)
    encoding={var:compression for var in dataset.data_vars}
    dataset.to_netcdf(datadir + f'processed/{month}_{year}/{month}_{year}_mcip.nc',encoding=encoding)
    
    print('Completed!')
    print('==========')
    
    grid.close()
    mcip.close()
    wind.close()
    dataset = None
    
def process_chem(year, month):
    # set time range
    STR = get_STR(year,month)
    END = get_END(year,month)
    times=pd.date_range(STR,END,freq='h')
    print('Processing CMAQ for [ ' + month + ', ' + str(year) + ' ]')

    grid = xr.open_dataset('D:/Data/Graduation/GRID/GRIDCRO2D_D03.nc')
    chem = xr.open_dataset(f'D:/Data/Graduation/COMBINE/{month}/COMBINE_ACONC_CN3GD_152X110_{year}_chem.nc')

    # convert layer to pressure
    preslevel=np.array(
        [1.,     0.9979, 0.9956, 0.9931, 0.9904, 0.9875, 0.9844, 0.9807, 0.9763, 0.9711,
            0.9649, 0.9575, 0.9488, 0.9385, 0.9263, 0.912,  0.8951, 0.8753, 0.8521, 0.8251,
            0.7937, 0.7597, 0.7229, 0.6883, 0.641,  0.596,  0.5484, 0.4985, 0.4467, 0.3934,
            0.3393, 0.285,  0.2316, 0.1801, 0.1324, 0.0903, 0.0542, 0.0241,]
        )
    pres = preslevel*950+50

    print('Calculating Height ...')
    
    ht=np.squeeze(grid.HT)
    height=np.zeros([np.size(chem.ZH,0),
                    np.size(chem.ZH,1),
                    np.size(chem.ZH,2),
                    np.size(chem.ZH,3)])
    for t in range(np.size(chem.ZH,0)):
        for l in range(np.size(chem.ZH,1)):
            height[t,l,:,:]=chem.ZH[t,l,:,:]+ht

    print('Creating dataset ...')

    days=1 # set spin-up days
    dataset=xr.Dataset(
        data_vars=dict(
            # ! vars from CMAQ
            O3=(['time','level','y','x'],chem.O3[days*24-8:-8,:21,:,:].data*48/22.4,{'long name':'Ozone','units':'ug m-3','molar mass':'48 g/mol'}),
            NO=(['time','level','y','x'],chem.NO[days*24-8:-8,:21,:,:].data*30/22.4,{'long name':'Nitric Oxide','units':'ug m-3','molar mass':'30 g/mol'}),
            NO2=(['time','level','y','x'],chem.NO2[days*24-8:-8,:21,:,:].data*46/22.4,{'long name':'Nitrogen Dioxide','units':'ug m-3','molar mass':'46 g/mol'}),
            VOC=(['time','level','y','x'],chem.VOC[days*24-8:-8,:21,:,:].data,{'long name':'Volitile Organic Compounds','units':'ppbV'}),
            PM25=(['time','level','y','x'],chem.PM25_TOT[days*24-8:-8,:21,:,:].data,{'long name':'','units':'ug m-3'}),
            ISOP=(['time','level','y','x'],chem.ISOP[days*24-8:-8,:21,:,:].data,{'long name':'','units':'ppbV','molar mass':'68 g/mol'}),
            # ! wwind
            wwind=(['time','level','y','x'],chem.WWind[days*24-8:-8,:21,:,:].data,{'long name':'Vertical Wind Speed','units':'m s-1'}),
            # ! altitude
            HT=(['time','level','y','x'],height[days*24-8:-8,:21,:,:].data,{'long name':'Altitudes','units':'m'}),
        ),
        coords=dict(
            time=times,
            level=pres[:21],
            latitude=(['y','x'],grid.LAT[0,0,:,:].data),
            longitude=(['y','x'],grid.LON[0,0,:,:].data),
        ),
        attrs=dict(
            name=f'GRAD_{month}_{year}',
            grid='CN3GD_152X110',
            createtime=pd.Timestamp.now().strftime('%Y-%m-%d'),
        ),
    )

    print('Export compressed file ...')
    
    compression=dict(zlib=True,complevel=5)
    encoding={var:compression for var in dataset.data_vars}
    dataset.to_netcdf(datadir + f'processed/{month}_{year}/{month}_{year}_chem.nc',encoding=encoding)
    
    print('Completed!')
    print('==========')
    
    grid.close()
    chem.close()
    dataset = None
    
def process_case_chem(case, year, month):
    
    if case == 1:
        scale = 'Annually'
    elif case == 2:
        scale = 'Seasonally'
        
    # set time range
    STR = get_STR(year,month)
    END = get_END(year,month)
    times=pd.date_range(STR,END,freq='h')
    print('Processing CMAQ for [ ' + scale + ', ' + month + ', ' + str(year) + ' ]')

    gridfile   = 'D:/Data/Graduation/GRID/GRIDCRO2D_D03.nc'
    inputfile  = f'D:/Data/Graduation/COMBINE/Case_{scale}/COMBINE_ACONC_CN3GD_152X110_{year}_chem.nc'
    outputfile = datadir + f'processed/{scale}_{month}_{year}/{month}_{year}_chem.nc'

    grid = xr.open_dataset(gridfile)
    chem = xr.open_dataset(inputfile)

    # convert layer to pressure
    preslevel=np.array(
        [1.,     0.9979, 0.9956, 0.9931, 0.9904, 0.9875, 0.9844, 0.9807, 0.9763, 0.9711,
            0.9649, 0.9575, 0.9488, 0.9385, 0.9263, 0.912,  0.8951, 0.8753, 0.8521, 0.8251,
            0.7937, 0.7597, 0.7229, 0.6883, 0.641,  0.596,  0.5484, 0.4985, 0.4467, 0.3934,
            0.3393, 0.285,  0.2316, 0.1801, 0.1324, 0.0903, 0.0542, 0.0241,]
        )
    pres = preslevel*950+50

    print('Calculating Height ...')
    
    ht=np.squeeze(grid.HT)
    height=np.zeros([np.size(chem.ZH,0),
                    np.size(chem.ZH,1),
                    np.size(chem.ZH,2),
                    np.size(chem.ZH,3)])
    for t in range(np.size(chem.ZH,0)):
        for l in range(np.size(chem.ZH,1)):
            height[t,l,:,:]=chem.ZH[t,l,:,:]+ht

    print('Creating dataset ...')

    days=1 # set spin-up days
    dataset=xr.Dataset(
        data_vars=dict(
            # ! vars from CMAQ
            O3=(['time','level','y','x'],chem.O3[days*24-8:-8,:21,:,:].data*48/22.4,{'long name':'Ozone','units':'ug m-3','molar mass':'48 g/mol'}),
            NO=(['time','level','y','x'],chem.NO[days*24-8:-8,:21,:,:].data*30/22.4,{'long name':'Nitric Oxide','units':'ug m-3','molar mass':'30 g/mol'}),
            NO2=(['time','level','y','x'],chem.NO2[days*24-8:-8,:21,:,:].data*46/22.4,{'long name':'Nitrogen Dioxide','units':'ug m-3','molar mass':'46 g/mol'}),
            VOC=(['time','level','y','x'],chem.VOC[days*24-8:-8,:21,:,:].data,{'long name':'Volitile Organic Compounds','units':'ppbV'}),
            PM25=(['time','level','y','x'],chem.PM25_TOT[days*24-8:-8,:21,:,:].data,{'long name':'','units':'ug m-3'}),
            ISOP=(['time','level','y','x'],chem.ISOP[days*24-8:-8,:21,:,:].data,{'long name':'','units':'ppbV','molar mass':'68 g/mol'}),
            # ! wwind
            wwind=(['time','level','y','x'],chem.WWind[days*24-8:-8,:21,:,:].data,{'long name':'Vertical Wind Speed','units':'m s-1'}),
            # ! altitude
            HT=(['time','level','y','x'],height[days*24-8:-8,:21,:,:].data,{'long name':'Altitudes','units':'m'}),
        ),
        coords=dict(
            time=times,
            level=pres[:21],
            latitude=(['y','x'],grid.LAT[0,0,:,:].data),
            longitude=(['y','x'],grid.LON[0,0,:,:].data),
        ),
        attrs=dict(
            name=f'GRAD-Case_{scale}-{month}_{year}',
            grid='CN3GD_152X110',
            createtime=pd.Timestamp.now().strftime('%Y-%m-%d'),
        ),
    )

    print('Export compressed file ...')
    
    compression=dict(zlib=True,complevel=5)
    encoding={var:compression for var in dataset.data_vars}
    dataset.to_netcdf(outputfile,encoding=encoding)
    
    print('Completed!')
    print('==========')
    
    grid.close()
    chem.close()
    dataset = None