from django import forms


class QPForm(forms.Form):
    sources = forms.CharField()
