from django.db import models
from django.utils.http import int_to_base36

# Create your models here.


class QPGraph(models.Model):
    short_url = models.CharField(max_length=10)
    creator = models.CharField(max_length=50, blank=True, null=True)
    creator_email = models.EmailField()
    creator_url = models.URLField(blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.short_url = int_to_base36((100 * self.id))
        super(QPGraph, self).save(*args, **kwargs)
