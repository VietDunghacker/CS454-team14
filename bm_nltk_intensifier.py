import argparse
import time
import nltk
from nltk.corpus import wordnet
from nltk.corpus import inaugural
from nltk import word_tokenize

from nltk.corpus import stopwords
from nltk import FreqDist
from nltk.collocations import *

stop_words = set(stopwords.words('english'))
all_synsets = [synset for synset in list(wordnet.all_synsets('r'))]

# remove all stop words from a list of words
def preprocess_corpus(word_list):
	results = []
	for w in word_list:
		w_new = w.lower()
		if w_new.isalnum():
			if not w_new in stop_words:
				results.append(w_new)
	return results

def filter_contains(s):
	tokens = word_tokenize(s)
	intensifer_specific = ['degree', 'intensifier', 'intensifiers']
	manner_specific = ['manner']
	if (intensifer_specific[0] in tokens or intensifer_specific[1] in tokens or intensifer_specific[2] in tokens) and \
			manner_specific[0] not in tokens:
		return 1
	return -1

def filter_one_word(w):
	synsets = wordnet.synsets(w, wordnet.ADV)
	be_intensifer = 0
	for synset in synsets:
		definition = synset.definition()
		if filter_contains(definition) == 1:
			be_intensifer += 1
	if be_intensifer > 0:
		return 1
	return -1

def get_all_intensifier():
	choosen_adverbs = []
	for synset in all_synsets:
		definition = synset.definition()
		if filter_contains(definition) == 1:
			choosen_adverbs += synset.lemma_names()
	double_filter = []
	for adverb in choosen_adverbs:
		if filter_one_word(adverb) == 1 and '_' not in adverb:
			double_filter.append(adverb)
	final_list = [w for w in double_filter if not w in stop_words]
	return list(set(final_list))

def filter_contains_scoring(s):
	tokens = word_tokenize(s)
	intensifer_specific = ['degree', 'intensifier', 'intensifiers']
	manner_specific = ['manner']
	if intensifer_specific[1] in tokens or intensifer_specific[2] in tokens:
		return 1
	if manner_specific[0] in tokens:
		return 0
	if intensifer_specific[0] in tokens:
		return 0.5
	return 0

def filter_one_word_scoring(w):  # for an adverb from the list of chosen adverbs
	synsets = wordnet.synsets(w, wordnet.ADV)
	if len(synsets) == 0:
		return 0
	be_intensifer_scoring = 0
	for synset in synsets:
		definition = synset.definition()
		if filter_contains_scoring(definition) == 1:
			return 1
		else:
			be_intensifer_scoring += filter_contains_scoring(definition)
	return be_intensifer_scoring / len(synsets)  # in the case there is no intensifier term in the definition string

def get_all_intensifier_scoring():
	choosen_adverbs = get_all_intensifier()
	double_filter = []
	for adverb in choosen_adverbs:
		score = filter_one_word_scoring(adverb)
		if score > 0 and '_' not in adverb:
			double_filter.append((score, adverb))
	final_list = [w for w in double_filter if not w in stop_words]
	return final_list

def test_nltk(count):
	times = []
	for i in range(count):
		t0 = time.time()
		get_all_intensifier_scoring()
		t1 = time.time()
		times.append(t1 - t0)
	return sum(times)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--piacin', dest='piacin', action='store_const', const=True, default=False, help='Use piacin')
	parser.add_argument('--clear', dest='clear', action='store_const', const=True, default=False, help='Clear piacin bag')
	parser.add_argument("-k", "--bmnumber", type=int, default=100, help="Number of time to repeat benchmark within run (default: 100)")

	args = parser.parse_args()

	if args.piacin:
		import piacin.sa

	print(test_nltk(args.bmnumber))