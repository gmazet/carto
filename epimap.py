# all imports should go here

import pandas as pd
import sys
#import os
#import subprocess
import datetime
#import platform
import math
#import matplotlib
#matplotlib.use('Cairo')

import matplotlib.pyplot as plt
#import seaborn as sb

import cartopy
import cartopy.crs as ccrs
from cartopy.io.img_tiles import *
import cartopy.feature as cfeature
from cartopy.io import shapereader
#from owslib.wmts import WebMapTileService
#import shapefile
from cartopy.geodesic import Geodesic
import shapely

#from matplotlib.path import Path
#import matplotlib.patheffects as PathEffects
from matplotlib import patheffects
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

#import numpy as np

try:
    evtlat=float(sys.argv[1])
    evtlon=float(sys.argv[2])
    evtdep=float(sys.argv[3])
    evtmag=float(sys.argv[4])
    evtcode=sys.argv[5]
    evtname=sys.argv[6]
    dist=float(sys.argv[7]) #in km
    zoomlevel=int(sys.argv[8]) #9, 10 or 11
except:
    print("error")
    exit()

# -------------------------------
stafile="../rms/resif.sta"
sitefile="./sites.csv"

#dist,zoomlevel=50.0,9

circles=[10.0,20.0,30.0,40.0,50.0] #km
# -------------------------------

maintitle="%s %s" % (evtcode,evtname)

deg2km=111.19
km2deg=1.0/deg2km
distdeg=dist*km2deg

latmin,latmax=evtlat-distdeg,evtlat+distdeg
#lonmin,lonmax=evtlon+distdeg,evtlon-distdeg
lonmin,lonmax=evtlon-distdeg/math.cos(evtlat/180.0*math.pi),evtlon+distdeg/math.cos(evtlat/180.0*math.pi)

print ("----------------------------------------------")
print ("lat/lon, min/max:",latmin,latmax,lonmin,lonmax)
print ("zoomlevel=",zoomlevel)
print ("dist=",dist)
print ("")

#tiler = Stamen('terrain-background')
tiler = QuadtreeTiles() # TEST
tiler = Stamen('terrain')
tiler = OSM() # TEST
tiler = GoogleTiles(style='street') # TEST

PC=ccrs.PlateCarree()
MERC=ccrs.Mercator()

#####mycrs=ccrs.Mercator()
#smallmap=ccrs.TransverseMercator()
smallmap=MERC

# -----------------------------

BORDERS2_10m = cartopy.feature.NaturalEarthFeature('cultural', 'admin_1_states_provinces_lines', '10m', edgecolor='black', facecolor='none')
BORDERS2_110m = cartopy.feature.NaturalEarthFeature('cultural', 'admin_0_boundary_lines_land', '110m', edgecolor='black', facecolor='none')
#country boundaries.
LAND_10m = cartopy.feature.NaturalEarthFeature('physical', 'land', '10m', edgecolor='face', facecolor=cartopy.feature.COLORS['land'])
#land polygons, including major islands.
RIVERS_10m = cartopy.feature.NaturalEarthFeature('physical', 'rivers_lake_centerlines', '10m', edgecolor=cartopy.feature.COLORS['water'], facecolor='none')
ROADS_10m = shapereader.natural_earth(category='cultural', name='roads', resolution='10m')
ROADS_10m = cartopy.feature.NaturalEarthFeature('cultural', 'roads', '10m')


#fig = plt.figure(figsize=(8,5))
fig = plt.figure()

# ------------------------------- Surrounding frame ------------------------------
# set up frame full height, full width of figure, this must be called first
left = -0.05
bottom = -0.05
width = 1.1
height = 1.05
rect = [left,bottom,width,height]
ax3 = plt.axes(rect)

# turn on the spines we want, ie just the surrounding frame
ax3.axis('off')
ax3.set_visible(False)
ax3.spines['right'].set_visible(True)
ax3.spines['top'].set_visible(True)
ax3.spines['bottom'].set_visible(True)
ax3.spines['left'].set_visible(True)

#ax3.text(0.01,0.01,'© Don Cameron, 2017: net-analysis.com. '+ 'Map generated at '+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), fontsize=8)
# ---------------------------------  Main Map -------------------------------------
#
# set up main map almost full height (allow room for title), right 80% of figure
left = 0.23
bottom = 0.05
width = 0.70
height = 0.85
rect = [left,bottom,width,height]

