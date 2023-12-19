progdir = 'D:/Academic/Project/GRAD/'
datadir = 'D:/data/Graduation/'

# ===================
# namelist for model
# ===================

d01name = 'CN27GD_182X138'
d02name = 'CN9GD_98X74'
d03name = 'CN3GD_152X110'

# time range
def get_STR(year,month):
    if month == "Jul":
        STR = f'{year}-07-01T00'
    elif month == "Sep":
        STR = f'{year}-09-01T00'
    return STR

def get_END(year,month):
    if month == "Jul":
        END = f'{year}-07-31T23'
    elif month == "Sep":
        END = f'{year}-09-30T23'
    return END

# ===================
# namelist for data preprocess
# ===================

grid_d01 = datadir + 'GRID/GRIDCRO2D_D01.nc'
grid_d02 = datadir + 'GRID/GRIDCRO2D_D02.nc'
grid_d03 = datadir + 'GRID/GRIDCRO2D_D03.nc'

CB_Sep = datadir + 'COMBINE/Sep/'
CB_Jul = datadir + 'COMBINE/Jul/'

# ===================
# namelist for processed data
# ===================

processed_dir = datadir + 'processed/'
rfpath = datadir + 'Contribution/RandomForest_output/'

# ===================
# namelist for OBS data
# ===================

obs_dir = datadir + 'OBS/CHEM/'
def get_obspath(month):
    if month == "Jul":
        obspath = obs_dir + 'selTime_Jul/'
    elif month == "Sep":
        obspath = obs_dir + 'selTime_Sep/'
    return obspath

# ===================
# namelist for MEIC data
# ===================
meicdata = datadir + 'MEIC/'

# ===================
# namelist for shapefile
# ===================

geobdydir = datadir + 'shapefile/cities_geobdy/'
admindir = datadir + 'shapefile/cities_admin/'

city_names = ['PRD', 'Guangzhou', 'Foshan', 'Zhongshan', 'Zhuhai', 'Zhaoqing', 'Jiangmen',
              'Dongguan', 'Shenzhen', 'Huizhou', 'Hongkong', 'Macau']

shp_files = {}

# Geographical Boundary
for city_name in city_names:
    geo_path = geobdydir + f'{city_name}/{city_name}.shp'
    shp_files[f'{city_name}_geo'] = geo_path

# Administration Boundary
for city_name in city_names:
    adm_path = admindir + f'{city_name}/{city_name}.shp'
    shp_files[f'{city_name}_adm'] = adm_path

# shp_PRD_geo       = geobdydir + 'PRD/PRD.shp'
# shp_Guangzhou_geo = geobdydir + 'Guangzhou/Guangzhou.shp'
# shp_Foshan_geo    = geobdydir + 'Foshan/Foshan.shp'
# shp_Zhongshan_geo = geobdydir + 'Zhongshan/Zhongshan.shp'
# shp_Zhuhai_geo    = geobdydir + 'Zhuhai/Zhuhai.shp'
# shp_Zhaoqing_geo  = geobdydir + 'Zhaoqing/Zhaoqing.shp'
# shp_Jiangmen_geo  = geobdydir + 'Jiangmen/Jiangmen.shp'
# shp_Dongguan_geo  = geobdydir + 'Dongguan/Dongguan.shp'
# shp_Shenzhen_geo  = geobdydir + 'Shenzhen/Shenzhen.shp'
# shp_Huizhou_geo   = geobdydir + 'Huizhou/Huizhou.shp'
# shp_Hongkong_geo  = geobdydir + 'Hongkong/Hongkong.shp'
# shp_Macau_geo     = geobdydir + 'Macau/Macau.shp'

# shp_PRD_adm       = admindir + 'PRD/PRD.shp'
# shp_Guangzhou_adm = admindir + 'Guangzhou/Guangzhou.shp'
# shp_Foshan_adm    = admindir + 'Foshan/Foshan.shp'
# shp_Zhongshan_adm = admindir + 'Zhongshan/Zhongshan.shp'
# shp_Zhuhai_adm    = admindir + 'Zhuhai/Zhuhai.shp'
# shp_Zhaoqing_adm  = admindir + 'Zhaoqing/Zhaoqing.shp'
# shp_Jiangmen_adm  = admindir + 'Jiangmen/Jiangmen.shp'
# shp_Dongguan_adm  = admindir + 'Dongguan/Dongguan.shp'
# shp_Shenzhen_adm  = admindir + 'Shenzhen/Shenzhen.shp'
# shp_Huizhou_adm   = admindir + 'Huizhou/Huizhou.shp'
# shp_Hongkong_adm  = admindir + 'Hongkong/Hongkong.shp'
# shp_Macau_adm     = admindir + 'Macau/Macau.shp'