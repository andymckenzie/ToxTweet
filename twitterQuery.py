#!/usr/bin/env python
# Using twitter instead of python-twtter wrapper
import twitter
import networkx as nx
import re
import codecs
import nltk
import csv
import xlwt
import itertools
from httplib import BadStatusLine
class twitterQuery(object):
	def __init__ (self, drug_name, locations):
		#assigning the drug name used in this particular twitter search
		self.drug_name = drug_name
		self.locations = locations
		print self.drug_name
		#try executes a block of code. if error occurs it returns the error and keeps going through the script instead of stopping
		try: #Look for a list of synonyms. If no list is found search Twitter just using the drug name
			self.synonym_filename = self.drug_name + '_synonyms.csv'
			self.synonyms = [line for line in csv.reader(open(self.synonym_filename,'rt'))]
			#flattening the list; type of list comprehension
			self.synonyms = [synonym for line in self.synonyms for synonym in line]
		except IOError as e:
			self.synonyms = []
			self.synonyms.append(self.drug_name)
             # Calling list(self.drug_name) splits the string into a list of characters 
        #Assume that the synonyms are stored in a CSV file
        #Query Twitter with those synonyms-------------------------------------
		#right now twitter keys set to public
		#method is cap Twitter, calling the object (aka module) lower case twitter
		#this is initialization
		self.search = twitter.Twitter(domain="search.twitter.com")
		self.results = []
		#by making it a self you are turning page_count into somewhat more of a "global" variable
		#if you made self page_count higher you can get more results, but you're still limited by twitter to some extent
		self.page_count = 10
		#radius around the location in miles; 
		self.radius = 10    
  		#by expanding this line, can iterate over locations
		#could modify to search over later locations
		
		#results per page
		self.rpp = 100
		#making a string with elements of the synonyms, which you input to twitter as an inclusive OR
		#joining the elements with that string btwn them
		self.query = ' OR'.join(self.synonyms)
        

		self.dial_in_tries = 4 #Sometimes Twitter's API flips a BadStatusLine error

		for attempt in range(self.dial_in_tries):
			try:
				self.iterator = [(location,geocode) for location,geocode in self.locations.iteritems()]
				self.results = [[self.search.search(q=self.query,rpp=self.rpp,page=page, geocode=geocode+','+str(self.radius)+'mi') for page in range(1,self.page_count+1)] for _,geocode in self.iterator]
				break
			except BadStatusLine,e:
				continue
		'''
		for attempt in range(self.dial_in_tries):
			try:
				for geocode,location in self.locations.iteritems(): 
					for page in range(1,self.page_count+1): # Python countings from 0. Twitter from one.
						self.results.append(self.search.search(q=self.query, 
						rpp=self.rpp,page=page, geocode=self.geocode+','+str(self.radius)+'mi'))
						break
					
			except BadStatusLine,e:
				continue
		'''
		print len(self.results)		
		#self.save(format='XLS')
		self.save(format='JSON')
	
	def clean(self,tweet):
		#verboten is german for "forbidden"; getting rid of the parts of tweets with url's and these other characters
		verboten = ['@','RT','http://']
		handles = set(filter(lambda x: 1 in [symbol in x for symbol in verboten], tweet.split(' ')))
		return ' '.join([word for word in tweet.split(' ') if word not in handles]).lower()
   
	def save(self, format='XLS'):
		for key,location in enumerate(self.results):
			if format == 'XLS': #Saving to an XLS file for human rating
				import xlwt as xlwt
				corpus = [tweet['text'] for page in location for tweet in page['results']]
	           #Make XLS Workbook with a sheet for everyone
				self.xls_wbk = xlwt.Workbook()
				self.everyone = {'Nick','Alex','Dan','Jen','Mike'}
				self.column = 1
				for person in self.everyone:
					sheet = self.xls_wbk.add_sheet(person)
					for row,tweet in enumerate(map(self.clean,set(corpus))):
						sheet.write(row,self.column,tweet)
				self.xls_wbk.save(self.drug_name.replace(' ','_')+'_for_rating.xls')
			elif format == 'JSON': #Dumping tweets, for say graph theory analysis
				from simplejson import dump
				self.record_filename = 'results_'+self.drug_name.replace(' ','_')+self.iterator[key][0]+'.txt'
				with open(self.record_filename,'a') as record:
					dump(location,record)
    
	def get_rt_sources(self,tweet):
		re_patterns = re.compile(r'(RT|via)((?:\b\W*@\w+)+)')
		return [source.strip() for entry in re_patterns.findall(tweet)
					for source in entry if source not in ("RT","via")]
    
	#def get_tweet_text(self,tweet):
	#	re_pattern = re.compile(", ""text":)
	#	return [source.strip() for entry in re_pattern.findall(tweet)
	#				for source in entry if source not in ()]	



	def make_graph(self,save_graph=True):
		self.da = []
		for key,location in enumerate(self.results):
			print '************'
			print key
			print '**************'
			graph = nx.DiGraph()
			all_tweets = []
			#for place in self.results:
				#what is page['results'] below? is it a list?
				#when I print the below, only get a new line at the end, suggesting it's just one blob
			#for page in self.results:
			#	print page['results']
			#	print '\n''\n'
			#	break
			#see http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
			all_tweets = [tweet for page in location for tweet in page['results']]
		
			corpus = [tweet['text'] for page in location for tweet in page['results']]
			corpus_str = map(lambda x: self.clean(x).split(),corpus)
			corpus_str = [item for sublist in corpus_str for item in sublist]
		
			corpus_str = [word for word in corpus_str if 3 <= len(word) and word.isalnum()]
				
			self.fdist = nltk.FreqDist(corpus_str)
		
			#self.fdist.plot(50,cumulative=True)
			
			
			
			fp = codecs.open("%s_%s.freqdist"%(self.drug_name.replace(' ','_'),self.iterator[key][0]),"wb",'utf-8')
			
			fp.write('\n'.join('%s %s' % x for x in self.fdist.iteritems()))
			
			#save this to a file, then read the results between drugs pairwise and compares counts of same words (e.g., union and difference, set module)
		
			#for word in tokenize.corpus(sent):
			#	fdist.inc(word.lower())
		
			#print self.fdist

			#tweet_text_corpus = []
		
			#for tweet in all_tweets: 
			
			
			#	for text in tweet_text:
			#		tweet_text_corpus.append(text)
		
			#print tweet_text_corpus		
			
			for tweet in all_tweets:
				rt_sources = self.get_rt_sources(tweet["text"])
				if not rt_sources: continue 
				for rt_source in rt_sources:
					graph.add_edge(rt_source, tweet["from_user"], {"tweet_id": tweet["id"]})
	        #--Calculate graph summary statistics
			if nx.is_connected(graph.to_undirected()):
				diameter  = nx.diameter(graph.to_undirected())         
				average_shortest_path = nx.average_shortest_path_length(graph.to_undirected())
				print 'Diameter: ', diameter
				print 'Average Shortest Path: ',average_shortest_path
			else:
				print "Graph is not connected so calculating the diameter and average shortest path length on all connected components."
				diameter = []
				average_shortest_path = []
				for subgraph in nx.connected_component_subgraphs(graph.to_undirected()):
					diameter.append(nx.diameter(subgraph))
					average_shortest_path.append(nx.average_shortest_path_length(subgraph))
				from numpy import median
				from scipy.stats import scoreatpercentile
				print 'Diameter: ',median(diameter),u'\xB1',str(scoreatpercentile(diameter,75)-scoreatpercentile(diameter,25))
				print 'Average Path Length :',median(average_shortest_path),u'\xB1',str(scoreatpercentile(average_shortest_path,75)-scoreatpercentile(average_shortest_path,25))
			degree_sequence=sorted(nx.degree(graph).values(),reverse=True) # degree sequence
           
			import matplotlib.pyplot as plt
			plt.loglog(degree_sequence,'b-',marker='o')
			plt.title("Distribution of Degrees for %s tweets" %(self.drug_name), fontsize=20)
			plt.ylabel("Degree", fontsize=20)
			plt.xlabel("Rank", fontsize=20)
        
	        # draw graph in inset
			ax = plt.axes([0.35,0.25,0.55,0.55])
			plt.axis('off')
			#nx.draw(graph, ax=ax, alpha=0.8, with_labels=False)
        
			plt.savefig("degree_distribution_%s_%s.png"%(self.drug_name.replace(' ','_'),self.iterator[key][0]), dpi=300)
			plt.close()
			if save_graph:
				output_file = self.drug_name.replace(' ','_') +self.iterator[key][0]+ '.dot'
				try:
					nx.drawing.write_dot(graph,output_file)
					print 'Graph saved as ',output_file
				except (ImportError, UnicodeEncodeError) as e:
					dot = ['"%s" -> "%s" [tweetid=%s]' % (node1,node2,graph[node1][node2]['tweet_id']) 
							for node1,node2, in graph.edges()]
					with codecs.open(output_file,'w', encoding='utf-8') as f:
						f.write('strict digraph G{\n%s\n}' % (';\n'.join(dot),))
						print 'Saved ',output_file,' by brute force'
				#self.da.append[(diameter,average_shortest_path)]
		return self.da
			
