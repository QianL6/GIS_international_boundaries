"""
Understanding GIS: Assessment 2
@author [10687829]

An Implementation Weighted Redistribution Algorithm (Huck et al.)
"""
from numpy import  mean, zeros
from numpy.random import uniform

from math import hypot, pi, sqrt, ceil, floor
from geopandas import read_file
from shapely.geometry import Point
from rtree import index
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from rasterio import open as rio_open
from rasterio.plot import show as rio_show
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.pyplot import subplots, savefig
from time import time



# set start time
start_time = time()	# NO CODE ABOVE HERE

'''ALL CODE MUST BE INSIDE HERE'''

def distance(a, b):
    """
	* Cartesian distance using Pythagoras
	"""
    
    return hypot(a[0] - b[0], a[1] - b[1])


def WeightedRedistribution(w,s,pointData,weightingSurface,administrativeAreas):
    # build spatial index
    idx = index.Index()
    for id, point in pointData.iterrows():
        idx.insert(id, point.geometry.bounds)
    # loop through administrative areaa in the Great Manchester
    for id, admin in administrativeAreas.iterrows():
       
        # get the bounds of the administrative area
       minx, miny, maxx, maxy = admin.geometry.bounds
       
       # get the indexes of tweet points that intersect bounds of the district
       possible_matches_index = list(idx.intersection(admin.geometry.bounds))
       # use those indexes to extract the possible matches from the GeoDataFrame
       possible_matches = points.iloc[possible_matches_index]
       # then search the possible matches for precise matches using more precise method
       precise_matches = possible_matches.loc[possible_matches.within(admin.geometry)]

       # loop through the points in the administrative area
       for id, point in precise_matches.iterrows():

              # set random_points to document the number of random points inside the admin
              random_points=0
              # store the maximum value of population density
              maximum = 0
              
              # get w random points in admin
              # loop until random points number is w
              while random_points<w+1:     
                 # calculate the random location (x and y separately)
                 xs = uniform(low=minx, high=maxx, size=1)
                 ys = uniform(low=miny, high=maxy, size=1)
               
                 p=Point(xs,ys)
                 
                 # check the random point inside admin
                 if p.within(admin.geometry):
                     # transform point coords into image space
                     P=weightingSurface.index(xs,ys)
                     
                     # get the population density value at P
                     value = weightingSurface.read(1)[P]
                     
                     # count random point
                     random_points = random_points + 1
                     
                     # select seed point with the highest population density value
                     if value > maximum:
                         seed = P
                         maximum=value

              #define x,y coordinate of seed point
              x0=mean(seed[0])
              y0=mean(seed[1])

       
              #calculate r
              r=sqrt(admin.geometry.area*s/pi) 
              #get image space value of r
              n=ceil(r/d.res[0])
              
              # define start cell
              i0=x0-n
              j0=y0-n
              #calculate v and make output map
              for i in range(2*n):
                  for j in range(2*n):
                      # check if the cell is out of the boundary of admin
                      if i0+i>0 and i0+i<d.height and j0+j>0 and j0+j<d.width:
                          Q=(i0+i,j0+j)
                          # check if the cell is in the circle
                          if distance(seed,Q) < n:
                              
                              # calculate v
                              v = 1-sqrt((n-i)*(n-i)+(n-j)*(n-j))/n
                              
                              x=int(i0+i)
                              y=int(j0+j)
                              # add v to output
                              output[(x,y)] =output[(x,y)]+v
            
           
    return output

# select British National Grid EPSG_27700 as projection
EPSG_27700 = '+proj=tmerc +lat_0=49 +lon_0=-2 +k=0.9996012717 +x_0=400000 +y_0=-100000 +ellps=airy +towgs84=446.448,-125.157,542.06,0.15,0.247,0.842,-20.489 +units=m +no_defs '
# read and project the district of the Great Manchester
GM = read_file("./data/wr/gm-districts.shp").to_crs(EPSG_27700)
# read the points of level-3 tweet
points=read_file("./data/wr/level3-tweets-subset.shp").to_crs(EPSG_27700)

#open population density map
with rio_open("./data/wr/100m_pop_2019.tif") as d:
  
    band_1=d.read(1)
    
    # create a new 'band' of raster data the same size with population density map
    output = zeros((d.height, d.width))
    
    # make hotpot redistribution map
    WeightedRedistribution(20, 0.01, points, d, GM)
        
    # output image
    fig, my_ax = subplots(1, 1, figsize=(16, 10))
    my_ax.set(title="Tweet Hotpot Redistribution")


    # plot the Great Manchester vector layer
    GM.plot(
        ax = my_ax,
        color = '#f0e0e0',
        alpha = 0.4,
        edgecolor = '#660000',
        linewidth = 0.5,
        )
    # plot the new raster layer 'output'
    rio_show(
        output,
        ax=my_ax,
        transform = d.transform,
		cmap = 'YlOrRd'
        )
    
    # add a colour bar
    fig.colorbar(ScalarMappable(norm=Normalize(vmin=floor(band_1.min()), vmax=ceil(band_1.max())), cmap='YlOrRd'), ax=my_ax)
    # add north arrow
    x, y, arrow_length = 0.97, 0.99, 0.1
    my_ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
    arrowprops=dict(facecolor='black', width=5, headwidth=15),
    ha='center', va='center', fontsize=20, xycoords=my_ax.transAxes)
    # add scalebar
    my_ax.add_artist(ScaleBar(dx=1, units="m", location="lower right"))


    # save the result
    savefig('./out/assessment2.png', bbox_inches='tight')

	
# report runtime
print(f"completed in: {time() - start_time} seconds")	# NO CODE BELOW HERE
