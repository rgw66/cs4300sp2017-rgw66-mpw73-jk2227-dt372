from __future__ import print_function
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pickle

# load in
ta_data = pickle.load(open("data/tripadvisor_reviews.pickle", 'rb'))
airbnb_data = pickle.load(open("data/airbnb_reviews.pickle", 'rb'))
ta_listings = pickle.load(open("data/tripadvisor_hotel_info.pickle", 'rb'))
airbnb_listings = pickle.load(open("data/airbnb_listings.pickle", 'rb'))

ta_listing_to_index = {}
ta_index_to_listing = {}
for i,d in enumerate(ta_listings.items()):
    ta_listing_to_index[d[0]] = i
    ta_index_to_listing[i] = d[0]

ta_reviews = []
ta_adj_mat = np.zeros((len(ta_listing_to_index), len(ta_data)))
for j,d in enumerate(ta_data):
    i = ta_listing_to_index[d['hotel_name']]
    ta_reviews.append(d['review'])
    ta_adj_mat[i,j] += 1

ta_mat_index_to_listing = {}
for i,_ in enumerate(ta_listings.items()):
    ta_mat_index_to_listing[i] = i

airbnb_index_to_listing = {}
airbnb_listing_to_mat_index = {}
airbnb_mat_index_to_listing = {}
airbnb_reviews = []
i = 0
for (ind, (listing_id, reviews)) in enumerate(airbnb_data.items()):
    for review in reviews:
        airbnb_reviews.append(review)
        airbnb_listing_to_mat_index[listing_id] = ind
        airbnb_mat_index_to_listing[ind] = listing_id
        airbnb_index_to_listing[i] = listing_id
        i += 1
count = i
airbnb_adj_mat = np.zeros((len(airbnb_data),i))
for (j, l) in airbnb_index_to_listing.items():
    airbnb_adj_mat[airbnb_listing_to_mat_index[l],j] += 1

total_adj_mat = np.zeros((len(ta_listing_to_index)+len(airbnb_data),len(ta_data)+count))
total_index_to_listing = {}
total_mat_index_to_listing = {}
for j,d in enumerate(ta_data):
    i = ta_listing_to_index[d['hotel_name']]
    ta_adj_mat[i,j] += 1
    total_mat_index_to_listing[i] = i
for (j, l) in airbnb_index_to_listing.items():
    row = len(ta_listing_to_index)+airbnb_listing_to_mat_index[l]
    col = len(ta_data)+j
    total_adj_mat[row,col] += 1
    total_mat_index_to_listing[row] = l
ta_vectorizer = TfidfVectorizer(stop_words='english', min_df=0.05, max_df=0.9)
airbnb_vectorizer = TfidfVectorizer(stop_words='english', min_df=0.05, max_df=0.9)
total_vectorizer = TfidfVectorizer(stop_words='english', min_df=0.05, max_df=0.9)

ta_tfidf = ta_vectorizer.fit_transform(ta_reviews)
airbnb_tfidf = airbnb_vectorizer.fit_transform(airbnb_reviews)

ta_tfidf_feature_names = ta_vectorizer.get_feature_names()
airbnb_tfidf_feature_names = airbnb_vectorizer.get_feature_names()

total_tfidf = total_vectorizer.fit_transform(ta_reviews + airbnb_reviews)
total_tfidf_feature_names = total_vectorizer.get_feature_names()

ta_lda_ht = pickle.load(open("data/ta_lda_ht.mat"))
ta_lda_dt = pickle.load(open("data/ta_lda_dt.mat"))
ta_lda_tt = pickle.load(open("data/ta_lda_tt.mat"))
airbnb_lda_ht = pickle.load(open("data/airbnb_lda_ht.mat"))
airbnb_lda_dt = pickle.load(open("data/airbnb_lda_dt.mat"))
airbnb_lda_tt = pickle.load(open("data/airbnb_lda_tt.mat"))
total_lda_ht = pickle.load(open("data/total_lda_ht.mat"))
total_lda_dt = pickle.load(open("data/total_lda_dt.mat"))
total_lda_tt = pickle.load(open("data/total_lda_tt.mat"))

def print_top_words(mat, feature_names, n_top_words):
    for topic_idx, topic in enumerate(mat):
        print("Rank #%d:" % topic_idx)
        indices = topic.argsort()[:-n_top_words - 1:-1]
        print(" ".join([feature_names[i] for i in indices if topic[i] > 0]))
    print()


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

listings, indices, scores = search_lda("quiet neat cozy clean comfortable close",
                                       airbnb_vectorizer,
                                       airbnb_lda_ht,
                                       airbnb_lda_tt,
                                       airbnb_mat_index_to_listing)


def get_airbnb_results(query):
    listings, indices, scores = search_lda(query,
                                           airbnb_vectorizer,
                                           airbnb_lda_ht,
                                           airbnb_lda_tt,
                                           airbnb_mat_index_to_listing)
    ordered_listings = []
    for (l, ind, score) in zip(listings, indices, scores):
        listing_id = str(int(l))
        airbnb_listing_info = airbnb_listings[listing_id]
        # print("Listing ID: " + listing_id)
        # print("Listing Name: " + airbnb_listing_info['name'])
        # print("Listing URL: " + airbnb_listing_info['listing_url'])
        # print("Image URL: " + airbnb_listing_info['picture_url'])
        # print("Score (Similarity): " + str(score))
        # print("**************")
        # print(airbnb_listing_info)
        ordered_listings.append({
            'name': airbnb_listing_info['name'],
            'listing_url': airbnb_listing_info['listing_url'],
            'image_url': airbnb_listing_info['picture_url'],
            'score': str(score)
        })

    return ordered_listings

def get_hotel_results(query):
    listings, indices, scores = search_lda(query,
                                           ta_vectorizer,
                                           ta_lda_ht,
                                           ta_lda_tt,
                                           ta_mat_index_to_listing)
    ordered_listings = []

    for (l, ind, score) in zip(listings, indices, scores):
        ta_listing_info = ta_listings[ta_index_to_listing[int(l)]]
        # print("Listing Name: " + ta_index_to_listing[int(l)])
        # print("Listing URL: " + ta_listing_info[0])
        # print("Score (Similarity): " + str(score))
        # print("**************")
        ordered_listings.append({
            'name': ta_index_to_listing[int(l)],
            'listing_url': ta_listing_info[0],
            'image_url': '/static/img/tripadvisor1600.png',
            'score': str(score)
        })

    return ordered_listings