"""Copernicus training : Python for Marine Data
Courses given by Guillaume Koenig <gkoenig@mercator-ocean.fr>
The exercises in Python are included in this program.

Contribution by O.Moreau <o.moreau@optimal-system.com>
Objectives of this code :

    Reorganization of the trainings to be reusable with other dataset.
    Access the functions of this program with a simple menu
    Explore Maps, Datasets and Files
    Avoid downloading several times the same dataset/files by creating a local index.json.
    The function 'plot_climatology' can be used for several variables (thetao, so)
    The functions 'black_sea' and 'artic_sea' load several datasets and check for correlation
    The functions 'martinique', 'france', and 'britany' are using other dataset and optimized code 
    Present the maps in a slideshow and record the maps (photos)
"""
__version__ = '0.4'
__dateversion__ = 261126
DEBUG = False

### Import standard libraries
import time
from gc import collect
import json                         # To create an index of downloads
import re                           # To parse file paths in data
from   pathlib import Path          # Management of directory
import warnings                     # To control warning messages
# Import specific libraries for this project
import copernicusmarine             # access to Copernicus data
import cartopy.crs as ccrs          # map projections
import cartopy.feature as cfeature  # geographic features (coastlines, land...)
import matplotlib.dates as mdates   # dates
import matplotlib.pyplot as plt     # plotting
import numpy as np                  # numerical arrays and math tools
import xarray as xr                 # work with NetCDF multidimensional datasets
from   scipy.ndimage import label   # label connected components

if not DEBUG : warnings.filterwarnings("ignore")


##############################################
# Index of downloaded Copernicus  :
##############################################

directory = "cpdata"
data_directory = Path(directory)
data_directory.mkdir(exist_ok=True)
fulldir   = directory+"/"
indexfile = fulldir+"index.json"
print(f"Files will be downloaded to: {data_directory.resolve()}")

def read_json(file):
    try :
        with open(file) as f: 
            dico = json.load(f)
        return dico
    except :
        print("Err reading JSON")
        
def write_json(file,dico):
    try : 
        with open(file, "w") as f:
            json.dump(dico, f)
        return True
    except :
        print("Err writing JSON")
        
def create_index():
    if not Path(indexfile).exists() :
        print("Creating a new index")
        index={}
        index["code"] = "filepath of the dataset"
        write_json(indexfile,index)
        
def add_index(code,filepath) :
    index = read_json(indexfile)
    index[code] = filepath
    write_json(indexfile,index)
    
def found_file(code) :
    index = read_json(indexfile)
    #if DEBUG : print(index)
    if code in index :
        filepath = index[code]
        return filepath
    else :
        return False


##############################################
# Ploting maps 
##############################################

def basic_geo_features(ax, lon_min=None, lon_max=None, lat_min=None, lat_max=None):
    # Add geographic features
    ax.add_feature(cfeature.COASTLINE)  # coastlines
    ax.add_feature(cfeature.RIVERS)     # rivers
    ax.add_feature(cfeature.BORDERS, linestyle=":")  # country borders (dotted)
    ax.gridlines(draw_labels=True)  # gridlines with labels
    ax.set_extent([lon_min, lon_max, lat_min, lat_max])
    
def background(lon_min, lon_max, lat_min, lat_max, sizeX=10, sizeY=8) :
    fig, ax = plt.subplots(figsize=(sizeX, sizeY), subplot_kw={"projection": ccrs.PlateCarree()})
    basic_geo_features(ax, lon_min, lon_max, lat_min, lat_max)
    return fig, ax

def color_bar(im, ax, label, shrink) : 
    # Add a colorbar linked to the plotted image, label it and shrink it to fit the layout
    plt.colorbar(im, ax, label, shrink)

def title(ax,text) :
    # Add a title (newline used to wrap subtitle)
    ax.set_title(text)

def convert_lonlat(lat,lon,size) :
    lat_min = lat-size/2
    lat_max = lat+size/2
    lon_min = lon-size/2
    lon_max = lon+size/2
    return (lon_min, lon_max, lat_min, lat_max)
    

