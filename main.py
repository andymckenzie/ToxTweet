#!/usr/bin/env python
import twitterQuery as tQ
import numpy as np
import matplotlib.pyplot as plt
import sys
from cPickle import dump, load
import xlrd


#--Formulary lists the "drugs" to search for on Twitter

#location = 

#formulary = ['cocaine','marijuana','bath salts','heroin','lsd','valium','ativan','ecstasy','ketamine']
formulary = ['coffee', 'marijuana']

'''
locations = {
					'NYC': '40.665572,-73.923557',
					'SF': '37.7750,-122.4183'
					}
'''
filename = 'zipcodes_cities.xls'

def grab_locs_from(filename):
	wb = xlrd.open_workbook(filename)
	#ZIP code is col 1, Lat is col 4, long is col 5
	#grab first sheet
	sh = wb.sheet_by_index(0)
	zipcodes = sh.col_values(0)
	latitudes = sh.col_values(3)
	longis = sh.col_values(4)
	return {str(int(zipcode)):','.join([str(lat),str(lon)]) for zipcode,lat,lon in zip(zipcodes,latitudes,longis)}
	
locations = grab_locs_from(filename)
print locations

graph_stats = []
for count,drug in enumerate(formulary):
	print 'Querying Twitter for ',drug,' and writing the results to an XLS file.'
	query = tQ.twitterQuery(drug,locations)
#	degree,path_length = query.make_graph()
#	print 'Finding the Retweet Graph. Saving it and a rank-sorted histogram of the degrees of its nodes.'
#	graph_stats.append((degree,path_length))

'''
with open('graph_stats.p','wb') as file:
	dump([formulary,graph_stats],file)

fig = plt.figure()
ax1 = fig.add_subplot(211)
ax1.boxplot([data[0] for data in graph_stats])
ax2 = fig.add_subplot(212)
ax2.boxplot([data[1] for data in graph_stats]) 
plt.title('Graph theoretic differences among commonly abused drugs.')
ax2.xaxis.set_ticks(range(1,len(formulary)+1),formulary)

plt.savefig('summary.png',dpi=300)
#plt.show()
'''
