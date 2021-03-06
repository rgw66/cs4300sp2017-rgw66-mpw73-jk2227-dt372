from __future__ import print_function
from scipy import sparse
from sklearn.preprocessing import normalize
import numpy as np
import pickle
import boto3

ta_listings = pickle.load(open("data/tripadvisor_hotel_info.pickle", 'rb'))
airbnb_listings = pickle.load(open("data/airbnb_listings.pickle", 'rb'))

ta_index_to_listing = pickle.load(open("data/ta_index_to_listing.pickle"))
airbnb_mat_index_to_listing = pickle.load(open("data/airbnb_mat_index_to_listing.pickle"))
ta_mat_index_to_listing = pickle.load(open("data/ta_mat_index_to_listing.pickle"))
total_mat_index_to_listing = pickle.load(open("data/total_mat_index_to_listing.pickle"))
ta_lda_ht = pickle.load(open("data/ta_lda_ht.mat"))
ta_lda_tt = pickle.load(open("data/ta_lda_tt.mat"))
airbnb_lda_ht = pickle.load(open("data/airbnb_lda_ht.mat"))
airbnb_lda_tt = pickle.load(open("data/airbnb_lda_tt.mat"))
total_lda_ht = pickle.load(open("data/total_lda_ht.mat"))
total_lda_tt = pickle.load(open("data/total_lda_tt.mat"))

ta_adj_mat = pickle.load(open("data/ta_adj_mat.pickle"))
airbnb_adj_mat = pickle.load(open("data/airbnb_adj_mat.pickle"))

airbnb_sentscores = pickle.load(open("airbnb_sentscores.pickle"))    
ta_sentscores = pickle.load(open("tripadvisor_sentscores.pickle")) 
airbnb_name_to_sent_avg = pickle.load(open("airbnb_name_to_sent_avg.pickle"))    
tripadvisor_name_to_sent_avg = pickle.load(open("tripadvisor_name_to_sent_avg.pickle")) 


airbnb_svd_s = pickle.load(open("data/airbnb_svd_s.pickle"))
airbnb_svd_tt = pickle.load(open("data/airbnb_svd_tt.pickle")) 
ta_svd_s = pickle.load(open("data/ta_svd_s.pickle"))
ta_svd_tt = pickle.load(open("data/ta_svd_tt.pickle"))
total_svd_s = pickle.load(open("data/total_svd_s.pickle"))
total_svd_tt = pickle.load(open("data/total_svd_tt.pickle"))

airbnb_vectorizer = pickle.load(open("data/airbnb_vectorizer.pickle", "rb"))
ta_vectorizer = pickle.load(open("data/ta_vectorizer.pickle", "rb"))
total_vectorizer = pickle.load(open("data/total_vectorizer.pickle", "rb"))
ta_word_to_index = ta_vectorizer.vocabulary_
ta_index_to_word = {i:t for t,i in ta_word_to_index.iteritems()}
airbnb_word_to_index = airbnb_vectorizer.vocabulary_
airbnb_index_to_word = {i:t for t,i in airbnb_word_to_index.iteritems()}
total_word_to_index = total_vectorizer.vocabulary_
total_index_to_word = {i:t for t,i in total_word_to_index.iteritems()}

ta_hs = pickle.load(open("data/ta_hs.pickle", "rb"))
airbnb_hs = pickle.load(open("data/airbnb_hs.pickle", "rb"))
total_hs = pickle.load(open("data/total_hs.pickle", "rb"))

BUCKET_NAME = 'cs4300-dream-team'
S3 = boto3.resource('s3')
CLIENT = boto3.client('s3')

tripadvisor_name_to_review_index = pickle.load(open("tripadvisor_name_to_review_index.pickle"))
airbnb_name_to_review_index = pickle.load(open("airbnb_name_to_review_index.pickle"))

def closest_words(word_in, total_svd_s, total_svd_tt, word_to_index, index_to_word, k = 5):
    if word_in not in word_to_index: return []
    sims = np.matmul(total_svd_tt.T, np.multiply(total_svd_s, total_svd_tt[:, word_to_index[word_in]]))
    asort = np.argsort(-sims)[:k+1]
    return [(index_to_word[i],sims[i]/sims[asort[0]]) for i in asort[1:]]

def get_hotel_reviews(site, hotel_ind):
    indices = None
    if (site == 'airbnb'):
        indices = sparse.find(airbnb_adj_mat[hotel_ind, :])[1]
    else:
        indices = sparse.find(ta_adj_mat[hotel_ind, :])[1]
    return get_reviews(site, indices)
        
    