ax = plt.axes(rect, projection=MERC)
ax.set_extent((lonmin, lonmax, latmin, latmax), crs=PC)
gl=ax.gridlines(draw_labels=True, linewidth=0.6, color='lightgrey', zorder=2)
gl.xlabel_style = {'size': 8, 'color': 'grey'}
gl.ylabel_style = {'size': 8, 'color': 'grey'}


#land polygons, including major islands, use cartopy default color
ax.add_image(tiler, zoomlevel, interpolation='spline36', regrid_shape=2000, zorder=1)
###ax.coastlines(resolution='10m', zorder=2)
###ax.add_feature(RIVERS_10m)
###ax.add_feature(LAND_10m)
###ax.stock_img()
###ax.add_feature(RIVERS_10m)
###ax.add_feature(BORDERS2_10m, edgecolor='grey')


# ---------------------------
# Plot stations
# ---------------------------
#headers = ['Station', 'Latitude', 'Longitude', 'SiteName']
#dtypes = {'Station': 'str', 'Latitude': 'float', 'Longitude': 'float', 'SiteName': 'str'}
#dfsta=pd.read_csv(stafile, delimiter="|", header=0, names=headers, dtype=dtypes)
dfsta=pd.read_csv(stafile, delimiter="|", header=0)
print (dfsta)

ax.scatter([x for x in dfsta.Longitude], [y for y in dfsta.Latitude], transform=PC, s=40, c='b', marker="^", label='Stations Résif', zorder=4)
for i in range(0,len(dfsta.Latitude)):
    if ( (dfsta.Longitude[i]>lonmax) | (dfsta.Longitude[i]<lonmin) | (dfsta.Latitude[i]>latmax) | (dfsta.Latitude[i]<latmin) ):
        continue
    if (dfsta.Station[i] in ['OGS2','OGS3']):
        continue
    print ("Plot station:",i, dfsta.Longitude[i], dfsta.Latitude[i], dfsta.Station[i])
    ax.text(dfsta.Longitude[i], dfsta.Latitude[i], dfsta.Station[i] , transform=PC, horizontalalignment='left', verticalalignment='bottom', fontsize=7, zorder=5)


# ---------------------------
# Plot sites
# ---------------------------
dfsite=pd.read_csv(sitefile, delimiter=",", header=0)
print (dfsite)
for i in range(0,len(dfsite.Lat)):
    if ( (dfsite.Lon[i]>lonmax) | (dfsite.Lon[i]<lonmin) | (dfsite.Lat[i]>latmax) | (dfsite.Lat[i]<latmin) ):
        continue
    print ("Plot site:",i, dfsite.Lon[i], dfsite.Lat[i], dfsite.Site[i])
    ax.text(dfsite.Lon[i]+0.015, dfsite.Lat[i], dfsite.Site[i] , transform=PC, horizontalalignment='left', verticalalignment='bottom', fontsize=7, color='r', 
            bbox=dict(boxstyle="round", ec=(1., 0.5, 0.5), fc=(1., 0.8, 0.8),),
            zorder=10
            )
ax.scatter([x for x in dfsite.Lon], [y for y in dfsite.Lat], transform=PC, s=30, c='r', marker="D", zorder=11)

#----------------
#plt.show()
#sys.exit()
#----------------


#single-line drainages, including lake centerlines.
lon0, lon1, lat0, lat1 = ax.get_extent()

# bar offset is how far from bottom left corner scale bar is (x,y) and how far up is scale bar text
bar_offset = [0.05, 0.05, 0.07]
bar_lon0 = lon0 + (lon1-lon0)*bar_offset[0]
bar_lat0 = lat0 + (lat1-lat0)*bar_offset[1]

text_lon0 = bar_lon0
text_lat0 = lat0 + (lat1-lat0)*bar_offset[2]
bar_tickmark = 20000 # metres
bar_ticks = 5
bar_alpha = 0.3

bar_color = ['black', 'red']
# draw a scale bar that is a set of colored line segments (bar_ticks of these), bar_tickmarks long
#for i in range(bar_ticks):
    #  90 degrees = direction of horizontal scale bar
    #end_lat, end_lon = displace(bar_lat0, bar_lon0, 90, bar_tickmark)
    # capstyle must be set so line segments end square
    #TODO make transform match ax projection
    #ax.plot([bar_lon0, end_lon], [bar_lat0, end_lat], color=bar_color[i%2], linewidth=20, transform=MERC, solid_capstyle='butt', alpha = bar_alpha)
    # start of next bar is end of last bar
    #bar_lon0 = end_lon
    #bar_lat0 = end_lat

