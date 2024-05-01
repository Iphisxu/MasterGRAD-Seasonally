import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from matplotlib.colors import Normalize

from cnmaps import get_adm_maps, clip_quiver_by_map, clip_contours_by_map, draw_map
import geopandas as gpd
from shapely.ops import unary_union

from matplotlib import rcParams
config = {
    "font.family":'Times New Roman',
    "mathtext.fontset":'stix',
    "font.serif": ['SimSun'],
}
rcParams.update(config)

# silence the warning note
import warnings
warnings.filterwarnings("ignore")

# Change font size and two subplots
# revised version of plot_map_withobs, 2024-05-01
def contourmap(gridfile, cmin, cmax, cmstep, cbstep, 
                  data1_to_plot, data2_to_plot,
                  uwind1,vwind1,uwind2,vwind2,
                  obs1_to_plot, obs2_to_plot, 
                  obslon, obslat,ngrid=None, scale=None, headwidth=None,
                  mapcolor=None, colorbar_label=None,
                  outpath=None):
    
    lon = gridfile.longitude
    lat = gridfile.latitude
    contourf_ticks = np.arange(cmin, cmax, cmstep)
    colorbar_ticks = np.arange(cmin,cmax+0.01,cbstep)

    fig = plt.figure(figsize=(12, 6), dpi=300)
    ax = fig.subplots(1, 2, subplot_kw={'projection': ccrs.PlateCarree()})
    if mapcolor is not None:
        colormap = mapcolor
    else:
        colormap = 'Spectral_r'
    
    # =============================================
    # Defining map boundaries
    # =============================================
    
    cities = ['广州市', '佛山市', '深圳市', '东莞市', '珠海市', '中山市', '惠州市', '江门市', '肇庆市']
    multi_polygons = []

    for city in cities:
        polygon = get_adm_maps(city=city, record='first', only_polygon=True)
        multi_polygons.append(polygon)
        draw_map(polygon, color='gray', linewidth=0.8,ax=ax[0])
        draw_map(polygon, color='gray', linewidth=0.8,ax=ax[1])

    map_polygon = unary_union(multi_polygons)

    data_to_plot = [data1_to_plot, data2_to_plot]
    for i in range(2):
        gl = ax[i].gridlines(
            xlocs=np.arange(-180, 180 + 1, 1), ylocs=np.arange(-90, 90 + 1, 1),
            draw_labels=True, x_inline=False, y_inline=False,
            linewidth=0, linestyle='--', color='gray')
        gl.top_labels = False
        gl.right_labels = False
        gl.rotate_labels = False
        gl.xlabel_style = {'size': 20}
        gl.ylabel_style = {'size': 20}
        
        ax[i].set_extent([111.2, 115.5, 21.4, 24.5], ccrs.PlateCarree())

        # =============================================
        # Pollutants concentration & Mask map
        # =============================================

        cf = ax[i].contourf(lon, lat, data_to_plot[i],
                        cmap=colormap,
                        levels=contourf_ticks, extend='both',
                        transform=ccrs.PlateCarree())

        clip_contours_by_map(cf,map_polygon,ax=ax[i])
        # =============================================
        # Wind vector map & Mask map
        # =============================================

        uwind = [uwind1, uwind2]
        vwind = [vwind1, vwind2]
        xgrid = np.size(uwind1, 1)
        ygrid = np.size(uwind1, 0)
        if ngrid is not None and scale is not None and headwidth is not None:
            qv = ax[i].quiver(lon[0:ygrid:ngrid, 0:xgrid:ngrid], lat[0:ygrid:ngrid, 0:xgrid:ngrid],
                       uwind[i][0:ygrid:ngrid, 0:xgrid:ngrid], vwind[i][0:ygrid:ngrid, 0:xgrid:ngrid],
                       transform=ccrs.PlateCarree(), color='k', alpha=1, scale=scale, headwidth=headwidth)
            clip_quiver_by_map(qv, map_polygon,ax=ax[i])

        # =============================================
        # Observation stations scatter & Mask map
        # =============================================
        
        obs_to_plot = [obs1_to_plot, obs2_to_plot]
        norm = Normalize(vmin=cmin, vmax=cmax)
        
        cs = ax[i].scatter(obslon,obslat,c=obs_to_plot[i],cmap=colormap,marker='o',s=20,
                        edgecolors='k',linewidths=0.5,norm=norm,transform=ccrs.PlateCarree())
    
    # =============================================
    # Defining title of the map and colorbar
    # =============================================

    ax[0].set_title('(a)', loc='left', fontdict={'fontsize': 30, 'fontweight': 'bold'})
    ax[1].set_title('(b)', loc='left', fontdict={'fontsize': 30, 'fontweight': 'bold'})

    fig.subplots_adjust(right=0.9)
    pos = fig.add_axes([0.92, 0.25, 0.02, 0.5])
    cbar = fig.colorbar(cf,cax=pos,orientation='vertical')
    cbar.set_ticks(colorbar_ticks)
    cbar.ax.tick_params(labelsize=20)
    if colorbar_label is not None:
        cbar.set_label(colorbar_label,fontsize=20)

    plt.show()
    
    if outpath is not None:
        fig.savefig(outpath, dpi=300, bbox_inches='tight')