def explore_maps() :
    print("\n\n====================\nExploration of Maps")
    print("Find the latitude and longitude with : https://www.latlong.net/")
    print("Choose the size of the map from 0.1 to 10")
    try : 
        lat=float(input("Latitude of the site ? "))
        lon=float(input("Longitude of the site ? "))
        size=float(input("Size of the site ? "))
        lat_min = lat-size/2
        lat_max = lat+size/2
        lon_min = lon-size/2
        lon_max = lon+size/2
        background(lon_min, lon_max, lat_min, lat_max, sizeX=10, sizeY=10)
        plt.pause(60)
        plt.close("all")
    except :
        print("Wrong input, sorry...")
        pass


##############################################
# Copernicus functions
##############################################

def explore_dataset() :
    print("\n\n====================\nExploration of Copernicus Datasets")
    ds=str(input("Name of the dataset ? "))
    try : 
        cop_files = copernicusmarine.get(
            dataset_id=ds,
            dry_run=True,
        )
        print(f"\nDataset found : {ds}")
        print(f"Number of files: {cop_files.number_of_files_to_download}")
        print(f"Total size: {cop_files.total_size / 1024:.0f} GB")
        print("\n Full dataset : ",cop_files)
        for file in cop_files.files[:3]:
            print("\nFilename    :",file.filename)
        print(f"\nMost recent : {cop_files.files[-1].filename}")
        time.sleep(10)
    except :
        print("Unknown dataset, sorry...")
        pass

    
def explore_file():
    print("\n\n====================\nExploration of Copernicus Files")
    code =str(input("Code of the file ? "))
    
    filepath = found_file(code)
    if not filepath :
        print("You must download that subset first. Sorry..")
        print("DataSet requested filepath :",filepath)
    else :
        my_file = filepath
        ds = xr.open_dataset(my_file)
        print("\n################ Dataset ###################  :\n",ds)
        print("\n################ Variables #################  :\n",ds.variables)
        time.sleep(10)


def load_dataset(dataset_id, data_filter,dry_run=False) :
    cop_files = copernicusmarine.get(
        dataset_id=dataset_id,
        filter=data_filter,
        output_directory=data_directory
    )
    return cop_files

def get_filterset(code,dataset,datafilter,filenum=0) :
    filepath = found_file(code)
    if DEBUG : print("DataSet filepath :",filepath)
    if not filepath :     
        cop_files = load_dataset(dataset,datafilter)
        my_file = Path(cop_files.files[filenum].file_path)
        match = re.search(r"file_path=PosixPath\('([^']+)'\)", str(cop_files.files))
        if match:
            filepath = match.group(1)
        if DEBUG : print("\n Adding to index.json : ",code,filepath)
        add_index(code,filepath)
    else :
        my_file = filepath
    ds = xr.open_dataset(my_file)
    ds = ds.squeeze() # to remove phantom data !
    print("Processing dataset :",ds.title)
    return ds


def get_subset(code,dataset,variable,*args) :
    filepath = found_file(code)
    if DEBUG : print("DataSet filepath :",filepath)
    if not filepath :
        print("Downloading of a subset frome Copernicus, please wait.")
        cop_file = copernicusmarine.subset(
            dataset_id=dataset,
            variables=[variable],
            start_datetime  =args[0],
            end_datetime    =args[1],
            minimum_depth   =args[2],
            maximum_depth   =args[3],
            output_directory=data_directory
        )
        my_file = Path(cop_file.file_path)
        if DEBUG : print("\n Adding a code and a filepath into index.json : \n",code,my_file)
        add_index(code,str(my_file))
    else :
        my_file = filepath
    ds = xr.open_dataset(my_file)
    ds = ds.squeeze() # to remove phantom data !
    if DEBUG : print("\n Dataset content : ",ds)
    print("Processing dataset :",ds.title)
    return ds


def plot_climatology(ax, dataset, variable, minmax=(10,20), colormap="jet",\
                        lon="longitude", lat="latitude", adj=0):
    var = dataset[variable].data + adj
    im = ax.pcolormesh(
        dataset[lon].data,
        dataset[lat].data,
        var,
        cmap=colormap,  
        vmin=minmax[0],
        vmax=minmax[1], 
    )
    return im


def plot_correlation_map(fig,ax,correlation, title, label, tim):
    """Plot a correlation map with a fixed diverging colormap."""
    im = ax.pcolormesh(
        correlation.longitude.data,  # x coordinates
        correlation.latitude.data,   # y coordinates
        correlation,                # correlation values
        cmap="RdBu_r",               # diverging colormap for positive/negative correlation
        vmin=-1,
        vmax=1,                      # fixed range for correlation
    )
    plt.colorbar(im, ax=ax, label=label, shrink=0.5)
    ax.set_title(title)
    plt.pause(tim)