# highlight text with white background
buffer = [patheffects.withStroke(linewidth=3, foreground="w")]
# Plot the scalebar label
units = 'km'
#TODO make transform match ax projection
#t0 = ax.text(text_lon0, text_lat0, str(bar_ticks*bar_tickmark/1000) + ' ' + units, transform=MERC, horizontalalignment='left', verticalalignment='bottom', path_effects=buffer, zorder=2)

n_points=2000
for r in circles:
    r=r*1000.0 # in meters
    circle_points=Geodesic().circle(lon=evtlon, lat=evtlat, radius=r, n_samples=n_points, endpoint=False)
    geom = shapely.geometry.Polygon(circle_points)
    ax.add_geometries((geom,), crs=PC, facecolor='none', edgecolor='k', linewidth=0.5, alpha=0.5, ls='-', zorder=3)


# ---------------------------------Locating Map ------------------------
#
# set up index map 20% height, left 16% of figure
left = 0
bottom = 0.05
width = 0.16
height = 0.22
rect = [left,bottom,width,height]

ax2 = plt.axes(rect, projection=smallmap)
ax2.set_extent((-5.0, 10.0, 41.0, 52.0))
#  ax2.set_global()  will show the whole world as context

ax2.coastlines(resolution='110m', zorder=2)
ax2.add_feature(cfeature.LAND)
ax2.add_feature(BORDERS2_110m, edgecolor='grey')
#ax2.add_feature(cfeature.OCEAN)

ax2.gridlines()


lon0,lon1,lat0,lat1 = ax.get_extent()
box_x = [lon0, lon1, lon1, lon0, lon0]
box_y = [lat0, lat0, lat1, lat1, lat0]

#plt.plot(box_x, box_y, color='red',  transform=ccrs.Geodetic())
plt.plot(box_x, box_y, color='red',  transform=MERC)
# -------------------------------- Title -----------------------------
# set up map title top 4% of figure, right 80% of figure
left = 0.2
bottom = 0.95
width = 0.8
height = 0.04
rect = [left,bottom,width,height]
ax6 = plt.axes(rect)
ax6.text(0.5, 0.0,maintitle, ha='center', fontsize=13)
ax6.axis('off')
# ---------------------------------North Arrow  ----------------------------
#
left = 0
bottom = 0.4
width = 0.16
height = 0.2
rect = [left,bottom,width,height]
rect = [left,bottom,width,height]
ax4 = plt.axes(rect)

# need a font that support enough Unicode to draw up arrow. need space after Unicode to allow wide char to be drawm?
ax4.text(0.5, 0.0,u'\u25B2 \nN ', ha='center', fontsize=15, family='Arial', rotation = 0)
ax4.axis('off')
# ------------------------------------  Legend -------------------------------------

# legends can be quite long, so set near top of map (0.4 - bottom + 0.5 height = 0.9 - near top)
left = 0
bottom = 0.6
width = 0.16
height = 0.3
rect = [left,bottom,width,height]
rect = [left,bottom,width,height]
ax5 = plt.axes(rect)
ax5.axis('off')
# create an array of color patches and associated names for drawing in a legend
# colors are the predefined colors for cartopy features (only for example, Cartopy names are unusual)
colors = sorted(cartopy.feature.COLORS.keys())

# handles is a list of patch handles
handles = []
# names is the list of corresponding labels to appear in the legend
names = []

# for each cartopy defined color, draw a patch, append handle to list, and append color name to names list
for c in colors:
    patch = mpatches.Patch(color=cfeature.COLORS[c], label=c)
    handles.append(patch)
    names.append(c)
#end for
# do some example lines with colors
river = mlines.Line2D([], [], color=cfeature.COLORS['water'], marker='', markersize=15, label='river')
coast = mlines.Line2D([], [], color='black', marker='', markersize=15, label='coast')
bdy  = mlines.Line2D([], [], color='grey', marker='', markersize=15, label='state boundary')

handles.append(river)
handles.append(coast)
handles.append(bdy)
names.append('river')
names.append('coast')
names.append('state boundary')
# create legend
#ax5.legend(handles, names)
print ("Save figure...")
ax5.set_title('Legend',loc='left')
plt.savefig("./%s.png" % evtcode, dpi=120)
#plt.savefig("./%f.png" % dist, dpi=120)
#print ("show...")
#plt.show()