def map_noneobs(gridfile, cmin, cmax, cmstep, cbstep, 
                  data1_to_plot, data2_to_plot,
                  uwind1,vwind1,uwind2,vwind2,
                  ngrid=None, scale=None, headwidth=None,
                  mapcolor=None, colorbar_label=None,
                  outpath=None):
    
    lon = gridfile.longitude
    lat = gridfile.latitude
    contourf_ticks = np.arange(cmin, cmax, cmstep)
    colorbar_ticks = np.arange(cmin,cmax+0.01,cbstep)

    fig = plt.figure(figsize=(12, 6), dpi=300)
    ax = fig.subplots(1, 2, subplot_kw={'projection': ccrs.PlateCarree()})
    if mapcolor is not None:
        colormap = mapcolor
    else:
        colormap = 'Spectral_r'
    
    # =============================================
    # Defining map boundaries
    # =============================================
    
    cities = ['广州市', '佛山市', '深圳市', '东莞市', '珠海市', '中山市', '惠州市', '江门市', '肇庆市']
    multi_polygons = []

    for city in cities:
        polygon = get_adm_maps(city=city, record='first', only_polygon=True)
        multi_polygons.append(polygon)
        draw_map(polygon, color='gray', linewidth=0.8,ax=ax[0])
        draw_map(polygon, color='gray', linewidth=0.8,ax=ax[1])

    map_polygon = unary_union(multi_polygons)

    data_to_plot = [data1_to_plot, data2_to_plot]
    for i in range(2):
        gl = ax[i].gridlines(
            xlocs=np.arange(-180, 180 + 1, 1), ylocs=np.arange(-90, 90 + 1, 1),
            draw_labels=True, x_inline=False, y_inline=False,
            linewidth=0, linestyle='--', color='gray')
        gl.top_labels = False
        gl.right_labels = False
        gl.rotate_labels = False
        gl.xlabel_style = {'size': 20}
        gl.ylabel_style = {'size': 20}
        
        ax[i].set_extent([111.2, 115.5, 21.4, 24.5], ccrs.PlateCarree())

        # =============================================
        # Pollutants concentration & Mask map
        # =============================================

        cf = ax[i].contourf(lon, lat, data_to_plot[i],
                        cmap=colormap,
                        levels=contourf_ticks, extend='both',
                        transform=ccrs.PlateCarree())

        clip_contours_by_map(cf,map_polygon,ax=ax[i])
        # =============================================
        # Wind vector map & Mask map
        # =============================================

        uwind = [uwind1, uwind2]
        vwind = [vwind1, vwind2]
        xgrid = np.size(uwind1, 1)
        ygrid = np.size(uwind1, 0)
        if ngrid is not None and scale is not None and headwidth is not None:
            qv = ax[i].quiver(lon[0:ygrid:ngrid, 0:xgrid:ngrid], lat[0:ygrid:ngrid, 0:xgrid:ngrid],
                       uwind[i][0:ygrid:ngrid, 0:xgrid:ngrid], vwind[i][0:ygrid:ngrid, 0:xgrid:ngrid],
                       transform=ccrs.PlateCarree(), color='k', alpha=1, scale=scale, headwidth=headwidth)
            clip_quiver_by_map(qv, map_polygon,ax=ax[i])

    # =============================================
    # Defining title of the map and colorbar
    # =============================================

    ax[0].set_title('(a)', loc='left', fontdict={'fontsize': 30, 'fontweight': 'bold'})
    ax[1].set_title('(b)', loc='left', fontdict={'fontsize': 30, 'fontweight': 'bold'})

    fig.subplots_adjust(right=0.9)
    pos = fig.add_axes([0.92, 0.25, 0.02, 0.5])
    cbar = fig.colorbar(cf,cax=pos,orientation='vertical')
    cbar.set_ticks(colorbar_ticks)
    cbar.ax.tick_params(labelsize=20)
    if colorbar_label is not None:
        cbar.set_label(colorbar_label,fontsize=20)

    plt.show()
    
    if outpath is not None:
        fig.savefig(outpath, dpi=300, bbox_inches='tight')

