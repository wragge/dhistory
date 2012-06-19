from urllib2 import Request, urlopen, URLError, HTTPError
from urllib import quote_plus
import datetime
import time
import re
import os
import json
from django.db.models import Count, Sum

from models import Article, Newspaper, Total

#from trove.utilities import get_url

NEWSPAPER_URL_ROOT = 'http://nla.gov.au/nla.news-title'
TROVE_API_URL = 'http://api.trove.nla.gov.au/result?zone=newspaper'
TROVE_KEY = 'ei4napgems7bf1bo'
        
def harvest_frontpages(start=0):
    '''
    Gets all newspaper articles from Trove published on page 1.
    However, this includes articles published on page 1 of supplements as well.
    '''
    url = '%s&encoding=json&key=%s&q=firstpageseq:1&reclevel=full&n=100&sortby=dateasc' % (TROVE_API_URL, TROVE_KEY)
    harvested = start
    total = 0
    tries = 0
    n = 100
    while n == 100:
        current_url = '%s&s=%s' % (url, harvested)
        print current_url
        try:
            results = json.load(get_url(current_url))
        except AttributeError, ValueError:
            if tries <= 10:
                tries += 1
                print 'Trying again in 10 seconds...'
                time.sleep(10)
                continue
            else:
                raise
        else:
            tries = 0
            if not total: total = int(results['response']['zone'][0]['records']['total'])
            articles = results['response']['zone'][0]['records']['article']
            for article in articles:
                try:
                    status = article['status']
                except KeyError:
                    status = ''
                if status == 'coming soon' or status == 'withdrawn' or article['category'] == 'Other':
                    print 'Article not available'
                else:
                    print '%s of %s -- %s' % (harvested+1, 
                                              total, 
                                              article['heading'])
                    illustrated = True if article['illustrated'] == 'Y' else False
                    article_date = datetime.date(*map(int, re.split('[^\d]', article['date'])))
                    new_article = Article.objects.create(trove_id=article['id'],
                                                    url=article['identifier'],
                                                    title=article['heading'],
                                                    article_date=article_date,
                                                    newspaper_id=article['title']['id'],
                                                    newspaper_title=article['title']['value'],
                                                    page=article['page'],
                                                    page_text=article['pageSequence'],
                                                    page_url=article['trovePageUrl'],
                                                    category=article['category'],
                                                    corrections=article['correctionCount'],
                                                    word_count=article['wordCount'],
                                                    illustrated=illustrated,
                                                    status='yes')
                harvested += 1
            n = int(results['response']['zone'][0]['records']['n'])
        
def get_page_seq(start, end):
    '''
    Add a pageSequence value to an article.
    This was necessary because I didn't realise that my search was returning
    pages from supplements until the harvest was part way through.
    The pageSequence value will allow me to filter them from the results.
    '''
    url = '%s&encoding=json&key=%s&q=firstpageseq:1&reclevel=full&n=100&sortby=dateasc' % (TROVE_API_URL, TROVE_KEY)
    harvested = start
    total = 0
    tries = 0
    n = 100
    while n == 100 and harvested <= end:
        current_url = '%s&s=%s' % (url, harvested)
        print current_url
        try:
            results = json.load(get_url(current_url))
        except AttributeError, ValueError:
            if tries <= 10:
                tries += 1
                print 'Trying again in 10 seconds...'
                time.sleep(10)
                continue
            else:
                raise
        else:
            tries = 0
            articles = results['response']['zone'][0]['records']['article']
            ids = []
            for article in articles:
                try:
                    status = article['status']
                except KeyError:
                    status = ''
                if status == 'coming soon' or status == 'withdrawn' or article['category'] == 'Other':
                    print 'Article not available'
                else:
                    if article['pageSequence'] == '1 S':
                        print '%s: %s -- %s' % (article['id'], article['pageSequence'], article['heading'])
                        ids.append(article['id'])
                    elif article['pageSequence'] != 1:
                        print '%s: %s -- %s' % (article['id'], article['pageSequence'], article['heading'])
                        Article.objects.filter(trove_id=article['id']).update(page_text=article['pageSequence'])
                harvested += 1
            if ids:
                rows = Article.objects.filter(trove_id__in=ids).update(page_text='1 S')
                print 'Rows updated: %s' % rows
                print ids
            n = int(results['response']['zone'][0]['records']['n'])

def get_titles():
    '''
    Extract newspaper titles from article table.
    '''
    titles = Article.objects.values('newspaper_id', 'newspaper_title').distinct()
    for title in titles:
        print title
        newspaper = Newspaper.objects.create(newspaper_id=int(title['newspaper_id']), newspaper_title=title['newspaper_title'])
        
def generate_totals():
    for newspaper in Newspaper.objects.all():
        get_newspaper_totals2(newspaper)
        
