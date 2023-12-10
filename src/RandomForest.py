import xarray as xr
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score


def read_data(years, month, region, datapath):
    df = {}

    for year in years:
        df[year] = pd.read_excel(datapath + f'SIM_{region}_{month}_{year}.xlsx', index_col=0)

    data = pd.concat(df, axis=0)
    data.reset_index(level=0, inplace=True)
    data.drop(columns='level_0', inplace=True)

    return data

def rf_importance(df, variants, target, random_state=42, test_size=0.2):
    # Splitting the data
    X = df[variants]
    y = df[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    # Creating and training the Random Forest Regressor model
    rf_model = RandomForestRegressor(n_estimators=100, random_state=random_state)
    rf_model.fit(X_train, y_train)

    # Predicting results
    y_pred_rf = rf_model.predict(X_test)

    # Mean Squared Error
    mse = mean_squared_error(y_test, y_pred_rf)
    # print(f'Mean Squared Error (Random Forest): {mse}')

    # R-squared
    r2 = r2_score(y_test, y_pred_rf)
    # print(f'R-squared (Random Forest): {r2}')

    # Getting feature importance
    feature_importance = rf_model.feature_importances_

    # add mse and r2
    output_index = variants + ['mse','r2']
    # Creating a DataFrame to store feature importance
    df_output = pd.DataFrame (
        index=output_index,
        columns=['value'],
    )
    
    df_output.loc['mse','value'] = mse
    df_output.loc['r2','value']  = r2
    
    # Matching feature importance with feature names
    for feature, importance in zip(variants, feature_importance):
        df_output.loc[feature, 'value'] = importance

    # Sorting feature importance in descending order
    # feature_importance_dict = dict(zip(variants, feature_importance))
    # sorted_feature_importance = sorted(feature_importance_dict.items(), key=lambda x: x[1], reverse=True)

    # Printing each variable's impact on O3
    # for feature, importance in sorted_feature_importance:
    #     print(f'{feature}: {importance}')

    return df_output


# ===========================================================
# Read NETCDF file, create dataframe
# ===========================================================

def read_ncdata(years, month, datapath):
    
    chemlist = [datapath + f'{month}_{year}/{month}_{year}_chem.nc' for year in years]
    mciplist = [datapath + f'{month}_{year}/{month}_{year}_mcip.nc' for year in years]

    dsmcip = xr.open_mfdataset(mciplist)
    dschem = xr.open_mfdataset(chemlist)

    return dsmcip, dschem

def create_dataframes(vars,ny,nx):
    dfs = {}
    for var in vars:
        dfs[var] = pd.DataFrame(
            index=range(ny),
            columns=range(nx)
        )
    return dfs

def write_nc_to_df(years, month, datapath, 
                   mcip_variants, chem_variants,
                   variants, target,
                   nx=None, ny=None):
    
    dsmcip, dschem = read_ncdata(years, month, datapath)
    if nx is None:
        nx = dsmcip.dims['x']
    if ny is None:
        ny = dsmcip.dims['y']
    print(f'nx = {nx}, ny = {ny}')
    minutes_to_use = nx*ny*8.146/60
    hours_to_use = nx*ny*8.146/3600
    print(f'The process is expected to take up to {minutes_to_use:.2f} min, or {hours_to_use:.2f} h')
    
    output_varlist = variants + ['mse','r2']
    dfs_dict = create_dataframes(output_varlist,110,152)
    
    for y in range(ny):
        for x in range(nx):
            
            process = (y*nx + x+1)/(ny*nx) *100
            
            df = pd.DataFrame(
                index=dschem.time.values,
                columns = mcip_variants + chem_variants
            )
            
            for mcip_var in mcip_variants:
                df[mcip_var] = dsmcip[mcip_var][:,0,y,x].squeeze().values
            for chem_var in chem_variants:
                df[chem_var] = dschem[chem_var][:,0,y,x].squeeze().values

            df_importance = rf_importance(df,variants,target)
            print(f'({x},{y}) --> {process:.2f} %')
            
            for var in output_varlist:
                dfs_dict[var].loc[y,x] = df_importance.loc[var].values[0]
                
    return dfs_dict

def write_ncdiff_to_df(years1, years2, month, datapath, 
                       mcip_variants, chem_variants,
                       variants, target,
                       nx=None, ny=None):
    
    dsmcip1, dschem1 = read_ncdata(years1, month, datapath)
    dsmcip2, dschem2 = read_ncdata(years2, month, datapath)
    if nx is None:
        nx = dsmcip1.dims['x']
    if ny is None:
        ny = dsmcip1.dims['y']
    print(f'nx = {nx}, ny = {ny}')
    minutes_to_use = nx*ny*13.51/60
    hours_to_use = nx*ny*13.51/3600
    print(f'The process is expected to take up to {minutes_to_use:.2f} min, or {hours_to_use:.2f} h')
    
    output_varlist = variants + ['mse','r2']
    dfs_dict = create_dataframes(output_varlist,110,152)
    
    for y in range(ny):
        for x in range(nx):
            
            process = (y*nx + x+1)/(ny*nx) *100
            
            df1 = pd.DataFrame(
                index=dschem1.time.values,
                columns = mcip_variants + chem_variants
            )
            df2 = pd.DataFrame(
                index=dschem1.time.values,
                columns = mcip_variants + chem_variants
            )
            
            for mcip_var in mcip_variants:
                df1[mcip_var] = dsmcip1[mcip_var][:,0,y,x].squeeze().values
                df2[mcip_var] = dsmcip2[mcip_var][:,0,y,x].squeeze().values
            for chem_var in chem_variants:
                df1[chem_var] = dschem1[chem_var][:,0,y,x].squeeze().values
                df2[chem_var] = dschem2[chem_var][:,0,y,x].squeeze().values

            df1 = df1.reset_index()
            df1.drop(columns='index',inplace=True)
            df2 = df2.reset_index()
            df2.drop(columns='index',inplace=True)
            
            diff = df2 - df1

            df_importance = rf_importance(diff,variants,target)
            print(f'({x},{y}) --> {process:.2f} %')
            
            for var in output_varlist:
                dfs_dict[var].loc[y,x] = df_importance.loc[var].values[0]
                
    return dfs_dict