# Change font size
# revised version of plot_map_withobs, 2024-05-01
def map_diff(gridfile, cmin, cmax, cmstep, cbstep, 
                  data1_to_plot, data2_to_plot,
                  obs1_to_plot, obs2_to_plot, 
                  obslon, obslat,
                  mapcolor=None, title=None, colorbar_label=None,
                  outpath=None):
    
    lon = gridfile.longitude
    lat = gridfile.latitude
    contourf_ticks = np.arange(cmin, cmax, cmstep)
    colorbar_ticks = np.arange(cmin,cmax+0.01,cbstep)

    fig = plt.figure(figsize=(12, 6), dpi=300)
    ax = fig.subplots(1, 1, subplot_kw={'projection': ccrs.PlateCarree()})
    if mapcolor is not None:
        colormap = mapcolor
    else:
        colormap = 'RdBu_r'
    
    # =============================================
    # Defining map boundaries
    # =============================================
    
    cities = ['广州市', '佛山市', '深圳市', '东莞市', '珠海市', '中山市', '惠州市', '江门市', '肇庆市']
    multi_polygons = []

    for city in cities:
        polygon = get_adm_maps(city=city, record='first', only_polygon=True)
        multi_polygons.append(polygon)
        draw_map(polygon, color='gray', linewidth=0.8)

    map_polygon = unary_union(multi_polygons)

    gl = ax.gridlines(
        xlocs=np.arange(-180, 180 + 1, 1), ylocs=np.arange(-90, 90 + 1, 1),
        draw_labels=True, x_inline=False, y_inline=False,
        linewidth=0, linestyle='--', color='gray')
    gl.top_labels = False
    gl.right_labels = False
    gl.rotate_labels = False
    gl.xlabel_style = {'size': 30}
    gl.ylabel_style = {'size': 30}
    
    ax.set_extent([111.2, 115.5, 21.4, 24.5], ccrs.PlateCarree())

    # =============================================
    # Pollutants concentration & Mask map
    # =============================================

    cf = ax.contourf(lon, lat, data2_to_plot - data1_to_plot,
                     cmap=colormap,
                     levels=contourf_ticks, extend='both',
                     transform=ccrs.PlateCarree())

    clip_contours_by_map(cf, map_polygon)
    
    # =============================================
    # Observation stations scatter & Mask map
    # =============================================
    
    norm = Normalize(vmin=cmin, vmax=cmax)
    
    cs = ax.scatter(obslon,obslat,c=obs2_to_plot - obs1_to_plot,cmap=colormap,marker='o',s=20,
                    edgecolors='k',linewidths=0.5,norm=norm,transform=ccrs.PlateCarree())
    
    # =============================================
    # Defining title of the map and colorbar
    # =============================================

    if title is not None:
        ax.set_title(title, loc='left', fontdict={'fontsize': 40, 'fontweight': 'bold'})

    cbar = fig.colorbar(cf)
    cbar.set_ticks(colorbar_ticks)
    cbar.ax.tick_params(labelsize=30)
    if colorbar_label is not None:
        cbar.set_label(colorbar_label,fontsize=30)

    plt.show()
    
    if outpath is not None:
        fig.savefig(outpath, dpi=300, bbox_inches='tight')