def get_newspaper_totals(newspaper):
    print 'Processing: %s' % newspaper.newspaper_title
    id = newspaper.newspaper_id
    dates = list(Article.objects.filter(newspaper_id=id).values_list('article_date', flat=True).distinct().order_by('article_date'))
    start_year = dates[0].year
    end_year = dates[-1].year
    all_totals = []
    for year in range(start_year, end_year+1):
        print 'Year: %s' % year
        year_issues = Article.objects.filter(page_text='1').filter(article_date__year=year,newspaper_id=id).values('article_date').distinct().count()
        print 'Issues: %s' % year_issues
        if year_issues:
            all_totals.append(Total(newspaper=newspaper, year=year, month=0, total_type='issues', value=year_issues))
        totals = Article.objects.filter(page_text='1').filter(article_date__year=year,newspaper_id=id).values('category').annotate(total=Count('id'))
        print totals
        for total in totals:
            average = float(total['total']) / year_issues
            all_totals.append(Total(newspaper=newspaper, year=year, month=0, total_type='total', category=total['category'], value=total['total'], average=average))
        words = Article.objects.filter(page_text='1').filter(article_date__year=year,newspaper_id=id).values('category').annotate(words=Sum('word_count'))
        print words
        for word in words:
            average = float(word['words']) / year_issues
            all_totals.append(Total(newspaper=newspaper, year=year, month=0, total_type='words', category=word['category'], value=word['words'], average=average))
        for month in range(1,13):
            print 'Month: %s' % month
            month_issues = Article.objects.filter(page_text='1').filter(article_date__year=year, article_date__month=month, newspaper_id=id).values('article_date').distinct().count()
            print 'Issues: %s' % month_issues
            if month_issues:
                all_totals.append(Total(newspaper=newspaper, year=year, month=month, total_type='issues', value=month_issues))            
                totals = Article.objects.filter(page_text='1').filter(article_date__year=year, article_date__month=month, newspaper_id=id).values('category').annotate(total=Count('id'))
                print totals
                for total in totals:
                    average = float(total['total']) / month_issues
                    all_totals.append(Total(newspaper=newspaper, year=year, month=month, total_type='total', category=total['category'], value=total['total'], average=average))
                words = Article.objects.filter(page_text='1').filter(article_date__year=year, article_date__month=month, newspaper_id=id).values('category').annotate(words=Sum('word_count'))
                print words
                for word in words:
                    average = float(word['words']) / month_issues
                    all_totals.append(Total(newspaper=newspaper, year=year, month=month, total_type='words', category=word['category'], value=word['words'], average=average))
    Total.objects.bulk_create(all_totals)
        
def get_newspaper_totals2(newspaper):
    categories = ['Article', 'Advertising', 'Detailed lists, results, guides', 'Family Notices', 'Literature']
    print 'Processing: %s' % newspaper.newspaper_title
    id = newspaper.newspaper_id
    dates = list(Article.objects.filter(newspaper_id=id).values_list('article_date', flat=True).distinct().order_by('article_date'))
    start_year = dates[0].year
    end_year = dates[-1].year
    for year in range(start_year, end_year+1):
        all_totals = []
        year_issues = {}
        year_totals = {}
        year_words = {}
        for cat in categories:
            year_totals[cat] = 0
            year_words[cat] = 0
        month_issues = {}
        month_totals = {}
        month_words = {}
        for m in range(1,13):
            month_issues[m] = {}
            month_totals[m] = {}
            month_words[m] = {}
            for cat in categories:
                month_totals[m][cat] = 0
                month_words[m][cat] = 0
        print 'Year: %s' % year
        articles = Article.objects.filter(page_text='1').filter(article_date__year=year,newspaper_id=id).order_by('article_date')
        for article in articles.iterator():
            year_issues[article.article_date] = 1
            year_totals[article.category] += 1
            year_words[article.category] += article.word_count
            month_issues[article.article_date.month][article.article_date] = 1
            month_totals[article.article_date.month][article.category] += 1
            month_words[article.article_date.month][article.category] += article.word_count
        year_issues = len(year_issues)
        month_issues = {month: len(issues) for month, issues in month_issues.items()}
        all_totals.append(Total(newspaper=newspaper, year=year, month=0, total_type='issues', value=year_issues))
        for category, total in year_totals.items():
            if total:
                average = float(total) / year_issues
                all_totals.append(Total(newspaper=newspaper, year=year, month=0, total_type='total', category=category, value=total, average=average))
        for category, total in year_words.items():
            if total:
                average = float(total) / year_issues
                all_totals.append(Total(newspaper=newspaper, year=year, month=0, total_type='words', category=category, value=total, average=average))
        for month, totals in month_totals.items():
            if month_issues[month]:
                all_totals.append(Total(newspaper=newspaper, year=year, month=month, total_type='issues', value=month_issues[month]))
                for category, total in totals.items():
                    if total:
                        average = float(total) / month_issues[month]
                        all_totals.append(Total(newspaper=newspaper, year=year, month=month, total_type='total', category=category, value=total, average=average))
        for month, totals in month_words.items():
            if month_issues[month]:
                for category, total in totals.items():
                    if total:
                        average = float(total) / month_issues[month]
                        all_totals.append(Total(newspaper=newspaper, year=year, month=month, total_type='words', category=category, value=total, average=average))
        Total.objects.bulk_create(all_totals)