def get_reviews(site,ind_lst):
    # site = "airbnb" or "ta" 
    sorted_lst = sorted(ind_lst)
    f = [] 
    low = (sorted_lst[0]/500) + 1
    tempBucket = []
    for elem in sorted_lst: 
        if elem < low * 500:
            tempBucket.append(elem)
        else: 
            low = (elem/500) + 1
            f.append(tempBucket)
            tempBucket = [elem]
    f.append(tempBucket)

    reviews = []

    for cluster in f:
        ind = cluster[0]
        page_lower = ind/500 * 500 
        page_upper = page_lower + 499
        page_key = "/{}_reviews/{}_review_{}-{}.txt".format(site,site,page_lower,page_upper)
        with open('tmp.p', 'wb') as data:
                CLIENT.download_fileobj(BUCKET_NAME,page_key,data)
        with open('tmp.p', 'rb') as data: 
            lst = pickle.load(data)
        for ind in cluster:
            ind_in_page = ind % 500
            reviews.append(lst[ind_in_page])

    unscramble = {} 
    for (idx, review) in zip(sorted_lst, reviews):
        unscramble[idx] = review 

    unscrambled_reviews = [unscramble[i] for i in ind_lst]
    return unscrambled_reviews #reviews


def search_lda(query, vectorizer, ht_mat, tt_mat, mat_to_listing_dict, 
               svd_weights, svd_topics, word_to_index, index_to_word, 
               hs, top_k = 12, bottom = False):
    related_words = []
    for q in query.split():
        related_words += closest_words(q, svd_weights, svd_topics, word_to_index, index_to_word)
    related_words = list(set(related_words))
    related_words = [w[0] for w in sorted(related_words, key = lambda item: item[1], reverse = True)[:5]]
    vec = vectorizer.transform([query]).todense().T
    results = np.multiply(np.dot(ht_mat, normalize(np.dot(tt_mat, vec), axis = 0)).T, hs)
    if (bottom):
        indices = np.squeeze(np.asarray(np.argsort(results)))[::-1].T[-top_k:]
        scores = np.squeeze(np.asarray(np.sort(results)))[::-1].T[-top_k:]    
        listings = np.zeros(indices.shape)
        for i in range(indices.shape[0]):
            listings[i] = mat_to_listing_dict[indices[i]]
        return (listings.tolist(), indices.tolist(), scores.tolist(), related_words)
    else:
        indices = np.squeeze(np.asarray(np.argsort(results)))[::-1].T[:top_k]
        scores = np.squeeze(np.asarray(np.sort(results)))[::-1].T[:top_k]    
        listings = np.zeros(indices.shape)
        for i in range(indices.shape[0]):
            listings[i] = mat_to_listing_dict[indices[i]]
        return (listings.tolist(), indices.tolist(), scores.tolist(), related_words)


def get_airbnb_results(query, bottom=False):
    airbnb_vectorizer = pickle.load(open("data/airbnb_vectorizer.pickle", "rb"))
    listings, indices, scores, related_words = search_lda(query,
                                           airbnb_vectorizer,
                                           airbnb_lda_ht,
                                           airbnb_lda_tt,
                                           airbnb_mat_index_to_listing,
                                           airbnb_svd_s,
                                           airbnb_svd_tt,
                                           airbnb_word_to_index,
                                           airbnb_index_to_word,
                                           airbnb_hs,
                                            bottom = bottom)
    ordered_listings = []
    min_max_indices = [] 
    for (l, ind, score) in zip(listings, indices, scores):
        listing_id = str(int(l))
        airbnb_listing_info = airbnb_listings[listing_id]
        name = airbnb_listing_info['name']
        indices_per_listing = airbnb_name_to_review_index[name]
        sent_scores_index_pairs = [(airbnb_sentscores[i], i) for i in indices_per_listing]
        sorted_sent_scores_index_pairs = sorted(sent_scores_index_pairs, key=lambda x : x[0])
        min_sent, min_review_index = sorted_sent_scores_index_pairs[0]
        max_sent, max_review_index = sorted_sent_scores_index_pairs[-1]
        
        min_max_indices.append(min_review_index) 
        min_max_indices.append(max_review_index)
        sent_scores = [sent_scores_index_pair[0] for sent_scores_index_pair in sent_scores_index_pairs]
        avg_sent = np.average(sent_scores)

        ordered_listings.append({
            'name': name,
            'listing_url': airbnb_listing_info['listing_url'],
            'image_url': airbnb_listing_info['picture_url'],
            'score': "{0:.3f}".format(round(score,4)), 
            'min_sent_score': min_sent,
            'min_sent_review': "", 
            'max_sent_score': max_sent,
            'max_sent_review': "", 
            'avg_sent_score': "{0:.3f}".format(round(airbnb_name_to_sent_avg[name],4)),
            'sent_scores': sent_scores,
            'rating': airbnb_listing_info['rating']
        })

    reviews = get_reviews('airbnb', min_max_indices)
    for i, review in enumerate(reviews):
        if i % 2 == 0: 
            ordered_listings[i/2]['min_sent_review'] = review 
        else:
            ordered_listings[i/2]['max_sent_review'] = review 

    del airbnb_vectorizer
    
    return ordered_listings

