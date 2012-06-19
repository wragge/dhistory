# Create your views here.
import json
from django.shortcuts import render_to_response
from dhistory.frontpages.models import *

def show_years_words(request):
    data = []
    newspapers = {}
    totals = Total.objects.filter(category='Article').filter(month=0).filter(total_type='words').exclude(newspaper__newspaper_id=112).order_by('year', 'newspaper')
    for total in totals:
        if total.average < 10000:
            data.append({ 'n': total.newspaper_id, 'x': total.year, 'y': total.average })
    for newspaper in Newspaper.objects.all():
        newspapers[newspaper.newspaper_id] = newspaper.newspaper_title
    return render_to_response('scatter.html', {'data': json.dumps(data), 'newspapers': json.dumps(newspapers)})
    