##############################################
# First training : Black Sea
##############################################

def black_sea() :
    #1) Define variables
    # What? Choosing data downloaded, analysed and ploted
    project   = "Correlate several Copernicus dataset of the Black sea"
    product   = "BLKSEA_MULTIYEAR_PHY_007_004"
    URL       = "https://data.marine.copernicus.eu/product/BLKSEA_MULTIYEAR_PHY_007_004/description"
    
    code1     = "black_sea_temp"
    title1    = "Climatology of SST on the Black Sea \n1993-2022"
    dataset1  = "cmems_mod_blk_phy-temp_my_2.5km_P1M-m"
    variable1 = "thetao" #temperature
    label1    = "SST (°C)"
    
    code2     = "black_sea_salinity"
    title2    = "Climatology of surface salinity on the Black Sea \n1993-2022"
    dataset2  = "cmems_mod_blk_phy-sal_my_2.5km_P1M-m"
    variable2 = "so" #salinity
    label2    = "Salinity (ssu)"
    
    code3     = "black_sea_bio"
    title3    = "Climatology of biological primary production on the Black Sea \n1993-2022"
    dataset3  = "cmems_mod_blk_bgc-bio_my_2.5km_P1M-m"
    variable3 = "nppv" # primary production
    label3    = "Biological primary production"
    
    code4     = "black_sea_evaporation"
    title4    = "Climatology of evaporation on the Black Sea \n1993-2022"
    dataset4  = "cmems_mod_blk_phy-mflux_my_2.5km_P1M-m"
    variable4 = "evs" #[kg m-2 s-1] Evaporation
    label4    = "Evaporation"

    titleC1   = "Correlation between temperature and salinity"
    labelC1   = "Strenght (-1=None 0=Maybe 1=Sure)"
    
    titleC2   = "Correlation between temperature and biological primary production"
    labelC2   = "Strenght (-1=None 0=Maybe 1=Sure)"
    
    titleC3   = "Correlation between temperature and evaporation"
    labelC3   = "Strenght (-1=None 0=Maybe 1=Sure)"
    
    # Where? Define Black Sea bounding box
    lon_min, lon_max = 27, 43
    lat_min, lat_max = 40, 48
    
    # When? Maximum period of observation
    start_date = "1993-01-01"
    end_date   = "2022-12-31"
    
    # How? Choosing temperature at the closest level layer to the surface from the product
    min_depth = 0.5001727938652039
    max_depth = 0.5001727938652039
    time_data = 5
    time_corr = 10


#2) Download data in arrays
    print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(project)

    ds1 = get_subset(code1,dataset1,variable1,start_date,end_date,min_depth,max_depth)
    ds2 = get_subset(code2,dataset2,variable2,start_date,end_date,min_depth,max_depth)
    ds3 = get_subset(code3,dataset3,variable3,start_date,end_date,min_depth,max_depth)
    ds4 = get_subset(code4,dataset4,variable4,start_date,end_date,min_depth,max_depth)
    
#3) Analyse data
    ds1_mean = ds1.mean(dim="time")
    ds2_mean = ds2.mean(dim="time")
    ds3_mean = ds3.mean(dim="time")
    ds4_mean = ds4.mean(dim="time")
    correlation1 = xr.corr(ds1.thetao, ds2.so,  dim="time")
    correlation2 = xr.corr(ds1.thetao, ds3[variable3], dim="time")
    correlation3 = xr.corr(ds1.thetao, ds4.evs, dim="time")
    if DEBUG :
        print("\n Analyse result of :",code1,ds1_mean)
        print("\n Analyse result of :",code2,ds2_mean)
        print("\n Analyse result of :",code3,ds3_mean)
        print("\n Analyse result of :",code4,ds4_mean)


#4) Plot the data maps
    for ds, var, label, ttl, dur in [
        (ds1_mean, variable1, label1, title1, time_data),
        (ds2_mean, variable2, label2, title2, time_data),
        (ds3_mean, variable3, label3, title3, time_data),
        (ds4_mean, variable4, label4, title4, time_data),
    ]:
        fig, ax = background (lon_min, lon_max, lat_min, lat_max)
        basic_geo_features(ax,lon_min, lon_max, lat_min, lat_max)
        im = plot_climatology(ax, ds, var)
        plt.colorbar(im, ax=ax, label=label, shrink=0.5)
        ax.set_title(ttl)
        plt.pause(dur)
        plt.close("all")
        
