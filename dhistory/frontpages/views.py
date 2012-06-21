# Create your views here.
import json
from django.shortcuts import render_to_response
from django.template import RequestContext
from dhistory.frontpages.models import *
from django.views.decorators.cache import cache_page
from django.db.models import Q

CATEGORIES = {'article': 'Article', 'advertising': 'Advertising', 'lists': 'Detailed lists, results, guides', 'family': 'Family Notices', 'literature': 'Literature'}
COLOURS = {'article': 'Article', 'advertising': 'Advertising', 'lists': 'Detailed lists, results, guides', 'family': 'Family Notices', 'literature': 'Literature'}

@cache_page(60 * 15)
def show_years_words(request):
    data = []
    newspapers = {}
    totals = Total.objects.filter(category='Article').filter(month=0).filter(total_type='words').exclude(newspaper__newspaper_id=112).order_by('year', 'newspaper')
    for total in totals:
        if total.average < 10000:
            data.append({ 'n': total.newspaper_id, 'x': total.year, 'y': total.average })
    for newspaper in Newspaper.objects.all():
        newspapers[newspaper.newspaper_id] = newspaper.newspaper_title
    return render_to_response('scatter.html', {'data': json.dumps(data), 'newspapers': json.dumps(newspapers)}, context_instance=RequestContext(request))
    
def show_newspaper(request, newspaper_id, total_type='total'):
    series = []
    newspaper = Newspaper.objects.get(newspaper_id=newspaper_id)
    newspapers = Newspaper.objects.values_list('newspaper_id', 'newspaper_title').order_by('newspaper_title')
    totals = Total.objects.filter(newspaper=newspaper).filter(month=0).filter(total_type=total_type)
    categories = request.GET.getlist('category')
    #q_objects = [Q(category=CATEGORIES[category]) for category in categories]
    #totals = totals.filter(reduce(operator.or_, q_objects))
    if not categories: categories = CATEGORIES.keys()
    for category in categories:
        data = totals.filter(category=CATEGORIES[category]).values_list('year', 'average').order_by('year')
        data = [[year, average] for year, average in data]
        series.append({'name': CATEGORIES[category], 'data': data})
    return render_to_response('newspaper.html', {'series': json.dumps(series), 'newspaper': newspaper, 'newspapers': newspapers, 'total_type': total_type}, context_instance=RequestContext(request))
        
        