def diff_noneobs(gridfile, cmin, cmax, cmstep, cbstep, 
                  data1_to_plot, data2_to_plot,
                  mapcolor=None, title=None, colorbar_label=None,
                  outpath=None):
    
    lon = gridfile.longitude
    lat = gridfile.latitude
    contourf_ticks = np.arange(cmin, cmax, cmstep)
    colorbar_ticks = np.arange(cmin,cmax+0.01,cbstep)

    fig = plt.figure(figsize=(12, 6), dpi=300)
    ax = fig.subplots(1, 1, subplot_kw={'projection': ccrs.PlateCarree()})
    if mapcolor is not None:
        colormap = mapcolor
    else:
        colormap = 'RdBu_r'
    
    # =============================================
    # Defining map boundaries
    # =============================================
    
    cities = ['广州市', '佛山市', '深圳市', '东莞市', '珠海市', '中山市', '惠州市', '江门市', '肇庆市']
    multi_polygons = []

    for city in cities:
        polygon = get_adm_maps(city=city, record='first', only_polygon=True)
        multi_polygons.append(polygon)
        draw_map(polygon, color='gray', linewidth=0.8)

    map_polygon = unary_union(multi_polygons)

    gl = ax.gridlines(
        xlocs=np.arange(-180, 180 + 1, 1), ylocs=np.arange(-90, 90 + 1, 1),
        draw_labels=True, x_inline=False, y_inline=False,
        linewidth=0, linestyle='--', color='gray')
    gl.top_labels = False
    gl.right_labels = False
    gl.rotate_labels = False
    gl.xlabel_style = {'size': 30}
    gl.ylabel_style = {'size': 30}
    
    ax.set_extent([111.2, 115.5, 21.4, 24.5], ccrs.PlateCarree())

    # =============================================
    # Pollutants concentration & Mask map
    # =============================================

    cf = ax.contourf(lon, lat, data2_to_plot - data1_to_plot,
                     cmap=colormap,
                     levels=contourf_ticks, extend='both',
                     transform=ccrs.PlateCarree())

    clip_contours_by_map(cf, map_polygon)

    # =============================================
    # Defining title of the map and colorbar
    # =============================================

    if title is not None:
        ax.set_title(title, loc='left', fontdict={'fontsize': 40, 'fontweight': 'bold'})

    cbar = fig.colorbar(cf)
    cbar.set_ticks(colorbar_ticks)
    cbar.ax.tick_params(labelsize=30)
    if colorbar_label is not None:
        cbar.set_label(colorbar_label,fontsize=30)

    plt.show()
    
    if outpath is not None:
        fig.savefig(outpath, dpi=300, bbox_inches='tight')

#==================================================================

