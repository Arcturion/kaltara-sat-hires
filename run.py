import ftplib
import os
from datetime import datetime
import glob
import bz2,shutil

from satpy import Scene
from datetime import datetime
import matplotlib.pyplot as plt
import satpy

import cartopy.crs as ccrs
import cartopy.feature as cf
import xarray as xr

from PIL import Image, ImageEnhance, ImageDraw, ImageFont

  
ftp = ftplib.FTP('')
ftp.login('' , '')

ftp.cwd('')
alamats = ftp.nlst('')

for alamat in alamats:
    alamat_target = alamat
    print(alamat_target)
    ftp.retrbinary("RETR " + alamat_target ,open(alamat_target, 'wb').write)
    #ftp.retrbinary("RETR " + alamat_target ,open("/" + ""+alamat_target, 'wb').write)
ftp.close()

files = glob.glob(r'*DAT.bz2')

for file in files:
    data = file
    target = file[:-4]
    print(data)
    with bz2.BZ2File(data) as fr, open(target,"wb") as fw:
        shutil.copyfileobj(fr,fw)
        fw.close()

for file in files:
    os.remove(file)

files = glob.glob(r'*.DAT') 

scn = Scene(filenames=files,  reader='ahi_hsd',filter_parameters={'start_time': datetime(2023,1,1,9,45), 'end_time': datetime(2023,12,31,9,55)})

scn.load(["B03"])

cropped_scn = scn.crop(ll_bbox=(114.5, 1.8, 118.6, 5.2))
remapped_scn = cropped_scn.resample(cropped_scn.min_area(), resampler='native')
dset = remapped_scn.to_xarray_dataset()

def plot_dataset(dataset : xr.Dataset):
    projection = ccrs.PlateCarree()
    crs = ccrs.PlateCarree()
    plt.figure(figsize=(16,9), dpi=150)
    ax = plt.axes(projection=projection, frameon=True)
    gl = ax.gridlines(crs=crs, draw_labels=True,
                    linewidth=.6, color='gray', alpha=0.5, linestyle='-.')
    gl.xlabel_style = {"size" : 7}
    gl.ylabel_style = {"size" : 7}

    ax.add_feature(cf.COASTLINE.with_scale("10m"), lw=0.8)
    ax.add_feature(cf.BORDERS.with_scale("10m"), lw=0.8)
    
    lon_min = 115
    lon_max = 118.5
    lat_min = 2
    lat_max = 5
   
    cbar_kwargs = {'orientation':'horizontal', 'shrink':0.6, "pad" : .05, 'aspect':40, 'label':'Tutupan Awan High Ress'}
    dataset["B03"].plot.contourf(ax=ax, cmap=plt.cm.gray, transform=ccrs.Orthographic(central_latitude=0.1, central_longitude=140.3), levels=30)
    
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=crs)
    plt.savefig("output.jpg")
    plt.show()

plot_dataset(dset)

#files = glob.glob(r'*DAT')
#for file in files:
#    os.remove(file)
    
img = Image.open('output.jpg')

img = ImageEnhance.Brightness(img)
img = img.enhance(1.2)

img = ImageEnhance.Contrast(img)
img = img.enhance(0.95)

box = (500, 150, 1850, 1250)
img = img.crop(box)

fontsize = 12
font = ImageFont.truetype("arial.ttf", fontsize)
img_draw = ImageDraw.Draw(img)
img_draw.text((500, 1025), 'work done with love by dimaspradana.com for BMKG Long Bawan', fill='white', font=font)

img.save("img/2023.jpg")

os.remove('output.jpg')

#img.show()
