"""
copernicus_tools.py
by O.Moreau <o.moreau@optimal-system.com>

A set of functions to do :
- Create and use an index of dowloaded datasets / files
- Explore maps, datsets, files
- Ploting maps with features (ex: coastline, borders)
- Specific Copernicus functions to get and plot data 
"""
__version__ = '0.5'
__dateversion__ = 261127
DEBUG = False

### Import standard libraries
import time
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

def found_file(code) :
    index = read_json(indexfile)
    #if DEBUG : print(index)
    if code in index :
        filepath = index[code]
        return filepath
    else :
        return False

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
    
##############################################
# Explore maps, datsets, files
##############################################
    
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


##############################################
# Ploting maps 
##############################################

def convert_lonlat(lat,lon,size) :
    lat_min = lat-size/2
    lat_max = lat+size/2
    lon_min = lon-size/2
    lon_max = lon+size/2
    return (lon_min, lon_max, lat_min, lat_max)

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


##############################################
# Copernicus functions
##############################################


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