def plot_PRD_map(gridfile, cmin, cmax, cmstep, cbstep, 
                 data_to_plot, uwind_to_plot, vwind_to_plot,
                 ngrid=None, scale=None, headwidth=None, 
                 mapcolor=None, title=None, colorbar_label=None,
                 outpath = None):
    
    '''
    绘制珠三角地区的填色地图，包括污染物浓度和风向风速。

    参数：
    gridfile (array-like)：包含经度和纬度信息的网格文件。
    cmin (float)：用于填色的污染物浓度的最小值。
    cmax (float)：用于填色的污染物浓度的最大值。
    cmstep (float)：等值线的步长。
    cbstep (float)：色标带的步长。
    data_to_plot (array-like)：要绘制的污染物浓度数据。
    uwind_to_plot (array-like)：要绘制的东西向风速数据。
    vwind_to_plot (array-like)：要绘制的南北向风速数据。
    ngrid (int, optional)：风速箭头的密度。
    scale (float, optional)：风速箭头的缩放比例。
    headwidth (float, optional)：风速箭头的头部宽度。
    title (str, optional)：地图的标题。
    colorbar_label (str, optional)：颜色条的标签。
    '''
    
    lon = gridfile.longitude
    lat = gridfile.latitude
    contourf_ticks = np.arange(cmin, cmax, cmstep)
    colorbar_ticks = np.arange(cmin,cmax+0.01,cbstep)
    if mapcolor is not None:
        colormap = mapcolor
    else:
        colormap = 'Spectral_r'
    
    fig = plt.figure(figsize=(12, 6), dpi=300)
    ax = fig.subplots(1, 1, subplot_kw={'projection': ccrs.PlateCarree()})

    # =============================================
    # Defining map boundaries
    # =============================================
    
    cities = ['广州市', '佛山市', '深圳市', '东莞市', '珠海市', '中山市', '惠州市', '江门市', '肇庆市']
    multi_polygons = []

    for city in cities:
        polygon = get_adm_maps(city=city, record='first', only_polygon=True)
        multi_polygons.append(polygon)
        draw_map(polygon, color='gray', linewidth=0.8)

    map_polygon = unary_union(multi_polygons)

    gl = ax.gridlines(
        xlocs=np.arange(-180, 180 + 1, 1), ylocs=np.arange(-90, 90 + 1, 1),
        draw_labels=True, x_inline=False, y_inline=False,
        linewidth=0, linestyle='--', color='gray')
    gl.top_labels = False
    gl.right_labels = False
    gl.rotate_labels = False

    ax.set_extent([111.2, 115.5, 21.4, 24.5], ccrs.PlateCarree())

    # =============================================
    # Pollutants concentration & Mask map
    # =============================================

    cf = ax.contourf(lon, lat, data_to_plot,
                     cmap=colormap,
                     levels=contourf_ticks, extend='both',
                     transform=ccrs.PlateCarree())

    clip_contours_by_map(cf, map_polygon)

    # =============================================
    # Wind vector map & Mask map
    # =============================================

    xgrid = np.size(uwind_to_plot, 1)
    ygrid = np.size(uwind_to_plot, 0)
    if ngrid is not None and scale is not None and headwidth is not None:
        qv = ax.quiver(lon[0:ygrid:ngrid, 0:xgrid:ngrid], lat[0:ygrid:ngrid, 0:xgrid:ngrid],
                       uwind_to_plot[0:ygrid:ngrid, 0:xgrid:ngrid], vwind_to_plot[0:ygrid:ngrid, 0:xgrid:ngrid],
                       transform=ccrs.PlateCarree(), color='k', alpha=1, scale=scale, headwidth=headwidth)
        clip_quiver_by_map(qv, map_polygon)

    # =============================================
    # Defining title of the map and colorbar
    # =============================================

    if title is not None:
        ax.set_title(title, loc='left', fontdict={'fontsize': 16, 'fontweight': 'bold'})

    cbar = plt.colorbar(cf)
    cbar.set_ticks(colorbar_ticks)
    if colorbar_label is not None:
        cbar.set_label(colorbar_label)

    plt.show()
    
    if outpath is not None:
        fig.savefig(outpath, dpi=300, bbox_inches='tight')

