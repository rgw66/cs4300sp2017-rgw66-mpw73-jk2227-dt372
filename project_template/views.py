from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from .models import Docs
from django.template import loader
from .form import QueryForm
from .test import get_hotel_results, get_hotel_tuples
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
import cPickle as pickle
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer


with open('data/tripadvisor_reviews.pickle','rb') as f:
  ta_reviews_data = pickle.load(f)

with open('data/tripadvisor_hotel_info.pickle','rb') as f:
  hotel_information = pickle.load(f)

(hotel_to_key_index, index_to_hotel, ta_reviews) = get_hotel_tuples(hotel_information, ta_reviews_data)

ta_vectorizer = TfidfVectorizer(stop_words='english', max_df = 0.7)
ta_vectorizer.fit_transform(ta_reviews)

with open('data/10_by_docs_svd_ta.pickle','rb') as f:
  docs_compressed_ta = pickle.load(f) 

with open('data/words_by_10_svd_ta.pickle','rb') as f:
  words_compressed_ta = pickle.load(f) 

with open('data/airbnb_reviews.pickle','rb') as f:
  airbnb_reviews = pickle.load(f)

with open('data/airbnb_listings.pickle','rb') as f:
  listings_information = pickle.load(f)



hotel_review = {'review': 'This is a wonderful hotel. Well proportioned room. I loved the decor. The restaurant and staff were great. Extra big shower caps was only the tell tale sign that they take care of all the details. Really friendly and helpful staff.', 'review_stars': '5 of 5 bubbles', 'hotel_name':  'Gramercy Park Hotel' , 'title': 'Beautiful decor'}

airbnb_review = {'review': 'I only saw Bobby for one brief minute in passing but our conversation seem like i knew him forever He has very good communication on checking in and telling you about his place The location is to die for You are actually only minutes away to the heart of Time Square Checking in the Lovely High Rise building was a snap having a 24 hr doorman Very safe to walk to at any time at nite male or female And the view from his place is a very nice scene of New York City I will truly come back and he was a great host'}

hotel_list = [hotel_review for _ in range(10)]

airbnb_list = [airbnb_review for _ in range(10)]

# Create your views here.
def index(request):
    print len(ta_reviews)
    print docs_compressed_ta.shape
    print words_compressed_ta.shape
    hotel_output = []
    airbnb_output = []
    words=json.load(open("jsons/words.json"))
    if request.GET.get('search'):
      query = request.GET.get('search')
      get_hotel_results(query, ta_reviews, hotel_information, ta_vectorizer, words_compressed_ta, docs_compressed_ta)
      
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
                           'hotel_output': hotel_output,
                           'magic_url': request.get_full_path(),
                           'words': words,
                           })