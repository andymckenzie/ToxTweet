#!/usr/bin/env python
filenames = ['coffee_SF.freqdist','coffee_NYC.freqdist']

wordlists = [map(lambda x: x.rstrip('\n'),open(filename,'rb').readlines()) for filename in filenames]

wordlists = [[filter(lambda x: not x.isdigit(),word) for word in wordlist] for wordlist in wordlists]
wordlists = map(set,wordlists)

#print wordlists


answers = [[(first.difference(second),first.intersection(second)) for first in wordlists] for second in wordlists]

#print answers[0][0][0]