def plot_PRD_diff(gridfile, cmin, cmax, cmstep, cbstep, 
                  data1_to_plot, data2_to_plot,
                  mapcolor=None, title=None, colorbar_label=None,
                  outpath=None):
    
    '''
    绘制珠三角地区的污染物浓度差值填色图。

    参数：
    gridfile (array-like)：包含经度和纬度信息的网格文件。
    cmin (float)：用于填色的污染物浓度的最小值。
    cmax (float)：用于填色的污染物浓度的最大值。
    cmstep (float)：等值线的步长。
    cbstep (float)：色标带的步长。
    data1_to_plot (array-like)：污染物浓度数据1。
    data2_to_plot (array-like)：污染物浓度数据2。
    title (str, optional)：地图的标题。
    colorbar_label (str, optional)：颜色条的标签。
    '''
    
    lon = gridfile.longitude
    lat = gridfile.latitude
    contourf_ticks = np.arange(cmin, cmax, cmstep)
    colorbar_ticks = np.arange(cmin,cmax+0.01,cbstep)

    fig = plt.figure(figsize=(12, 6), dpi=300)
    ax = fig.subplots(1, 1, subplot_kw={'projection': ccrs.PlateCarree()})
    if mapcolor is not None:
        colormap = mapcolor
    else:
        colormap = 'RdBu_r'
    
    # =============================================
    # Defining map boundaries
    # =============================================
    
    cities = ['广州市', '佛山市', '深圳市', '东莞市', '珠海市', '中山市', '惠州市', '江门市', '肇庆市']
    multi_polygons = []

    for city in cities:
        polygon = get_adm_maps(city=city, record='first', only_polygon=True)
        multi_polygons.append(polygon)
        draw_map(polygon, color='gray', linewidth=0.8)

    map_polygon = unary_union(multi_polygons)

    gl = ax.gridlines(
        xlocs=np.arange(-180, 180 + 1, 1), ylocs=np.arange(-90, 90 + 1, 1),
        draw_labels=True, x_inline=False, y_inline=False,
        linewidth=0, linestyle='--', color='gray')
    gl.top_labels = False
    gl.right_labels = False
    gl.rotate_labels = False

    ax.set_extent([111.2, 115.5, 21.4, 24.5], ccrs.PlateCarree())

    # =============================================
    # Pollutants concentration & Mask map
    # =============================================

    cf = ax.contourf(lon, lat, data2_to_plot - data1_to_plot,
                     cmap=colormap,
                     levels=contourf_ticks, extend='both',
                     transform=ccrs.PlateCarree())

    clip_contours_by_map(cf, map_polygon)

    # =============================================
    # Defining title of the map and colorbar
    # =============================================

    if title is not None:
        ax.set_title(title, loc='left', fontdict={'fontsize': 16, 'fontweight': 'bold'})

    cbar = plt.colorbar(cf)
    cbar.set_ticks(colorbar_ticks)
    if colorbar_label is not None:
        cbar.set_label(colorbar_label)

    plt.show()
    
    if outpath is not None:
        fig.savefig(outpath, dpi=300, bbox_inches='tight')
    

def plot_map_withobs(gridfile, cmin, cmax, cmstep, cbstep, 
                 data_to_plot, uwind_to_plot, vwind_to_plot,
                 obsdata, obslon, obslat,
                 ngrid=None, scale=None, headwidth=None, 
                 mapcolor=None, title=None, colorbar_label=None,
                 outpath=None):

    lon = gridfile.longitude
    lat = gridfile.latitude
    contourf_ticks = np.arange(cmin, cmax, cmstep)
    colorbar_ticks = np.arange(cmin,cmax+0.01,cbstep)
    if mapcolor is not None:
        colormap = mapcolor
    else:
        colormap = 'Spectral_r'
    
    fig = plt.figure(figsize=(12, 6), dpi=300)
    ax = fig.subplots(1, 1, subplot_kw={'projection': ccrs.PlateCarree()})

    # =============================================
    # Defining map boundaries
    # =============================================
    
    cities = ['广州市', '佛山市', '深圳市', '东莞市', '珠海市', '中山市', '惠州市', '江门市', '肇庆市']
    multi_polygons = []

    for city in cities:
        polygon = get_adm_maps(city=city, record='first', only_polygon=True)
        multi_polygons.append(polygon)
        draw_map(polygon, color='gray', linewidth=0.8)

    map_polygon = unary_union(multi_polygons)

    gl = ax.gridlines(
        xlocs=np.arange(-180, 180 + 1, 1), ylocs=np.arange(-90, 90 + 1, 1),
        draw_labels=True, x_inline=False, y_inline=False,
        linewidth=0, linestyle='--', color='gray')
    gl.top_labels = False
    gl.right_labels = False
    gl.rotate_labels = False

    ax.set_extent([111.2, 115.5, 21.4, 24.5], ccrs.PlateCarree())

    # =============================================
    # Pollutants concentration & Mask map
    # =============================================

    cf = ax.contourf(lon, lat, data_to_plot,
                     cmap=colormap,
                     levels=contourf_ticks, extend='both',
                     transform=ccrs.PlateCarree())

    clip_contours_by_map(cf, map_polygon)

    # =============================================
    # Wind vector map & Mask map
    # =============================================

    xgrid = np.size(uwind_to_plot, 1)
    ygrid = np.size(uwind_to_plot, 0)
    if ngrid is not None and scale is not None and headwidth is not None:
        qv = ax.quiver(lon[0:ygrid:ngrid, 0:xgrid:ngrid], lat[0:ygrid:ngrid, 0:xgrid:ngrid],
                       uwind_to_plot[0:ygrid:ngrid, 0:xgrid:ngrid], vwind_to_plot[0:ygrid:ngrid, 0:xgrid:ngrid],
                       transform=ccrs.PlateCarree(), color='k', alpha=1, scale=scale, headwidth=headwidth)
        clip_quiver_by_map(qv, map_polygon)

    # =============================================
    # Observation stations scatter & Mask map
    # =============================================
    
    norm = Normalize(vmin=cmin, vmax=cmax)
    
    cs = ax.scatter(obslon,obslat,c=obsdata,cmap=colormap,marker='o',s=20,
                    edgecolors='k',linewidths=0.5,norm=norm,transform=ccrs.PlateCarree())
    
    # =============================================
    # Defining title of the map and colorbar
    # =============================================

    if title is not None:
        ax.set_title(title, loc='left', fontdict={'fontsize': 16, 'fontweight': 'bold'})

    cbar = plt.colorbar(cf)
    cbar.set_ticks(colorbar_ticks)
    if colorbar_label is not None:
        cbar.set_label(colorbar_label)

    plt.show()
    
    if outpath is not None:
        fig.savefig(outpath, dpi=300, bbox_inches='tight')
    

