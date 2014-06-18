# Create your views here.
import urllib2
import json
import validictory
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from haystack.views import SearchView
from dhistory.querypic.forms import QPForm
from dhistory.querypic.models import QPGraph
from django.views.decorators.cache import cache_page

JSON_SCHEMA = {
                "type": "object",
                "properties": {
                    "sources": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "query": {"type": "string"},
                                "web_query": {"type": "string"},
                                "api_query": {"type": "string"},
                                "interval": {"type": "string"},
                                "country": {"type": "array"},
                                "dates": {"type": "string"},
                                "limits": {"type": "object", "required": False},
                                "data": {
                                    "type": "object",
                                    "additionalProperties": {
                                        "type": "object",
                                        "properties": {
                                            "all": {"type": "integer"},
                                            "total": {"type": "integer"},
                                            "ratio": {"type": "number"}
                                        },
                                        "additionalProperties": False
                                    }
                                },
                            },
                            "additionalProperties": False,
                        },

                    },
                },
            }

START_YEAR = 1900
END_YEAR = 2014

@cache_page(60 * 60 * 6)
def create_collectionview(request):
    preset = "false"
    selected_nucs = request.GET.getlist('nuc')
    query = request.GET.get('q')
    year_start = request.GET.get('start')
    year_end = request.GET.get('end')
    if selected_nucs or query or year_start or year_end:
        preset = "true"
    year_start = int(year_start) if year_start else START_YEAR
    year_end = int(year_end) if year_end else END_YEAR
    response = urllib2.urlopen('http://trove.nla.gov.au/general/libraries')
    nucs = json.load(response)
    return render(request, 'collectionview-create.html', {
        'nucs': nucs, 
        'selected_nucs': selected_nucs, 
        'years': range(1800, 2015),
        'query': query,
        'start': year_start,
        'end': year_end,
        'preset': preset
        })


def show_tree(request):
    return render(request, 'tree.html', {})


def show_sunburst(request):
    return render(request, 'trove-sunburst.html', {})

def show_sunburst_embed(request):
    return render(request, 'trove-sunburst-iframe.html', {})


def show_querypic_form(request):
    if request.method == 'POST':
        form = QPForm(request.POST)
        print form.errors
        if form.is_valid():
            creator = form.cleaned_data['creator']
            email = form.cleaned_data['creator_email']
            creator_url = form.cleaned_data['creator_url']
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            data = form.cleaned_data['sources']
            # Validation of json
            try:
                json_data = json.loads(data)
                validictory.validate(json_data, JSON_SCHEMA)
            except ValueError:
                #return render(request, 'querypic-create.html', {'form': form})
                raise
            else:
                keywords = []
                for source in json_data['sources']:
                    keywords.extend(clean_keywords(source['name'].replace('+', ' ')))
                keywords = ' '.join(keywords)
                qpgraph = QPGraph.objects.create(creator=creator,
                    creator_email=email,
                    creator_url=creator_url,
                    title=title,
                    description=description,
                    data=data,
                    keywords=keywords)
                short_url = qpgraph.short_url
                return HttpResponseRedirect('/querypic/%s/' % short_url)
        else:
            form = QPForm()
    else:
        form = QPForm()
    return render(request, 'collectionview-create.html', {'form': form})


def show_querypic(request, short_url):
    qpgraph = QPGraph.objects.get(short_url=short_url)
    return render(request, 'querypic-show.html', {'qpgraph': qpgraph})


class ExploreView(SearchView):
    def __name__(self):
        return "ExploreView"

    def build_page(self):
        """
        Paginates the results appropriately.

        In case someone does not want to use Django's built-in pagination, it
        should be a simple matter to override this method to do what they would
        like.
        """
        if self.query:
            try:
                page_no = int(self.request.GET.get('page', 1))
            except (TypeError, ValueError):
                raise Http404("Not a valid number for page.")

            if page_no < 1:
                raise Http404("Pages should be 1 or greater.")

            start_offset = (page_no - 1) * self.results_per_page
            self.results[start_offset:start_offset + self.results_per_page]

            paginator = Paginator(self.results, self.results_per_page)

            try:
                page = paginator.page(page_no)
            except InvalidPage:
                raise Http404("No such page!")

            return (paginator, page)
        else:
            return (None, None)

    def extra_context(self):
        extra = super(ExploreView, self).extra_context()
        sort = self.request.GET.get('sort_by', 'title')
        extra['sort'] = sort
        if not self.query:
            results = QPGraph.objects.all().order_by(sort)
            paginator = Paginator(results, 25)
            page = self.request.GET.get('page')
            print 'error'
            try:
                qpgraphs = paginator.page(page)
            except PageNotAnInteger:
                qpgraphs = paginator.page(1)
            except EmptyPage:
                qpgraphs = paginator.page(paginator.num_pages)
            extra['qpgraphs'] = qpgraphs
        return extra


def show_home(request):
    qpgraphs = QPGraph.objects.all().order_by('-created')[:5]
    return render(request, 'querypic-home.html', {'qpgraphs': qpgraphs})


def show_help(request):
    return render(request, 'tt-help.html', {})


def list_querypics(request):
    sort = request.GET.get('sort_by', 'title')
    results = QPGraph.objects.all().order_by(sort)
    paginator = Paginator(results, 25)
    page = request.GET.get('page')
    try:
        qpgraphs = paginator.page(page)
    except PageNotAnInteger:
        qpgraphs = paginator.page(1)
    except EmptyPage:
        qpgraphs = paginator.page(paginator.num_pages)
    return render(request, 'querypic-browse.html', {'qpgraphs': qpgraphs, 'sort': sort})


def clean_keywords(string):
    ignore = ['AND', 'NOT', 'OR']
    keywords = [keyword.strip('(').strip(')') for keyword in string.split() if keyword not in ignore]
    return keywords
