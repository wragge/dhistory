# Create your views here.
import json
import validictory
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from haystack.views import SearchView
from dhistory.querypic.forms import QPForm
from dhistory.querypic.models import QPGraph

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
                    keywords.extend(clean_keywords(source['name']))
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
    return render(request, 'querypic-create.html', {'form': form})


def show_querypic(request, short_url):
    qpgraph = QPGraph.objects.get(short_url=short_url)
    return render(request, 'querypic-show.html', {'qpgraph': qpgraph})


class ExploreView(SearchView):
    def __name__(self):
        return "ExploreView"

    def extra_context(self):
        extra = super(ExploreView, self).extra_context()
        sort = self.request.GET.get('sort_by', 'title')
        extra['sort'] = sort
        if not self.query:
            results = QPGraph.objects.all().order_by(sort)
            paginator = Paginator(results, 25)
            page = self.request.GET.get('page')
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
    return render(request, 'querypic-help.html', {})


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
