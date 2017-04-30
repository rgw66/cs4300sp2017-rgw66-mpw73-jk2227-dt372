from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from .models import Docs
from django.template import loader
from .form import QueryForm
from main import get_airbnb_results, get_hotel_results
from django.http import JsonResponse
import json
# from .test import get_hotel_results, get_hotel_tuples, get_airbnb_tuples, get_airbnb_results
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
def index(request):
    words=json.load(open("jsons/words.json"))
    airbnb_output = []
    hotel_output = []
    best_result = {}
    query = ''
    if request.GET.get('search'):
        query = request.GET.get('search')
        airbnb_output = get_airbnb_results(query)
        hotel_output = get_hotel_results(query)

        if airbnb_output[0]['score'] > hotel_output[0]['score']:
            best_result = airbnb_output[0]
        else:
            best_result = hotel_output[0]

        ## KEEP THIS. This will be helpful if we want to do pages
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
                           'best_result': best_result,
                           'magic_url': request.get_full_path(),
                           'words': words,
                           })

def refine(request):
    hotel_words = ['clean', 'clean', 'clean']
    airbnb_words= ['nice', 'nice', 'nice']
    return JsonResponse({"hotel_words":hotel_words,
                         "airbnb_words":airbnb_words})