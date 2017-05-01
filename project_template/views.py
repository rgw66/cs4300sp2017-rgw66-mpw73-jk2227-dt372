from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from .models import Docs
from django.template import loader
from .form import QueryForm
from main import get_airbnb_results, get_hotel_results, get_closest_words, get_overall_results
from django.http import JsonResponse
import json
# from .test import get_hotel_results, get_hotel_tuples, get_airbnb_tuples, get_airbnb_results
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
def index(request):
    words=json.load(open("jsons/words.json"))
    airbnb_output = []
    hotel_output = []
    airbnb_sentscores = [] 
    hotel_sentscores = [] 
    overall_output = []
    query = ''
    if request.GET.get('search'):
        query = request.GET.get('search')
        airbnb_output = get_airbnb_results(query)
        hotel_output = get_hotel_results(query)
        #for airbnb_info in airbnb_output:
        #  airbnb_sentscores.extend(airbnb_info['sent_scores'])
        #for hotel_info in hotel_output:
        #  hotel_sentscores.extend(hotel_info['sent_scores'])
        overall_output = get_overall_results(query)
        for info in overall_output:
          if info['is_airbnb']:
            airbnb_sentscores.extend(info['sent_scores'])
          else:
            hotel_sentscores.extend(info['sent_scores'])

    return render_to_response('project_template/index.html',
                          {'airbnb_output': airbnb_output,
                           'search': query,
                           'hotel_output': hotel_output,
                           'overall_output': overall_output,
                           'magic_url': request.get_full_path(),
                           'words': words,
                           'hotel_sentscores': hotel_sentscores,
                           'airbnb_sentscores': airbnb_sentscores
                           })

def refine(request):
    hotel_words = get_closest_words("hotel", request.GET.get('words'))
    airbnb_words = get_closest_words("airbnb", request.GET.get('words'))
    return JsonResponse({"hotel_words":hotel_words,
                         "airbnb_words":airbnb_words})