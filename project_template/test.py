# from .models import Docs
# import os
# import Levenshtein
# import json
# import numpy as np
# from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
# import nltk
# from nltk.sentiment.vader import SentimentIntensityAnalyzer
# import cPickle as pickle
# from scipy.sparse.linalg import svds
# from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
#
# try:
#     sid = SentimentIntensityAnalyzer()
# except:
#     nltk.download("vader_lexicon")
#     sid = SentimentIntensityAnalyzer()
#
#
# def get_hotel_tuples(hotel_information, ta_reviews):
#     hotel_to_key_index = {}
#     index_to_hotel = {}
#     reviews = []
#     i = 0
#     index_to_hotel = {}
#     for hotel_name in hotel_information:
#         hotel_to_key_index[hotel_name] = i
#         i += 1
#     i = 0
#     for ta_review in ta_reviews:
#         reviews.append(ta_review['review'])
#         index_to_hotel[i] = hotel_to_key_index[ta_review['hotel_name']]
#         i += 1
#     return (hotel_to_key_index,
#             index_to_hotel,
#             reviews)
#
#
# def get_airbnb_tuples(airbnb_reviews):
#     r = []
#     i = 0
#     index_to_listing = {}
#     for listing_id, reviews in airbnb_reviews.items():
#         for review in reviews:
#             r.append(review)
#             index_to_listing[i] = listing_id
#             i += 1
#     return (index_to_listing, r)
#
#
# def search_svd(query, mapping, vectorizer, words_compressed, docs_compressed, top_k=10):
#     vec = vectorizer.transform([query])
#     results = np.dot(vec * words_compressed, docs_compressed)
#     indices = np.squeeze(np.asarray(np.argsort(results)[:, ::-1][:, :top_k]))
#     scores = np.squeeze(np.asarray(np.sort(results)[:, ::-1][:, :top_k]))
#     listings = np.zeros(indices.shape)
#     for i in range(indices.shape[0]):
#         listings[i] = mapping[indices[i]]
#     return (listings.tolist(), indices.tolist(), scores.tolist())
#
#
# def get_airbnb_results(query, airbnb_reviews, airbnb_listings, index_to_listing, vectorizer, words_compressed,
#                        docs_compressed):
#     airbnb_results = []
#     listings, indices, scores = search_svd(query, index_to_listing, vectorizer, words_compressed, docs_compressed)
#     for (l, ind, score) in zip(listings, indices, scores):
#         listing_id = str(int(l))
#         airbnb_listing_info = airbnb_listings[listing_id]
#         print "Listing ID: " + listing_id
#         print "Listing Name: " + airbnb_listing_info['name']
#         print "Review : \n" + airbnb_reviews[ind]
#         print "Listing URL: " + airbnb_listing_info['listing_url']
#         print "Image URL: " + airbnb_listing_info['picture_url']
#         print "Score (Similarity): " + str(score)
#         print sid.polarity_scores(airbnb_reviews[ind])['compound']
#         print "**************"
#         airbnb_results.append({
#             "id": listing_id,
#             "name": airbnb_listing_info['name'],
#             "review": airbnb_reviews[ind],
#             "listing_url": airbnb_listing_info['listing_url'],
#             "image_url": airbnb_listing_info['picture_url'],
#             "score": score,
#             "sentiment_analysis_score": sid.polarity_scores(airbnb_reviews[ind])['compound']
#         });
#     return airbnb_results
#
#
# def get_hotel_results(query, ta_reviews, hotel_information, index_to_hotel, vectorizer, words_compressed,
#                       docs_compressed):
#     hotel_results = []
#     hotels, indices, scores = search_svd(query, index_to_hotel, vectorizer, words_compressed, docs_compressed)
#     hotel_keys = hotel_information.keys()
#     for (l, ind, score) in zip(hotels, indices, scores):
#         hotel_id = int(l)
#         review_info = ta_reviews[ind]
#         hotel_info = hotel_information[hotel_keys[hotel_id]]
#         print "Hotel ID: %i" % hotel_id
#         print "Hotel name: " + hotel_keys[hotel_id]
#         print "Review Title: " + review_info['title']
#         print "Review: \n" + review_info['review']
#         print "Hotel URL: " + hotel_info[0]
#         print "Score (Similarity): " + str(score)
#         print sid.polarity_scores(review_info['review'])['compound']
#         print "**************"
#         hotel_results.append({
#             "id": hotel_id,
#             "name": hotel_keys[hotel_id],
#             "review_title": review_info['title'],
#             "review": review_info['review'],
#             "listing_url": hotel_info[0],
#             "score": score,
#             "sentiment_analysis_score": sid.polarity_scores(review_info['review'])['compound']
#         });
#     return hotel_results
#
#
# with open('data/tripadvisor_reviews.pickle', 'rb') as f:
#     ta_reviews_data = pickle.load(f)
#
# with open('data/tripadvisor_hotel_info.pickle', 'rb') as f:
#     hotel_information = pickle.load(f)
#
# (hotel_to_key_index, index_to_hotel, ta_reviews) = get_hotel_tuples(hotel_information, ta_reviews_data)
#
# ta_vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7)
# ta_tfidf = ta_vectorizer.fit_transform(ta_reviews)
#
# # words_compressed_ta, _, docs_compressed_ta = svds(ta_tfidf, k=10)
# docs_compressed_ta, _, words_compressed_ta = svds(ta_tfidf, k=10)
# docs_compressed_ta = docs_compressed_ta.T
# words_compressed_ta = words_compressed_ta.T
#
# # with open('data/10_by_docs_svd_ta.pickle','rb') as f:
# #  words_compressed_ta = pickle.load(f)
#
# # with open('data/words_by_10_svd_ta.pickle','rb') as f:
# #  docs_compressed_ta = pickle.load(f)
#
# with open('data/airbnb_reviews.pickle', 'rb') as f:
#     airbnb_reviews_data = pickle.load(f)
#
# with open('data/airbnb_listings.pickle', 'rb') as f:
#     listings_information = pickle.load(f)
#
# (index_to_listing, airbnb_reviews) = get_airbnb_tuples(airbnb_reviews_data)
#
# airbnb_vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7)
# airbnb_tfidf = airbnb_vectorizer.fit_transform(airbnb_reviews)
#
# docs_compressed_airbnb, _, words_compressed_airbnb = svds(airbnb_tfidf, k=10)
# docs_compressed_airbnb = docs_compressed_airbnb.T
# words_compressed_airbnb = words_compressed_airbnb.T

