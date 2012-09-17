from django import forms
from haystack.forms import SearchForm


class QPForm(forms.Form):

    creator = forms.CharField(max_length=50, required=False)
    creator_email = forms.EmailField()
    creator_url = forms.URLField(required=False)
    title = forms.CharField(max_length=200)
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'input-xlarge'}))
    sources = forms.CharField(widget=forms.HiddenInput)


class ExploreForm(SearchForm):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'input-medium search-query'}))
    sort_by = forms.CharField(required=False)

    def search(self):
        if not self.is_valid():
            return self.no_query_found()
        if not self.cleaned_data.get('q'):
            return self.no_query_found()
        sqs = self.searchqueryset.auto_query(self.cleaned_data['q'])
        if self.load_all:
            sqs = sqs.load_all()
        if self.cleaned_data['sort_by']:
            sqs = sqs.order_by(self.cleaned_data['sort_by'])
        return sqs

