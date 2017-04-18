from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from .models import Docs
from django.template import loader
from .form import QueryForm
from .test import get_hotel_results, get_hotel_tuples, get_airbnb_tuples, get_airbnb_results
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
import cPickle as pickle
from scipy.sparse.linalg import svds
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

with open('data/tripadvisor_reviews.pickle','rb') as f:
  ta_reviews_data = pickle.load(f)

with open('data/tripadvisor_hotel_info.pickle','rb') as f:
  hotel_information = pickle.load(f)

(hotel_to_key_index, index_to_hotel, ta_reviews) = get_hotel_tuples(hotel_information, ta_reviews_data)

ta_vectorizer = TfidfVectorizer(stop_words='english', max_df = 0.7)
ta_tfidf = ta_vectorizer.fit_transform(ta_reviews)

#words_compressed_ta, _, docs_compressed_ta = svds(ta_tfidf, k=10)
docs_compressed_ta, _, words_compressed_ta = svds(ta_tfidf, k=10)
docs_compressed_ta = docs_compressed_ta.T
words_compressed_ta = words_compressed_ta.T

#with open('data/10_by_docs_svd_ta.pickle','rb') as f:
#  words_compressed_ta = pickle.load(f) 

#with open('data/words_by_10_svd_ta.pickle','rb') as f:
#  docs_compressed_ta = pickle.load(f) 

with open('data/airbnb_reviews.pickle','rb') as f:
 airbnb_reviews_data = pickle.load(f)

with open('data/airbnb_listings.pickle','rb') as f:
 listings_information = pickle.load(f)

(index_to_listing, airbnb_reviews) = get_airbnb_tuples(airbnb_reviews_data)

airbnb_vectorizer = TfidfVectorizer(stop_words='english', max_df = 0.7)
airbnb_tfidf = airbnb_vectorizer.fit_transform(airbnb_reviews)

docs_compressed_airbnb, _, words_compressed_airbnb = svds(airbnb_tfidf, k=10)
docs_compressed_airbnb = docs_compressed_airbnb.T
words_compressed_airbnb = words_compressed_airbnb.T

# Create your views here.
def index(request):
    words=json.load(open("jsons/words.json"))
    airbnb_output = []
    hotel_output = []
    query = ''
    if request.GET.get('search'):
      query = request.GET.get('search')

      hotel_output = get_hotel_results(query, ta_reviews_data, hotel_information, index_to_hotel, ta_vectorizer, words_compressed_ta, docs_compressed_ta)
      airbnb_output = get_airbnb_results(query, airbnb_reviews, listings_information, index_to_listing, airbnb_vectorizer, words_compressed_airbnb, docs_compressed_airbnb)

      print hotel_output[0]
      print airbnb_output[0]
        #hotel_output = hotel_list
        #airbnb_output = airbnb_list
        # search = request.GET.get('search')
        # output_list = find_similar(search)
        # paginator = Paginator(output_list, 10)
        # page = request.GET.get('page')
        #
        # try:
        #     output = paginator.page(page)
        # except PageNotAnInteger:
        #     output = paginator.page(1)
        # except EmptyPage:
        #     output = paginator.page(paginator.num_pages)
    return render_to_response('project_template/index.html',
                          {'airbnb_output': airbnb_output,
                           'search': query,
                           'hotel_output': hotel_output,
                           'magic_url': request.get_full_path(),
                           'words': words,
                           })