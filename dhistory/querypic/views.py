# Create your views here.
import json
from django.shortcuts import render
from dhistory.querypic.forms import QPForm
from dhistory.querypic.models import QPGraph

def show_querypic(request):
    if request.method == 'POST':
        form = QPForm(request.POST)
        if form.is_valid():
            creator = form.cleaned_date['creator']
            email = form.cleaned_date['creator_email']
            creator_url = form.cleaned_date['creator_url']
            title = form.cleaned_date['title']
            description = form.cleaned_date['description']
            data = form.cleaned_data['sources']
            # Validation of json
            try:
                json_data = json.loads(data)
                # Validate here
            except ValueError:
                return render(request, 'index.html', {'form': form, 'sources': None})
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
        else:
            form = QPForm()
    else:
        form = QPForm()
    return render(request, 'index.html', {'form': form})


def clean_keywords(string):
    ignore = ['AND', 'NOT', 'OR']
    keywords = [keyword.strip('(').strip(')') for keyword in string.split() if keyword not in ignore]
    return keywords