def get_hotel_results(query, bottom=False):
    ta_vectorizer = pickle.load(open("data/ta_vectorizer.pickle", "rb"))
    hotel_images = pickle.load(open("data/hotel_images.pickle", "rb"))
    listings, indices, scores, related_words = search_lda(query,
                                           ta_vectorizer,
                                           ta_lda_ht,
                                           ta_lda_tt,
                                           ta_mat_index_to_listing,
                                           ta_svd_s,
                                           ta_svd_tt,
                                           ta_word_to_index,
                                           ta_index_to_word,
                                           ta_hs,
                                            bottom=bottom)
    ordered_listings = []
    min_max_indices = [] 

    total_listings = 0
    for (l, ind, score) in zip(listings, indices, scores):
        name = ta_index_to_listing[int(l)]
        #We updated one of our pickle files but didn't want to update the others as a consequence...
        if name == "Loews Regency New York Hotel " or name == "Royal Park Hotel ":
            continue
        if total_listings == 10:
            continue
        indices_per_listing = tripadvisor_name_to_review_index[name]
        sent_scores_index_pairs = [(ta_sentscores[i], i) for i in indices_per_listing]
        sorted_sent_scores_index_pairs = sorted(sent_scores_index_pairs, key=lambda x : x[0])
        min_sent, min_review_index = sorted_sent_scores_index_pairs[0]
        max_sent, max_review_index = sorted_sent_scores_index_pairs[-1]
        
        min_max_indices.append(min_review_index) 
        min_max_indices.append(max_review_index)

        sent_scores = [sent_scores_index_pair[0] for sent_scores_index_pair in sent_scores_index_pairs]

        ordered_listings.append({
            'name': name,
            'listing_url': ta_listings[name][0],
            'image_url': hotel_images[name],
            'score': "{0:.3f}".format(round(score,4)),
            'min_sent_score': min_sent,
            'min_sent_review': "", # min_review,
            'max_sent_score': max_sent,
            'max_sent_review': "", # max_review,
            'avg_sent_score': "{0:.3f}".format(round(tripadvisor_name_to_sent_avg[name],4)),
            'sent_scores': sent_scores,
            'rating': ta_listings[name][1]*20
        })
        total_listings+=1

    del ta_vectorizer
    del hotel_images
    reviews = get_reviews('ta', min_max_indices)
    for i, review in enumerate(reviews):
        if i % 2 == 0: 
            ordered_listings[i/2]['min_sent_review'] = review 
        else:
            ordered_listings[i/2]['max_sent_review'] = review 

    return ordered_listings

