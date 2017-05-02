from .models import Docs
import os
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
		i += 1 
	return (hotel_to_key_index,
		index_to_hotel, 
		reviews)

def get_airbnb_tuples(airbnb_reviews):
	r = []
	i = 0
	index_to_listing = {}
	for listing_id, reviews in airbnb_reviews.items():
		for review in reviews: 
			r.append(review)
			index_to_listing[i] = listing_id
			i += 1
	return (index_to_listing, r)

def search_svd(query, mapping, vectorizer, words_compressed, docs_compressed, top_k = 10):
    vec = vectorizer.transform([query])
    results = np.dot(vec * words_compressed, docs_compressed)
    indices = np.squeeze(np.asarray(np.argsort(results)[:,::-1][:,:top_k]))
    scores = np.squeeze(np.asarray(np.sort(results)[:,::-1][:,:top_k]))
    listings = np.zeros(indices.shape)
    for i in range(indices.shape[0]):
        listings[i] = mapping[indices[i]]
    return (listings.tolist(), indices.tolist(), scores.tolist())

def get_airbnb_results(query, airbnb_reviews, airbnb_listings, index_to_listing, vectorizer, words_compressed, docs_compressed):
	airbnb_results = [] 
	listings, indices, scores = search_svd(query, index_to_listing, vectorizer, words_compressed, docs_compressed)
	for (l, ind, score) in zip(listings, indices, scores):
		listing_id = str(int(l))
		airbnb_listing_info = airbnb_listings[listing_id]
		airbnb_results.append({
			"id": listing_id, 
			"name": airbnb_listing_info['name'],
			"review": airbnb_reviews[ind],
			"listing_url": airbnb_listing_info['listing_url'],
			"image_url": airbnb_listing_info['picture_url'],
			"score": score,
			"sentiment_analysis_score": 0
			});
	return airbnb_results 

def get_hotel_results(query, ta_reviews, hotel_information, index_to_hotel, vectorizer, words_compressed, docs_compressed):
	hotel_results = []
	hotels, indices, scores = search_svd(query, index_to_hotel, vectorizer, words_compressed, docs_compressed)
	hotel_keys = hotel_information.keys()
	for (l, ind, score) in zip(hotels, indices, scores):
		hotel_id = int(l)
		review_info = ta_reviews[ind]
		hotel_info = hotel_information[hotel_keys[hotel_id]]

		hotel_results.append({
			"id": hotel_id,
			"name": hotel_keys[hotel_id],
			"review_title": review_info['title'],
			"review": review_info['review'],
			"listing_url": hotel_info[0],
			"score": score,
			"sentiment_analysis_score": 0
			});
	return hotel_results