# Plot the correlation maps
    for correlation, title, label in [
        (correlation1, titleC1, labelC1),
        (correlation2, titleC2, labelC2),
        (correlation3, titleC3, labelC3),
    ]:
        fig, ax = background(lon_min, lon_max, lat_min, lat_max)
        plot_correlation_map(fig, ax, correlation, title, label, time_corr)
        plt.close("all")

##############################################
# Second training : Artic Sea
##############################################

def artic_sea() :
    # Copernicus module specific for ploting artic sea !
    from arctic_maps import plot_arctic_map
    
#1) Define variables
    # What? Choosing data downloaded, analysed and ploted
    project   = "Correlate several Copernicus dataset of the Artic sea"
    product   = "SEAICE_ARC_SEAICE_L4_NRT_OBSERVATIONS_011_008"
    URL       = """https://data.marine.copernicus.eu/product/DMI-ARC-SEAICE_TEMP-L4-NRT-OBS4"/description"""
    dataset   = "DMI-ARC-SEAICE_TEMP-L4-NRT-OBS"
    basecode  = "artic_sea_temp_"

    variable1 = "analysed_st" #temperature
    label1     = "SST (°C)"
    date1     = "20261119"
    code1     = basecode+date1
    filter1   = "*"+date1+"*"
    title1    = "Arctic sea temperature from space "+date1
    
    variable2 = "sea_ice_fraction" #temperature
    label2    = "Ice fraction"
    date2     = "20261119"
    code2     = basecode+date2
    filter2   = "*"+date2+"*"
    title2    = "Arctic ice fraction from space"+date2
 
#2) Download data in arrays
    print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(project)

    ds1 = get_filterset(code1,dataset,filter1,0)
    ds2 = get_filterset(code2,dataset,filter2,0)

#3) Analyse data
    temperature = ds1[variable1]
    print(f"Temperature range: {float(temperature.min()):.1f} K to {float(temperature.max()):.1f} K")
    temperature_celsius = temperature - 273.15
    ice = ds2[variable2]
#     print(f"Ice fraction: {ice.min} {ice.max}")
    

#4) Plot result
    plot_arctic_map(
        temperature_celsius,
        title1,
        cmap="RdBu_r", vmin=-15, vmax=15,
        cbar_kwargs={"label": "Surface temperature (°C)", "shrink": 0.7},
        )
     
    plt.pause(2)
    
    plot_arctic_map(
        ice,
        title2,
        cmap="Blues_r", vmin=0, vmax=1,
        cbar_kwargs={"label": "Sea ice fraction", "shrink": 0.7},
        )
     
    plt.pause(10)
    plt.close("all")


##############################################
# New project : Martinique
##############################################

def martinique() :
#1) define variables
    project    = "Correlate several Copernicus dataset of the sea around Martinique"
    product    = "GLOBAL_ANALYSISFORECAST_PHY_001_024"
    URL        = "https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_PHY_001_024/description"
    dataset1   = "cmems_mod_glo_phy-thetao_anfc_0.083deg_P1D-m"
    variable1  = "thetao" #temperature

    code1      = "martinique_temp01"
    title1     = "Climatology of SST on the sea around Martinique"
    label1     = "SST (°C)"
    colormap   = "coolwarm" #https://matplotlib.org/stable/users/explain/colors/colormaps.html
    mapsize    = (10, 10)
    geomap     = (14.65,-61.0, 5) # Full Martinique
    minmax     = (29,30)
    start_date = "2026-11-01"
    end_date   = "2026-11-24"
    min_depth  = 0.5001727938652039
    max_depth  = 0.5001727938652039
    photo1     = True
    
#2) Download data in arrays
    print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(project)

    ds1 = get_subset(code1,dataset1,variable1,start_date,end_date,min_depth,max_depth)
#     ds2 = get_subset(code2,dataset2,variable2,start_date,end_date,min_depth,max_depth)
    
#3) Analyse data
    ds1_mean = ds1.mean(dim="time")
#     ds2_mean = ds2.mean(dim="time")
#     correlation1 = xr.corr(ds1.thetao, ds2.so,  dim="time")
#     if DEBUG : print("\n Analyse result of :",code1,ds1_mean)

