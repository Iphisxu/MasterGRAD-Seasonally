import numpy as np
import xarray as xr
import shapely.geometry as sgeom
from shapely.prepared import prep

# silence the warning note
import warnings
warnings.filterwarnings("ignore")

def polygon_to_mask(polygon, x, y):
    '''
    Generate a mask array of points falling into the polygon
    
    Example:
    
    shp = gpd.read_file(shapefile)
    lon = ncfile.longitude
    lat = ncfile.latitude

    mask = polygon_to_mask(shp.geometry[0],lon,lat)
    mask_da = xr.DataArray(mask,dims=('y','x'))

    masked_data = data.where(mask_da)
    data_mean   = masked_data.mean(dim=['y','x'],skipna=True)
    '''
    x = np.atleast_1d(x)
    y = np.atleast_1d(y)
    mask = np.zeros(x.shape, dtype=bool)

    # if each point falls into a polygon, without boundaries
    prepared = prep(polygon)
    for index in np.ndindex(x.shape):
        point = sgeom.Point(x[index], y[index])
        if prepared.contains(point):
            mask[index] = True

    return mask


def average_data(filelist, var, level=None):
    """
    This function takes a list of file names and a variable name as input,
    reads the data from each file, computes an average over all files, and returns
    an xarray DataArray with the averaged data.
    
    Parameters
    ----------
    filelist : list of str
        List of file names to read.
        
    var : str
        Name of the variable to extract from the datasets.
        
    level : num
        Barometric altitude to select. Default None set to 1000hPa.
        
    Returns
    -------
    avg_data : xarray.DataArray
        Averaged data as an xarray DataArray.
    """
    select_data = []
    for file in filelist:
        ds = xr.open_dataset(file)
        if level is not None:
            data = ds[var].sel(level=level, method='nearest')
        else:
            data = ds[var][:,0,:,:] # Ground level
        select_data.append(data)
        ds.close()
    
    #// combined = xr.concat(select_data, dim='data_array')
    #// averaged = combined.mean(dim='data_array')

    averaged = (select_data[0].values 
                + select_data[1].values 
                + select_data[2].values) / 3
    
    avg_data = xr.DataArray(
        averaged,
        dims=data.dims,
        coords=data.coords,
        name=var
    )
    return avg_data