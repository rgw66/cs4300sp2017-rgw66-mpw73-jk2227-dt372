from __future__ import print_function
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pickle
import boto3
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

try:
  sid = SentimentIntensityAnalyzer()
except:
  nltk.download("vader_lexicon")
  sid = SentimentIntensityAnalyzer()

ta_listings = pickle.load(open("data/tripadvisor_hotel_info.pickle", 'rb'))
airbnb_listings = pickle.load(open("data/airbnb_listings.pickle", 'rb'))

ta_index_to_listing = pickle.load(open("data/ta_index_to_listing.pickle"))
airbnb_mat_index_to_listing = pickle.load(open("data/airbnb_mat_index_to_listing.pickle"))
ta_mat_index_to_listing = pickle.load(open("data/ta_mat_index_to_listing.pickle"))
ta_lda_ht = pickle.load(open("data/ta_lda_ht.mat"))
ta_lda_tt = pickle.load(open("data/ta_lda_tt.mat"))
airbnb_lda_ht = pickle.load(open("data/airbnb_lda_ht.mat"))
airbnb_lda_tt = pickle.load(open("data/airbnb_lda_tt.mat"))

BUCKET_NAME = 'cs4300-dream-team'

ACCESS_KEY = 'AKIAJ55CDKOUVGR3GE3Q'
SECRET_KEY = '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'

S3 = boto3.resource('s3',
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY)

CLIENT = boto3.client('s3',
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY)


def get_reviews(site,ind_lst):
    # site = "airbnb" or "ta" 
    sorted_lst = sorted(ind_lst, reverse = True)
    clustered_lst = []
    lower = 0 
    upper = lower + 499
    tmp = []
    while sorted_lst != []: 
        ind = sorted_lst.pop() 
        if ind > upper: 
            clustered_lst.append(tmp)
            lower = upper + 1
            upper = lower + 499
            tmp = [ind]
        else: 
            tmp.append(ind)
    clustered_lst.append(tmp)

    reviews = []

    for cluster in clustered_lst:
        for ind in cluster:
            page_lower = ind/500 * 500 
            page_upper = page_lower + 499
            ind_in_page = ind % 500
            page_key = "/{}_reviews/{}_review_{}-{}.txt".format(site,site,page_lower,page_upper)
            with open('tmp.p', 'wb') as data:
                CLIENT.download_fileobj(BUCKET_NAME,page_key,data)
            with open('tmp.p', 'rb') as data: 
                lst = pickle.load(data)
            reviews.append(lst[ind_in_page])

    return reviews


def search_lda(query, vectorizer, ht_mat, tt_mat, mat_to_listing_dict, top_k=10):
    vec = vectorizer.transform([query]).todense().T
    results = np.dot(ht_mat, np.dot(tt_mat, vec)).T
    indices = np.squeeze(np.asarray(np.argsort(results)))[::-1].T[:top_k]
    scores = np.squeeze(np.asarray(np.sort(results)))[::-1].T[:top_k]

    explanation = np.squeeze(np.asarray(np.multiply(np.dot(ht_mat, tt_mat), vec.T)[indices, :]))
    #     print_top_words(explanation, airbnb_tfidf_feature_names, 10)

    listings = np.zeros(indices.shape)
    for i in range(indices.shape[0]):
        listings[i] = mat_to_listing_dict[indices[i]]
    return (listings.tolist(), indices.tolist(), scores.tolist())


def get_airbnb_results(query):
    airbnb_vectorizer = pickle.load(open("data/airbnb_vectorizer.pickle", "rb"))
    listings, indices, scores = search_lda(query,
                                           airbnb_vectorizer,
                                           airbnb_lda_ht,
                                           airbnb_lda_tt,
                                           airbnb_mat_index_to_listing)
    ordered_listings = []
    for (l, ind, score) in zip(listings, indices, scores):
        listing_id = str(int(l))
        airbnb_listing_info = airbnb_listings[listing_id]
        ordered_listings.append({
            'name': airbnb_listing_info['name'],
            'listing_url': airbnb_listing_info['listing_url'],
            'image_url': airbnb_listing_info['picture_url'],
            'score': str(score)
        })
    del airbnb_vectorizer
    return ordered_listings

def get_hotel_results(query):
    ta_vectorizer = pickle.load(open("data/ta_vectorizer.pickle", 'rb'))
    listings, indices, scores = search_lda(query,
                                           ta_vectorizer,
                                           ta_lda_ht,
                                           ta_lda_tt,
                                           ta_mat_index_to_listing)
    ordered_listings = []

    for (l, ind, score) in zip(listings, indices, scores):
        name = ta_index_to_listing[int(l)]
        ordered_listings.append({
            'name': name,
            'listing_url': ta_listings[name][0],
            'image_url': '/static/img/tripadvisor1600.png',
            'score': str(score)
        })
    del ta_vectorizer
    return ordered_listings

