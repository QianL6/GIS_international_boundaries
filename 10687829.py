"""
Understanding GIS: Assessment 1
@author [10687829]

Calculate the length of the World's Shortest Border, as fast as possible
"""
from time import time

# set start time
start_time = time()	# NO CODE ABOVE HERE

from geopandas import read_file, GeoSeries
from pyproj import Geod
from rtree import index
from matplotlib.pyplot import subplots, savefig
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.patches import Patch

#read file
world = read_file("./data/ne_10m_admin_0_countries.shp") 

# set ellipsoid
g = Geod(ellps='WGS84')

# initialise an rtree index
idx = index.Index()

# loop through each row and construct spatial index on the larger dataset	

for id, country in world.iterrows():
    idx.insert(id, country.geometry.bounds)

# set 'shortest' to store the shortest international border value of the world and set it as infinite
shortest = float("inf")

i=0

#loop each country in the world to find all international border
for id_1, country_1 in world.iterrows(): 
    # get the indexes of countries that intersect bounds of the country_1              
    possible_matches_index = list(idx.intersection(country_1.geometry.bounds))
    # use those indexes to extract the possible matches from the GeoDataFrame
    possible_matches = world.iloc[possible_matches_index]
    # then search the possible matches for precise matches using the slower but more precise method
    precise_matches = possible_matches.loc[possible_matches.intersects(country_1.geometry)]
    
    # loop each country that intersects with country_1
    for id_2, country_2 in precise_matches.iterrows():
        borders = (country_1.geometry.intersection(country_2.geometry))
        
        # select border
        if borders.type == 'MultiLineString':
            i=i+1
            # Calculate borders
            # initialise a variable to hold the cumulative length
            cumulativeLength = 0
            # loop through each segment in the line
            for segment in list(borders):
                # use g.inv to calculate the distance of each segment
	            azF, azB, distance = g.inv(segment.coords[0][0], segment.coords[0][1], segment.coords[1][0], segment.coords[1][1])

	            # add the distance to cumulative total
	            cumulativeLength = cumulativeLength + distance
            
            # store the shortest border length, the shortest border and two countries
            if cumulativeLength < shortest:
                shortest = cumulativeLength
                shortest_border = borders
                country_A = country_1
                country_B = country_2

# get the name of two countries
countryA = country_A['NAME']
countryB = country_B['NAME']

print(f"The shortest international border is {shortest}m long")
print(f"the shortest international border is the border between {countryA} and {countryB}") 
print(f"The number of cycles is i={i}")   

# ectract the country Italy and Vatican.
italy = world[(world.NAME == 'Italy')]
vatican = world[(world.NAME == 'Vatican')]

# project border
lambert_conic = '+proj=lcc +lat_1=20 +lat_2=60 +lat_0=40 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs'
shortest_border = GeoSeries(shortest_border, crs=world.crs).to_crs(lambert_conic)

# create map axis object
fig, my_ax = subplots(1, 1, figsize=(16, 10))

# remove axes
my_ax.axis('off')

# set title
my_ax.set(title=f"The shortest international border is the border between {countryA} and {countryB}. The shortest international border:{shortest}m long")
   

# set bounds (1000m buffer around the border itself, to give us some context)
buffer = 1000
my_ax.set_xlim([shortest_border.geometry.iloc[0].bounds[0] - buffer, shortest_border.geometry.iloc[0].bounds[2] + buffer])
my_ax.set_ylim([shortest_border.geometry.iloc[0].bounds[1] - buffer, shortest_border.geometry.iloc[0].bounds[3] + buffer])


# plot country
italy.to_crs(lambert_conic).plot(
    ax = my_ax,
    color = '#f0e0e0',
    edgecolor = '#f0e0e0',
    linewidth = 0.5,
    )

vatican.to_crs(lambert_conic).plot(
    ax = my_ax,
    color = '#e0e0f0',
    edgecolor = '#e0e0f0',
    linewidth = 0.5,
    )

# plot border
shortest_border.plot(
    ax = my_ax,
    edgecolor = '#21209e',
    linewidth = 2,
    )

# add north arrow
x, y, arrow_length = 0.95, 0.99, 0.1
my_ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
	arrowprops=dict(facecolor='black', width=5, headwidth=15),
	ha='center', va='center', fontsize=20, xycoords=my_ax.transAxes)

# add scalebar
my_ax.add_artist(ScaleBar(dx=1, units="m", location="lower left", length_fraction=0.25))

# manually draw a legend
my_ax.legend([
    Patch(facecolor='#f0e0e0', edgecolor='#660000', label='Italy'),
    Patch(facecolor='#e0e0f0', edgecolor='#000066', label='Vatican'),
    Patch(facecolor='#21209e', edgecolor='#21209e', label='shortest_border')],
	['Italy', 'Vatican', 'shortest_border'], loc='lower right')

# save the result
savefig('out/ass1.png', bbox_inches='tight')
print("done!")

'''ALL CODE MUST BE INSIDE HERE'''

# report runtime
print(f"completed in: {time() - start_time} seconds")	# NO CODE BELOW HERE
