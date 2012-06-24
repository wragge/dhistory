# Create your views here.
import json
from django.shortcuts import render_to_response
from django.template import RequestContext
from dhistory.frontpages.models import *
from django.views.decorators.cache import cache_page
from django.db.models import Q

CATEGORIES = {'article': 'Article', 'advertising': 'Advertising', 'lists': 'Detailed lists, results, guides', 'family': 'Family Notices', 'literature': 'Literature'}
CATEGORIES_REV = {'Article':'article', 'Advertising': 'advertising', 'Detailed lists, results, guides': 'lists', 'Family Notices': 'family', 'Literature': 'literature'}
COLOURS = {'article': 'Article', 'advertising': 'Advertising', 'lists': 'Detailed lists, results, guides', 'family': 'Family Notices', 'literature': 'Literature'}
MONTHS = ['Year', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
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
    
def show_newspaper(request, newspaper_id):
    newspaper = Newspaper.objects.get(newspaper_id=newspaper_id)
    newspapers = Newspaper.objects.values_list('newspaper_id', 'newspaper_title').order_by('newspaper_title')
    totals = Total.objects.filter(newspaper=newspaper).filter(month=0).order_by('year', 'total_type')
    years = {}
    for total in totals:
        if total.total_type == 'issues':
            years[total.year] = {}
            years[total.year]['issues'] = total.value
        else:
            if total.total_type == 'total':
                years[total.year][CATEGORIES_REV[total.category]] = {}
                years[total.year][CATEGORIES_REV[total.category]]['total'] = {}
                years[total.year][CATEGORIES_REV[total.category]]['total']['value'] = total.value
                years[total.year][CATEGORIES_REV[total.category]]['total']['average'] = total.average
            elif total.total_type == 'words':
                years[total.year][CATEGORIES_REV[total.category]]['words'] = {}
                years[total.year][CATEGORIES_REV[total.category]]['words']['value'] = total.value
                years[total.year][CATEGORIES_REV[total.category]]['words']['average'] = total.average
    return render_to_response('newspaper.html', {'newspaper': newspaper, 'newspapers': newspapers, 'years': years, 'totals': totals}, context_instance=RequestContext(request))
        
def show_newspaper_line(request, newspaper_id, total_type='words'):
    series = []
    if total_type == 'number': total_type = 'total'
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
    if total_type == 'total': total_type = 'number'
    return render_to_response('newspaper_line.html', {'series': json.dumps(series), 'newspaper': newspaper, 'newspapers': newspapers, 'total_type': total_type}, context_instance=RequestContext(request))
        
def show_newspaper_year(request, newspaper_id, year):
    newspaper = Newspaper.objects.get(newspaper_id=newspaper_id)
    newspapers = Newspaper.objects.values_list('newspaper_id', 'newspaper_title').order_by('newspaper_title')
    totals = Total.objects.filter(newspaper=newspaper).filter(year=year).order_by('month', 'total_type')
    months = {}
    for total in totals:
        if total.total_type == 'issues':
            months[total.month] = {}
            months[total.month]['issues'] = total.value
            months[total.month]['label'] = MONTHS[total.month]
        else:
            if total.total_type == 'total':
                months[total.month][CATEGORIES_REV[total.category]] = {}
                months[total.month][CATEGORIES_REV[total.category]]['total'] = {}
                months[total.month][CATEGORIES_REV[total.category]]['total']['value'] = total.value
                months[total.month][CATEGORIES_REV[total.category]]['total']['average'] = total.average
            elif total.total_type == 'words':
                months[total.month][CATEGORIES_REV[total.category]]['words'] = {}
                months[total.month][CATEGORIES_REV[total.category]]['words']['value'] = total.value
                months[total.month][CATEGORIES_REV[total.category]]['words']['average'] = total.average
    return render_to_response('newspaper_year.html', {'newspaper': newspaper, 'newspapers': newspapers, 'months': months, 'year': year}, context_instance=RequestContext(request))

def show_newspaper_year_line(request, newspaper_id, year, total_type='words'):
    series = []
    if total_type == 'number': total_type = 'total'
    newspaper = Newspaper.objects.get(newspaper_id=newspaper_id)
    newspapers = Newspaper.objects.values_list('newspaper_id', 'newspaper_title').order_by('newspaper_title')
    totals = Total.objects.filter(newspaper=newspaper).filter(year=year).exclude(month=0).filter(total_type=total_type)
    categories = request.GET.getlist('category')
    #q_objects = [Q(category=CATEGORIES[category]) for category in categories]
    #totals = totals.filter(reduce(operator.or_, q_objects))
    if not categories: categories = CATEGORIES.keys()
    for category in categories:
        data = totals.filter(category=CATEGORIES[category]).values_list('month', 'average').order_by('year')
        data = [average for month, average in data]
        series.append({'name': CATEGORIES[category], 'data': data})
    if total_type == 'total': total_type = 'number'
    return render_to_response('newspaper_year_line.html', {'series': json.dumps(series), 'newspaper': newspaper, 'newspapers': newspapers, 'total_type': total_type, 'year': year}, context_instance=RequestContext(request))

def show_newspaper_month(request, newspaper_id, year, month):
    newspaper = Newspaper.objects.get(newspaper_id=newspaper_id)
    newspapers = Newspaper.objects.values_list('newspaper_id', 'newspaper_title').order_by('newspaper_title')
    totals = Total.objects.filter(newspaper=newspaper).filter(year=year).filter(month=month).order_by('month', 'total_type')
    articles = Article.objects.filter(article_date__year=year, article_date__month=month, newspaper_id=newspaper_id).order_by('article_date', 'category', 'title')
    issues = {}
    for article in articles:
        try:
            issues[article.article_date][article.category]['total'] += 1
            issues[article.article_date][article.category]['words'] += word_count
        except KeyError:
            try:
                issues[article.article_date][CATEGORIES_REV[article.category]] = {}
                issues[article.article_date][CATEGORIES_REV[article.category]]['total'] = 1
                issues[article.article_date][CATEGORIES_REV[article.category]]['words'] = article.word_count
            except KeyError:
                issues[article.article_date] = {}
                issues[article.article_date][CATEGORIES_REV[article.category]] = {}
                issues[article.article_date][CATEGORIES_REV[article.category]]['total'] = 1
                issues[article.article_date][CATEGORIES_REV[article.category]]['words'] = article.word_count
    issues = [ [date, issues[date]] for date in sorted(issues.keys()) ]
    return render_to_response('newspaper_month.html', {'newspaper': newspaper, 'newspapers': newspapers, 'issues': issues, 'year': year, 'month': month, 'month_label': MONTHS[int(month)]}, context_instance=RequestContext(request))

def show_newspaper_month_line(request, newspaper_id, year, month, total_type='words'):
    series = []
    if total_type == 'number': total_type = 'total'
    newspaper = Newspaper.objects.get(newspaper_id=newspaper_id)
    newspapers = Newspaper.objects.values_list('newspaper_id', 'newspaper_title').order_by('newspaper_title')
    totals = Total.objects.filter(newspaper=newspaper).filter(year=year).filter(month=month).order_by('month', 'total_type')
    articles = Article.objects.filter(article_date__year=year, article_date__month=month, newspaper_id=newspaper_id).order_by('article_date', 'category', 'title')
    categories = request.GET.getlist('category')
    issues = {}
    for article in articles:
        try:
            issues[article.article_date.day][article.category]['total'] += 1
            issues[article.article_date.day][article.category]['words'] += word_count
        except KeyError:
            try:
                issues[article.article_date.day][CATEGORIES_REV[article.category]] = {}
                issues[article.article_date.day][CATEGORIES_REV[article.category]]['total'] = 1
                issues[article.article_date.day][CATEGORIES_REV[article.category]]['words'] = article.word_count
            except KeyError:
                issues[article.article_date.day] = {}
                issues[article.article_date.day][CATEGORIES_REV[article.category]] = {}
                issues[article.article_date.day][CATEGORIES_REV[article.category]]['total'] = 1
                issues[article.article_date.day][CATEGORIES_REV[article.category]]['words'] = article.word_count
    if not categories: categories = CATEGORIES.keys()
    for category in categories:
        data = []
        for issue, values in issues.items():
            try:
                data.append([issue, values[category][total_type]])
            except KeyError:
                pass
        if data:
            series.append({'name': CATEGORIES[category], 'data': data})
    if total_type == 'total': total_type = 'number'
    return render_to_response('newspaper_month_line.html', {'newspaper': newspaper, 'newspapers': newspapers, 'series': json.dumps(series), 'year': year, 'month': month, 'month_label': MONTHS[int(month)], 'total_type': total_type}, context_instance=RequestContext(request))
      
        
            