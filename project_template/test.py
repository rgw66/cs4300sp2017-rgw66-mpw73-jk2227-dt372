from .models import Docs
import os
import Levenshtein
import json
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer


def get_hotel_tuples(hotel_information, ta_reviews):
	hotel_to_key_index = {} 
	index_to_hotel = {}
	reviews = [] 
	i = 0 
	index_to_hotel = {} 
	for hotel_name in hotel_information:
		hotel_to_key_index[hotel_name] = i 
		i += 1
	i = 0 
	for ta_review in ta_reviews: 
		reviews.append(ta_review['review'])
		index_to_hotel[i] = hotel_to_key_index[ta_review['hotel_name']]
	print "lol"
	print len(reviews)
	return (hotel_to_key_index,
		index_to_hotel, 
		reviews)

def read_file(n):
	path = Docs.objects.get(id = n).address;
	file = open(path)
	transcripts = json.load(file)
	return transcripts

def _edit(query, msg):
    return Levenshtein.distance(query.lower(), msg.lower())

def search_svd(query, vectorizer, words_compressed, docs_compressed, top_k = 10):
    vec = vectorizer.transform([query])
    results = np.dot(vec * words_compressed, docs_compressed)
    indices = np.squeeze(np.asarray(np.argsort(results)[:,::-1][:,:top_k]))
    scores = np.squeeze(np.asarray(np.sort(results)[:,::-1][:,:top_k]))
    listings = np.zeros(indices.shape)
    for i in range(indices.shape[0]):
        for j in range(indices.shape[1]):
            listings[i,j] = index_to_hotel[indices[i,j]]
    return (listings, indices, scores)

def get_hotel_results(query, ta_reviews, hotel_information, vectorizer, words_compressed, docs_compressed):
	hotels, indices, scores = search_svd(query, vectorizer, words_compressed, docs_compressed)
	hotel_keys = hotel_information.keys()
	for (l,ind, score) in zip(hotels, indices, scores):
		hotel_id = int(l)
        review_info = ta_reviews[ind] 
        hotel_info = hotel_information[hotel_keys[hotel_id]]
        print("Hotel ID: %i" % hotel_id)
        print ("Hotel name: " + hotel_keys[hotel_id])
        print ("Review Title: %s" % review_info['title'])
        print("Review: \n" + review_info['review'])
        print ("Hotel URL: " + hotel_info[0])
        print("Score (Similarity): " + str(score))
        print("**********************")

def find_similar(q):
	transcripts = read_file(1)
	result = []
	for transcript in transcripts:
		for item in transcript:
			m = item['text']
			result.append(((_edit(q, m)), m))

	return sorted(result, key=lambda tup: tup[0])