#4) Plot the data maps
    latlon = convert_lonlat(*geomap)
 
    for ds, var, label, ttl, pho, cod in [
        (ds1_mean, variable1, label1, title1, photo1, code1),
#         (ds2_mean, variable2, label2, title2, photo2, code2),
    ]:
        fig, ax = background(*latlon,*mapsize)
        basic_geo_features(ax,*latlon)
        im = plot_climatology(ax, ds, var, minmax, colormap)
        plt.colorbar(im, ax=ax, label=label, shrink=0.5)
        ax.set_title(ttl)
        if pho : plt.savefig(fulldir+cod+'.png')
        plt.pause(10)
        plt.close("all")
        
#5) Plot the correlation maps
#     for correlation, title, label in [
#         (correlation1, titleC1, labelC1),
#     ]:
#         fig, ax = background(*latlon,*mapsize)
#         plot_correlation_map(fig, ax, correlation, title, label, time_corr)
#         plt.close("all")


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

    ds1 = get_subset(code1,dataset1,variable1,start_date,end_date,min_depth,max_depth)
#     ds2 = get_subset(code2,dataset2,variable2,start_date,end_date,min_depth,max_depth)
    
#3) Analyse data
    ds1_mean = ds1.mean(dim="time")
#     ds2_mean = ds2.mean(dim="time")
#     correlation1 = xr.corr(ds1.thetao, ds2.so,  dim="time")
#     if DEBUG : print("\n Analyse result of :",code1,ds1_mean)

#4) Plot the data maps
    latlon = convert_lonlat(*geomap)

 
    for ds, var, label, ttl, pho, cod in [
        (ds1_mean, variable1, label1, title1, photo1, code1),
#         (ds2_mean, variable2, label2, title2, photo2, code2),
    ]:
        fig, ax = background(*latlon,*mapsize)
        basic_geo_features(ax,*latlon)
        im = plot_climatology(ax, ds, var, minmax, colormap)
        plt.colorbar(im, ax=ax, label=label, shrink=0.5)
        ax.set_title(ttl)
        if pho : plt.savefig(fulldir+cod+'.png')
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

    ds1 = get_filterset(code1,dataset,filter1,0)
    ds2 = get_filterset(code2,dataset,filter2,0)

#3) Analyse data
    temp1 = ds1[variable]
    print(f"Temperature range: {float(temp1.min()):.1f} K to {float(temp1.max()):.1f} K")
    temp2 = ds2[variable]
    print(f"Temperature range: {float(temp2.min()):.1f} K to {float(temp2.max()):.1f} K")

#4) Plot the data maps
    latlon = convert_lonlat(*geomap)

    for ds, var, label, ttl, pho, cod in [
        (ds1, variable, label, title1, photo, code1),
        (ds2, variable, label, title2, photo, code2),
    ]:
        fig, ax = background(*latlon,*mapsize)
        basic_geo_features(ax,*latlon)
        im = plot_climatology(ax, ds, var, minmax=minmax, colormap=colormap,\
                                 lon="lon", lat="lat", adj=-273.5)
        plt.colorbar(im, ax=ax, label=label, shrink=0.5)
        ax.set_title(ttl)
        if pho : plt.savefig(fulldir+cod+'.png')
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
    create_index()
    while True :
        print("\n--- MENU des TEST---\n")
        print("1 = Black Sea")
        print("2 = Artic Sea")
        print("3 = Martinique")
        print("4 = France")
        print("5 = Bretagne")
        print("6 = Sandbox")
        print("7 = Explore Maps")
        print("8 = Explore Copernicus Datasets")
        print("9 = Explore Copernicus Files")
        print("0 = STOP")
        choice = int(input("\n??? "))
        if choice not in (1,2,3,4,5,6,7,8,9,0) :
            print("Not on the menu !")
            pass
        elif choice == 1 : black_sea()
        elif choice == 2 : artic_sea()
        elif choice == 3 : martinique()
        elif choice == 4 : france()
        elif choice == 5 : bretagne()
        elif choice == 6 : sandbox()
        elif choice == 7 : explore_maps()
        elif choice == 8 : explore_dataset()
        elif choice == 9 : explore_file()
        elif choice == 0 : stop()

if __name__ == '__main__': 
    loop()


    
