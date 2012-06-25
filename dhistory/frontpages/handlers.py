#!/usr/bin/env python
from django.core.cache import cache
from piston.handler import BaseHandler
from dhistory.frontpages.models import Article, Newspaper

class AutocompleteHandler(BaseHandler):
    methods_allowed = ('GET',)

    def read(self, request, newspaper_id=None, year=None, month=None):
        if not newspaper_id:
            if cache.get('auto-newspapers') is None:
                results = Newspaper.objects.values_list('newspaper_id', 'newspaper_title').order_by('newspaper_title')
                cache.set('auto-newspapers', results, 60*60*24*7)
            else:
                results = cache.get('auto-newspapers')
        elif newspaper_id and not year:
            if cache.get('auto-%s' % newspaper_id) is None:
                results = Article.objects.values_list('article_date', flat=True).filter(newspaper_id=newspaper_id, page_text='1').distinct()
                results = sorted(set([date.year for date in results]))
                cache.set('auto-%s' % newspaper_id, results, 60*60*24*7)
            else:
                results = cache.get('auto-%s' % newspaper_id)
        elif newspaper_id and year and not month:
            if cache.get('auto-%s-%s' % (newspaper_id, year)) is None:
                results = Article.objects.values_list('article_date', flat=True).filter(newspaper_id=newspaper_id, article_date__year=year, page_text='1').distinct().order_by('article_date')
                results = sorted(set([date.month for date in results]))
                cache.set('auto-%s-%s' % (newspaper_id, year), results, 60*60*24*7)
            else:
                results = cache.get('auto-%s-%s' % (newspaper_id, year))
        elif newspaper_id and year and month:
            if cache.get('auto-%s-%s-%s' % (newspaper_id, year, month)) is None:
                results = Article.objects.values_list('article_date', flat=True).filter(newspaper_id=newspaper_id, article_date__year=year, article_date__month=month, page_text='1').distinct().order_by('article_date')
                results = sorted(set([date.day for date in results]))
                cache.set('auto-%s-%s-%s' % (newspaper_id, year, month), results, 60*60*24*7)
            else:
                results = cache.get('auto-%s-%s-%s' % (newspaper_id, year, month))
        return results