from haystack import indexes
from dhistory.querypic.models import QPGraph


class QPGraphIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    creator = indexes.CharField(model_attr='creator')
    title = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr='description')
    created = indexes.DateTimeField(model_attr='created')

    def get_model(self):
        return QPGraph