def plot_diff_withobs(gridfile, cmin, cmax, cmstep, cbstep, 
                  data1_to_plot, data2_to_plot,
                  obs1_to_plot, obs2_to_plot, 
                  obslon, obslat,
                  mapcolor=None, title=None, colorbar_label=None,
                  outpath=None):
    
    lon = gridfile.longitude
    lat = gridfile.latitude
    contourf_ticks = np.arange(cmin, cmax, cmstep)
    colorbar_ticks = np.arange(cmin,cmax+0.01,cbstep)

    fig = plt.figure(figsize=(12, 6), dpi=300)
    ax = fig.subplots(1, 1, subplot_kw={'projection': ccrs.PlateCarree()})
    if mapcolor is not None:
        colormap = mapcolor
    else:
        colormap = 'RdBu_r'
    
    # =============================================
    # Defining map boundaries
    # =============================================
    
    cities = ['广州市', '佛山市', '深圳市', '东莞市', '珠海市', '中山市', '惠州市', '江门市', '肇庆市']
    multi_polygons = []

    for city in cities:
        polygon = get_adm_maps(city=city, record='first', only_polygon=True)
        multi_polygons.append(polygon)
        draw_map(polygon, color='gray', linewidth=0.8)

    map_polygon = unary_union(multi_polygons)

    gl = ax.gridlines(
        xlocs=np.arange(-180, 180 + 1, 1), ylocs=np.arange(-90, 90 + 1, 1),
        draw_labels=True, x_inline=False, y_inline=False,
        linewidth=0, linestyle='--', color='gray')
    gl.top_labels = False
    gl.right_labels = False
    gl.rotate_labels = False

    ax.set_extent([111.2, 115.5, 21.4, 24.5], ccrs.PlateCarree())

    # =============================================
    # Pollutants concentration & Mask map
    # =============================================

    cf = ax.contourf(lon, lat, data2_to_plot - data1_to_plot,
                     cmap=colormap,
                     levels=contourf_ticks, extend='both',
                     transform=ccrs.PlateCarree())

    clip_contours_by_map(cf, map_polygon)
    
    # =============================================
    # Observation stations scatter & Mask map
    # =============================================
    
    norm = Normalize(vmin=cmin, vmax=cmax)
    
    cs = ax.scatter(obslon,obslat,c=obs2_to_plot - obs1_to_plot,cmap=colormap,marker='o',s=20,
                    edgecolors='k',linewidths=0.5,norm=norm,transform=ccrs.PlateCarree())
    
    # =============================================
    # Defining title of the map and colorbar
    # =============================================

    if title is not None:
        ax.set_title(title, loc='left', fontdict={'fontsize': 16, 'fontweight': 'bold'})

    cbar = plt.colorbar(cf)
    cbar.set_ticks(colorbar_ticks)
    if colorbar_label is not None:
        cbar.set_label(colorbar_label)

    plt.show()
    
    if outpath is not None:
        fig.savefig(outpath, dpi=300, bbox_inches='tight')