from django.db import models
from django.utils.http import int_to_base36
from django.db.models.signals import post_save

# Create your models here.


class QPGraph(models.Model):
    short_url = models.CharField(max_length=10)
    creator = models.CharField(max_length=50, blank=True, null=True)
    creator_email = models.EmailField()
    creator_url = models.URLField(blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    data = models.TextField()
    keywords = models.CharField(max_length=250, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)


def add_short_url(sender, **kwargs):
    qpgraph = kwargs['instance']
    if not qpgraph.short_url:
        qpgraph.short_url = int_to_base36((100 + qpgraph.id))
        qpgraph.save()


post_save.connect(add_short_url, sender=QPGraph)