def get_overall_results(query, bottom=False):
    total_vectorizer = pickle.load(open("data/total_vectorizer.pickle", "rb"))
    hotel_images = pickle.load(open("data/hotel_images.pickle", "rb"))
    listings, indices, scores, related_words = search_lda(query,
                                           total_vectorizer,
                                           total_lda_ht,
                                           total_lda_tt,
                                           total_mat_index_to_listing,
                                           total_svd_s,
                                           total_svd_tt,
                                           total_word_to_index,
                                           total_index_to_word,
                                           total_hs,
                                            bottom=bottom)
    ordered_listings = []
    min_max_indices = [] 

    threshold = (ta_lda_ht.shape)[0]
    for (l, ind, score) in zip(listings, indices, scores):
        if (ind > threshold):
            listing_id = str(int(l))
            airbnb_listing_info = airbnb_listings[listing_id]
            name = airbnb_listing_info['name']
            indices_per_listing = airbnb_name_to_review_index[name]
            sent_scores_index_pairs = [(airbnb_sentscores[i], i) for i in indices_per_listing]
            sorted_sent_scores_index_pairs = sorted(sent_scores_index_pairs, key=lambda x : x[0])
            min_sent, min_review_index = sorted_sent_scores_index_pairs[0]
            max_sent, max_review_index = sorted_sent_scores_index_pairs[-1]
            
            min_max_indices.append((1, min_review_index))
            min_max_indices.append((1, max_review_index))
            sent_scores = [sent_scores_index_pair[0] for sent_scores_index_pair in sent_scores_index_pairs]

            ordered_listings.append({
                'name': name,
                'listing_url': airbnb_listing_info['listing_url'],
                'image_url': airbnb_listing_info['picture_url'],
                'score': "{0:.3f}".format(round(score,4)), 
                'min_sent_score': min_sent,
                'min_sent_review': "", 
                'max_sent_score': max_sent,
                'max_sent_review': "", 
                'avg_sent_score': "{0:.3f}".format(round(airbnb_name_to_sent_avg[name],4)),
                'sent_scores': sent_scores,
                'rating': airbnb_listing_info['rating'],
                'is_airbnb': True
            })
        else:
            name = ta_index_to_listing[int(l)]
            indices_per_listing = tripadvisor_name_to_review_index[name]
            sent_scores_index_pairs = [(ta_sentscores[i], i) for i in indices_per_listing]
            sorted_sent_scores_index_pairs = sorted(sent_scores_index_pairs, key=lambda x : x[0])
            min_sent, min_review_index = sorted_sent_scores_index_pairs[0]
            max_sent, max_review_index = sorted_sent_scores_index_pairs[-1]
            
            min_max_indices.append((0, min_review_index))
            min_max_indices.append((0, max_review_index))

            sent_scores = [sent_scores_index_pair[0] for sent_scores_index_pair in sent_scores_index_pairs]

            ordered_listings.append({
                'name': name,
                'listing_url': ta_listings[name][0],
                'image_url': hotel_images[name],
                'score': "{0:.3f}".format(round(score,4)),
                'min_sent_score': min_sent,
                'min_sent_review': "", # min_review,
                'max_sent_score': max_sent,
                'max_sent_review': "", # max_review,
                'avg_sent_score': "{0:.3f}".format(round(tripadvisor_name_to_sent_avg[name],4)),
                'sent_scores': sent_scores,
                'rating': ta_listings[name][1],
                'is_airbnb': False
            })
    del total_vectorizer
    del hotel_images
    reviews = []
    for i, min_max_ind in min_max_indices:
        if (i == 0): reviews += get_reviews('ta', [min_max_ind])
        else: reviews += get_reviews('airbnb', [min_max_ind])
    for i, review in enumerate(reviews):
        if i % 2 == 0: 
            ordered_listings[i/2]['min_sent_review'] = review 
        else:
            ordered_listings[i/2]['max_sent_review'] = review 

    return ordered_listings

def get_closest_words(listing_type, query):
    if listing_type == "airbnb":
        airbnb_vectorizer = pickle.load(open("data/airbnb_vectorizer.pickle", "rb"))
        listings, indices, scores, related_words = search_lda(query,
                                                              airbnb_vectorizer,
                                                              airbnb_lda_ht,
                                                              airbnb_lda_tt,
                                                              airbnb_mat_index_to_listing,
                                                              airbnb_svd_s,
                                                              airbnb_svd_tt,
                                                              airbnb_word_to_index,
                                                              airbnb_index_to_word,
                                                              airbnb_hs)
    elif listing_type == "hotel":
        ta_vectorizer = pickle.load(open("data/ta_vectorizer.pickle", "rb"))
        listings, indices, scores, related_words = search_lda(query,
                                                          ta_vectorizer,
                                                          ta_lda_ht,
                                                          ta_lda_tt,
                                                          ta_mat_index_to_listing,
                                                          ta_svd_s,
                                                          ta_svd_tt,
                                                          ta_word_to_index,
                                                          ta_index_to_word,
                                                          ta_hs)
    else:
        ta_vectorizer = pickle.load(open("data/ta_vectorizer.pickle", "rb"))
        listings, indices, scores, related_words = search_lda(query,
                                                          ta_vectorizer,
                                                          ta_lda_ht,
                                                          ta_lda_tt,
                                                          ta_mat_index_to_listing,
                                                          ta_svd_s,
                                                          ta_svd_tt,
                                                          ta_word_to_index,
                                                          ta_index_to_word,
                                                          ta_hs)
    return related_words

