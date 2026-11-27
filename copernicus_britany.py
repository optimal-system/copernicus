"""
Etude de la météorolgie de la Bretagne
By O.Moreau <o.moreau@optimal-system.com>
"""
__version__ = '0.5'
__dateversion__ = 261127
DEBUG = False

import copernicus_tools as CT
# 
# ### Import standard libraries
# import time
# from gc import collect
# import json                         # To create an index of downloads
# import re                           # To parse file paths in data
# from   pathlib import Path          # Management of directory
# import warnings                     # To control warning messages
# # Import specific libraries for this project
# import copernicusmarine             # access to Copernicus data
# import cartopy.crs as ccrs          # map projections
# import cartopy.feature as cfeature  # geographic features (coastlines, land...)
# import matplotlib.dates as mdates   # dates
import matplotlib.pyplot as plt     # plotting
# import numpy as np                  # numerical arrays and math tools
# import xarray as xr                 # work with NetCDF multidimensional datasets
# from   scipy.ndimage import label   # label connected components
# 
# if not DEBUG : warnings.filterwarnings("ignore")
# 

###################################

def france() :
#1) define variables
    project    = "Correlate several Copernicus dataset of the sea around Britany"
    product    = "GLOBAL_ANALYSISFORECAST_PHY_001_024" # same as martinique_sea !!!
    URL        = "https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_PHY_001_024/description"
    dataset1   = "cmems_mod_glo_phy-thetao_anfc_0.083deg_P1D-m"
    variable1  = "thetao" #temperature

    code1      = "france_temp01"
    title1     = "Climatology of SST on the sea around France"
    label1     = "SST (°C)"
    colormap   = "coolwarm" #https://matplotlib.org/stable/users/explain/colors/colormaps.html
    mapsize    = (10,10)    # multiply by 100 for size in pixels
    geomap     = (48.25, -3.5, 25) # Centered on center of Britany
    minmax     = (10,20)
    start_date = "2026-11-01"
    end_date   = "2026-11-24"
    min_depth  = 0.5001727938652039
    max_depth  = 0.5001727938652039
    photo1     = True

#2) Download data in arrays
    print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(project)

    ds1 = CT.get_subset(code1,dataset1,variable1,start_date,end_date,min_depth,max_depth)
#     ds2 = get_subset(code2,dataset2,variable2,start_date,end_date,min_depth,max_depth)
    
#3) Analyse data
    ds1_mean = ds1.mean(dim="time")
#     ds2_mean = ds2.mean(dim="time")
#     correlation1 = xr.corr(ds1.thetao, ds2.so,  dim="time")
#     if DEBUG : print("\n Analyse result of :",code1,ds1_mean)

#4) Plot the data maps
    latlon = CT.convert_lonlat(*geomap)

 
    for ds, var, label, ttl, pho, cod in [
        (ds1_mean, variable1, label1, title1, photo1, code1),
#         (ds2_mean, variable2, label2, title2, photo2, code2),
    ]:
        fig, ax = CT.background(*latlon,*mapsize)
        CT.basic_geo_features(ax,*latlon)
        im = CT.plot_climatology(ax, ds, var, minmax, colormap)
        plt.colorbar(im, ax=ax, label=label, shrink=0.5)
        ax.set_title(ttl)
        if pho : plt.savefig(CT.fulldir+cod+'.png')
        plt.pause(10)
        plt.close("all")
        
#5) Plot the correlation maps
#     for correlation, title, label in [
#         (correlation1, titleC1, labelC1),
#     ]:
#         fig, ax = background(*latlon,*mapsize)
#         plot_correlation_map(fig, ax, correlation, title, label, time_corr)
#         plt.close("all")


########################################
def bretagne() :
#1) define variables
    project   = "Correlate several Copernicus dataset of the sea around Britany"
    product   = "SST_ATL_SST_L4_NRT_OBSERVATIONS_010_025"
    URL       = "https://documentation.marine.copernicus.eu/PUM/CMEMS-SST-PUM-010-025.pdf"
    dataset   = "IFREMER-ATL-SST-L4-NRT-OBS_FULL_TIME_SERIE"
    variable  = "analysed_sst" #temperature
    title     = "Climatology of SST on the sea around Britany. Date :"
    label     = "SST (°C)"
    colormap  = "jet" #https://matplotlib.org/stable/users/explain/colors/colormaps.html
    mapsize   = (10, 10)
    geomap    = (48.826763, -3.511280, 1) # Centered on Trégastel !
    minmax    = (12,20)
    photo     = True
    
    code1     = "bzh_temp11"
    date1     = "20260815"
    filter1   = "*"+date1+"*"
    title1    = title+date1

    code2     = "bzh_temp22"
    date2     = "20261115"
    filter2   = "*"+date2+"*"
    title2    = title+date2


#2) Download data in arrays
    print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(project)

    ds1 = CT.get_filterset(code1,dataset,filter1,0)
    ds2 = CT.get_filterset(code2,dataset,filter2,0)

#3) Analyse data
    temp1 = ds1[variable]
    print(f"Temperature range: {float(temp1.min()):.1f} K to {float(temp1.max()):.1f} K")
    temp2 = ds2[variable]
    print(f"Temperature range: {float(temp2.min()):.1f} K to {float(temp2.max()):.1f} K")

#4) Plot the data maps
    latlon = CT.convert_lonlat(*geomap)

    for ds, var, label, ttl, pho, cod in [
        (ds1, variable, label, title1, photo, code1),
        (ds2, variable, label, title2, photo, code2),
    ]:
        fig, ax = CT.background(*latlon,*mapsize)
        CT.basic_geo_features(ax,*latlon)
        im = CT.plot_climatology(ax, ds, var, minmax=minmax, colormap=colormap,\
                                 lon="lon", lat="lat", adj=-273.5)
        plt.colorbar(im, ax=ax, label=label, shrink=0.5)
        ax.set_title(ttl)
        if pho : plt.savefig(CT.fulldir+cod+'.png')
        plt.pause(10)
        plt.close("all")

 #################################   
    
def loop() :
    def soon() :
        print("Working on it...")
    def stop() :
        print("That's the END !")
        
    def sandbox() :
        pass

    print("============ TESTS COPERNICUS =================") 
    print("Version :", __version__)
    CT.create_index()
    while True :
        print("\n--- MENU des TEST---\n")
        print("1 = ")
        print("2 = ")
        print("3 = ")
        print("4 = France")
        print("5 = Bretagne")
        print("6 = ")
        print("7 = Explore Maps")
        print("8 = Explore Copernicus Datasets")
        print("9 = Explore Copernicus Files")
        print("0 = STOP")
        choice = int(input("\n??? "))
        if choice not in (1,2,3,4,5,6,7,8,9,0) :
            print("Not on the menu !")
            pass
        elif choice == 1 : pass
        elif choice == 2 : pass
        elif choice == 3 : pass
        elif choice == 4 : france()
        elif choice == 5 : bretagne()
        elif choice == 6 : pass
        elif choice == 7 : CT.explore_maps()
        elif choice == 8 : CT.explore_dataset()
        elif choice == 9 : CT.explore_file()
        elif choice == 0 : stop()

if __name__ == '__main__': 
    loop()


    
