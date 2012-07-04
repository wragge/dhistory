# Create your views here.
import json
import datetime
import re
from operator import itemgetter
from django.shortcuts import render_to_response
from django.template import RequestContext
from dhistory.frontpages.models import *
from django.views.decorators.cache import cache_page
from django.db.models import Q

CATEGORIES = {'article': 'Article', 'advertising': 'Advertising', 'lists': 'Detailed lists, results, guides', 'family': 'Family Notices', 'literature': 'Literature'}
CATEGORIES_REV = {'Article':'article', 'Advertising': 'advertising', 'Detailed lists, results, guides': 'lists', 'Family Notices': 'family', 'Literature': 'literature'}
COLOURS = {'article': 'Article', 'advertising': 'Advertising', 'lists': 'Detailed lists, results, guides', 'family': 'Family Notices', 'literature': 'Literature'}
MONTHS = ['Year', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

@cache_page(60 * 60)
def show_home(request):
    return render_to_response('frontpages.html', {}, context_instance=RequestContext(request))

@cache_page(60 * 60)
def show_years_words(request, category='article', total_type='words'):
    if total_type == 'number': total_type = 'total'
    data = []
    newspapers = {}
    if category == 'illustrated':
        total_type = 'illustrated'
        category_long = 'Illustrated article'
        totals = Total.objects.filter(month=0).filter(total_type='illustrated').exclude(newspaper__newspaper_id=112).order_by('year', 'newspaper') 
    else:
        category_long = CATEGORIES[category]
        totals = Total.objects.filter(category=category_long).filter(month=0).filter(total_type=total_type).exclude(newspaper__newspaper_id=112).order_by('year', 'newspaper')   
    for total in totals:
        if total.average < 10000:
            data.append({ 'n': total.newspaper.newspaper_id, 'x': total.year, 'y': total.average })
    for newspaper in Newspaper.objects.all():
        newspapers[newspaper.newspaper_id] = newspaper.newspaper_title
    if total_type == 'total': total_type = 'number'
    return render_to_response('scatter.html', {'data': json.dumps(data),
                                               'newspapers': json.dumps(newspapers),
                                               'category': category,
                                               'category_long': category_long,
                                               'total_type': total_type},context_instance=RequestContext(request))

@cache_page(60 * 60)  
def show_newspaper(request, newspaper_id):
    newspaper = Newspaper.objects.get(newspaper_id=newspaper_id)
    totals = Total.objects.filter(newspaper=newspaper).filter(month=0).order_by('year', 'total_type')
    years = {}
    for total in totals:
        if total.total_type == 'issues':
            try:
                years[total.year]['issues'] = total.value
            except KeyError:
                years[total.year] = {}
                years[total.year]['issues'] = total.value
        elif total.total_type == 'illustrated':
            try:
                years[total.year]['illustrated'] = {}
            except KeyError:
                years[total.year] = {}
                years[total.year]['illustrated'] = {}
            years[total.year]['illustrated']['value'] = total.value
            years[total.year]['illustrated']['average'] = total.average
        elif total.total_type == 'total' or total.total_type == 'words':
            try:
                years[total.year][CATEGORIES_REV[total.category]]
            except KeyError:
                try:
                    years[total.year][CATEGORIES_REV[total.category]] = {}
                except KeyError:
                    years[total.year] = {}
                    years[total.year][CATEGORIES_REV[total.category]] = {}
            if total.total_type == 'total':
                years[total.year][CATEGORIES_REV[total.category]]['total'] = {}
                years[total.year][CATEGORIES_REV[total.category]]['total']['value'] = total.value
                years[total.year][CATEGORIES_REV[total.category]]['total']['average'] = total.average
            elif total.total_type == 'words':
                years[total.year][CATEGORIES_REV[total.category]]['words'] = {}
                years[total.year][CATEGORIES_REV[total.category]]['words']['value'] = total.value
                years[total.year][CATEGORIES_REV[total.category]]['words']['average'] = total.average
    return render_to_response('newspaper.html', {'newspaper': newspaper,
                                                 'years': years,
                                                 'totals': totals}, context_instance=RequestContext(request))
@cache_page(60 * 60)       
def show_newspaper_line(request, newspaper_id, total_type='words'):
    series = []
    if total_type == 'number': total_type = 'total'
    newspaper = Newspaper.objects.get(newspaper_id=newspaper_id)
    newspapers = Newspaper.objects.values_list('newspaper_id', 'newspaper_title').order_by('newspaper_title')
    totals = Total.objects.filter(newspaper=newspaper).filter(month=0).filter(total_type=total_type)
    if total_type == 'illustrated':
        data = totals.values_list('year', 'average').order_by('year')
        data = [[year, average] for year, average in data]
        series.append({'name': 'Illustrated article', 'data': data})
    else:
        categories = request.GET.getlist('category')
        #q_objects = [Q(category=CATEGORIES[category]) for category in categories]
        #totals = totals.filter(reduce(operator.or_, q_objects))
        if not categories: categories = CATEGORIES.keys()
        for category in categories:
            data = totals.filter(category=CATEGORIES[category]).values_list('year', 'average').order_by('year')
            data = [[year, average] for year, average in data]
            series.append({'name': CATEGORIES[category], 'data': data})
        if total_type == 'total': total_type = 'number'
    return render_to_response('newspaper_line.html', {'series': json.dumps(series),
                                                      'newspaper': newspaper,
                                                      'total_type': total_type}, context_instance=RequestContext(request))
@cache_page(60 * 60)       
def show_newspaper_year(request, newspaper_id, year):
    newspaper = Newspaper.objects.get(newspaper_id=newspaper_id)
    newspapers = Newspaper.objects.values_list('newspaper_id', 'newspaper_title').order_by('newspaper_title')
    totals = Total.objects.filter(newspaper=newspaper).filter(year=year).order_by('month', 'total_type')
    months = {}
    for total in totals:
        if total.total_type == 'issues':
            try:
               months[total.month]['issues'] = total.value
            except KeyError:
                months[total.month] = {}
                months[total.month]['issues'] = total.value
            months[total.month]['label'] = MONTHS[total.month]
        elif total.total_type == 'illustrated':
            try:
                months[total.month]['illustrated'] = {}
            except KeyError:
                months[total.month] = {}
                months[total.month]['illustrated'] = {}
            months[total.month]['illustrated']['value'] = total.value
            months[total.month]['illustrated']['average'] = total.average
        elif total.total_type == 'total' or total.total_type == 'words':
            try:
                months[total.month][CATEGORIES_REV[total.category]]
            except KeyError:
                try:
                    months[total.month][CATEGORIES_REV[total.category]] = {}
                except KeyError:
                    months[total.month] = {}
                    months[total.month][CATEGORIES_REV[total.category]] = {}
            if total.total_type == 'total':
                months[total.month][CATEGORIES_REV[total.category]]['total'] = {}
                months[total.month][CATEGORIES_REV[total.category]]['total']['value'] = total.value
                months[total.month][CATEGORIES_REV[total.category]]['total']['average'] = total.average
            elif total.total_type == 'words':
                months[total.month][CATEGORIES_REV[total.category]]['words'] = {}
                months[total.month][CATEGORIES_REV[total.category]]['words']['value'] = total.value
                months[total.month][CATEGORIES_REV[total.category]]['words']['average'] = total.average
    return render_to_response('newspaper_year.html', {'newspaper': newspaper,
                                                      'months': months,
                                                      'year': year}, context_instance=RequestContext(request))
@cache_page(60 * 60)
def show_newspaper_year_line(request, newspaper_id, year, total_type='words'):
    series = []
    if total_type == 'number': total_type = 'total'
    newspaper = Newspaper.objects.get(newspaper_id=newspaper_id)
    newspapers = Newspaper.objects.values_list('newspaper_id', 'newspaper_title').order_by('newspaper_title')
    totals = Total.objects.filter(newspaper=newspaper).filter(year=year).exclude(month=0).filter(total_type=total_type)
    if total_type == 'illustrated':
        data = totals.values_list('month', 'average').order_by('year')
        data = [[month-1, average] for month, average in data]
        series.append({'name': 'Illustrated article', 'data': data})
    else:
        categories = request.GET.getlist('category')
        #q_objects = [Q(category=CATEGORIES[category]) for category in categories]
        #totals = totals.filter(reduce(operator.or_, q_objects))
        if not categories: categories = CATEGORIES.keys()
        for category in categories:
            data = totals.filter(category=CATEGORIES[category]).values_list('month', 'average').order_by('year')
            data = [[month-1, average] for month, average in data]
            series.append({'name': CATEGORIES[category], 'data': data})
    if total_type == 'total': total_type = 'number'
    return render_to_response('newspaper_year_line.html', {'series': json.dumps(series),
                                                           'newspaper': newspaper,
                                                           'total_type': total_type,
                                                           'year': year}, context_instance=RequestContext(request))
@cache_page(60 * 60)
def show_newspaper_month(request, newspaper_id, year, month):
    newspaper = Newspaper.objects.get(newspaper_id=newspaper_id)
    newspapers = Newspaper.objects.values_list('newspaper_id', 'newspaper_title').order_by('newspaper_title')
    totals = Total.objects.filter(newspaper=newspaper).filter(year=year).filter(month=month).order_by('month', 'total_type')
    articles = Article.objects.filter(article_date__year=year, article_date__month=month, newspaper_id=newspaper_id, page_text='1').order_by('article_date', 'category', 'title')
    issues = {}
    for article in articles:
        try:
            if article.illustrated: issues[article.article_date]['illustrated'] += 1
            issues[article.article_date][CATEGORIES_REV[article.category]]['total'] += 1
            issues[article.article_date][CATEGORIES_REV[article.category]]['words'] += article.word_count
        except KeyError:
            try:
                issues[article.article_date][CATEGORIES_REV[article.category]] = {}
                if article.illustrated: issues[article.article_date]['illustrated'] = 1
                issues[article.article_date][CATEGORIES_REV[article.category]]['total'] = 1
                issues[article.article_date][CATEGORIES_REV[article.category]]['words'] = article.word_count
            except KeyError:
                issues[article.article_date] = {}
                issues[article.article_date][CATEGORIES_REV[article.category]] = {}
                if article.illustrated: issues[article.article_date]['illustrated'] = 1
                issues[article.article_date][CATEGORIES_REV[article.category]]['total'] = 1
                issues[article.article_date][CATEGORIES_REV[article.category]]['words'] = article.word_count
    issues = [ [date, issues[date]] for date in sorted(issues.keys()) ]
    return render_to_response('newspaper_month.html', {'newspaper': newspaper,
                                                       'issues': issues,
                                                       'year': year,
                                                       'month': month,
                                                       'month_label': MONTHS[int(month)]}, context_instance=RequestContext(request))
@cache_page(60 * 60)
def show_newspaper_month_line(request, newspaper_id, year, month, total_type='words'):
    series = []
    if total_type == 'number': total_type = 'total'
    newspaper = Newspaper.objects.get(newspaper_id=newspaper_id)
    newspapers = Newspaper.objects.values_list('newspaper_id', 'newspaper_title').order_by('newspaper_title')
    articles = Article.objects.filter(article_date__year=year, article_date__month=month, newspaper_id=newspaper_id, page_text='1').order_by('article_date', 'category', 'title')
    issues = {}
    if total_type == 'illustrated':
        articles = articles.filter(illustrated=True)
        for article in articles:
            try:
                issues[article.article_date.day] += 1
            except KeyError:
                issues[article.article_date.day] = 1
        data = [[issue, total] for issue, total in issues.items()]
        if data: series.append({'name': 'Illustrated article', 'data': sorted(data, key=itemgetter(0))})       
    else:
        categories = request.GET.getlist('category')
        for article in articles:
            try:
                issues[article.article_date.day][CATEGORIES_REV[article.category]]['total'] += 1
                issues[article.article_date.day][CATEGORIES_REV[article.category]]['words'] += article.word_count
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
                series.append({'name': CATEGORIES[category], 'data': sorted(data, key=itemgetter(0))})
    if total_type == 'total': total_type = 'number'
    return render_to_response('newspaper_month_line.html', {'newspaper': newspaper,
                                                            'series': json.dumps(series),
                                                            'year': year,
                                                            'month': month,
                                                            'month_label': MONTHS[int(month)],
                                                            'total_type': total_type}, context_instance=RequestContext(request))
@cache_page(60 * 60)      
def show_newspaper_issue(request, newspaper_id, year, month, day):
    newspaper = Newspaper.objects.get(newspaper_id=newspaper_id)
    newspapers = Newspaper.objects.values_list('newspaper_id', 'newspaper_title').order_by('newspaper_title')
    try:
        issue_date = datetime.date(int(year), int(month), int(day))
    except ValueError:
        articles = []
    else:
        articles = Article.objects.filter(newspaper_id=newspaper_id, article_date=issue_date, page_text='1').order_by('category', 'title')
    try:
        previous_date = Article.objects.values_list('article_date', flat=True).filter(newspaper_id=newspaper_id, page_text='1').filter(article_date__lt=issue_date).order_by('-article_date')[0]
    except IndexError:
        previous_date = None
    try:
        next_date = Article.objects.values_list('article_date', flat=True).filter(newspaper_id=newspaper_id, page_text='1').filter(article_date__gt=issue_date).order_by('article_date')[0]
    except IndexError:
        next_date = None
    issue = {}
    issue['words'] = 0
    issue['total'] = 0
    issue['illustrated'] = 0
    for article in articles:
        issue['words'] += article.word_count
        issue['total'] += 1
        if article.illustrated:
            issue['illustrated'] += 1
        category = CATEGORIES_REV[article.category]
        try:
            issue[category]['total'] += 1
            issue[category]['words'] += article.word_count
        except KeyError:
            try:
                issue[category] = {}
                issue[category]['total'] = 1
                issue[category]['words'] = article.word_count
            except KeyError:
                issue = {}
                issue[category] = {}
                issue[category]['total'] = 1
                issue[category]['words'] = article.word_count
    if articles:
        page_url = article.page_url
        page_id = re.search(r'\/(\d+)$', page_url).group(1)
    else:
        page_url = ''
        page_id = ''
    data_total = []
    data_words = []
    for short, long in CATEGORIES.items():
        try:
            if short == 'article':
                data_total.append([long, float(issue[short]['total'] - issue['illustrated']) / issue['total']])
            else:
                data_total.append([long, float(issue[short]['total']) / issue['total']])
            data_words.append([long, float(issue[short]['words']) / issue['words']])
        except KeyError:
            pass
    data_total.append(['Illustrated article', float(issue['illustrated']) / issue['total']])
    series = {'total': data_total, 'words': data_words}       
    return render_to_response('newspaper_issue.html', {'newspaper': newspaper,
                                                       'articles': articles,
                                                       'series': json.dumps(series),
                                                       'issue': issue,
                                                       'page_id': page_id,
                                                       'page_url': page_url,
                                                       'issue_date': issue_date,
                                                       'previous_date': previous_date,
                                                       'next_date': next_date}, context_instance=RequestContext(request))
            