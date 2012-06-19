from django.db import models

# Create your models here.

class Article(models.Model):
    trove_id = models.IntegerField()
    url = models.URLField(blank=True)
    title = models.TextField(blank=True)
    article_date = models.DateField(blank=True, null=True)
    newspaper_id = models.IntegerField(blank=True, null=True)
    newspaper_title = models.TextField(blank=True)
    page = models.IntegerField(blank=True, null=True)
    page_url = models.URLField(blank=True)
    corrections = models.IntegerField(default=0, blank=True)
    category = models.CharField(max_length=100, blank=True)
    word_count = models.IntegerField(blank=True, null=True)
    illustrated = models.BooleanField(default=False)
    status = models.CharField(max_length=5, default='yes', choices=(('yes', 'yes'),('no', 'no'),('maybe','maybe')))
    harvested = models.DateTimeField(auto_now=True)
    page_text = models.CharField(max_length=20, blank=True, null=True)
    
class Newspaper(models.Model):
    newspaper_id = models.IntegerField(blank=True, null=True)
    newspaper_title = models.TextField(blank=True)

class Total(models.Model):
    newspaper = models.ForeignKey('Newspaper', null=True)
    year = models.IntegerField(blank=True, null=True)
    month = models.IntegerField(blank=True, null=True)
    category = models.CharField(max_length=50, blank=True)
    total_type = models.CharField(max_length=50, blank=True)
    value = models.IntegerField(default=0)
    average = models.FloatField(default=0)
