# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Article'
        db.create_table('frontpages_article', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('trove_id', self.gf('django.db.models.fields.IntegerField')()),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('title', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('article_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('newspaper_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('newspaper_title', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('page', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('page_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('corrections', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('word_count', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('illustrated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('status', self.gf('django.db.models.fields.CharField')(default='yes', max_length=5)),
            ('harvested', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('page_text', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
        ))
        db.send_create_signal('frontpages', ['Article'])

        # Adding model 'Newspaper'
        db.create_table('frontpages_newspaper', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('newspaper_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('newspaper_title', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('frontpages', ['Newspaper'])

        # Adding model 'Total'
        db.create_table('frontpages_total', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('newspaper', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['frontpages.Newspaper'], null=True)),
            ('year', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('month', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('total_type', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('value', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('frontpages', ['Total'])


    def backwards(self, orm):
        # Deleting model 'Article'
        db.delete_table('frontpages_article')

        # Deleting model 'Newspaper'
        db.delete_table('frontpages_newspaper')

        # Deleting model 'Total'
        db.delete_table('frontpages_total')


    models = {
        'frontpages.article': {
            'Meta': {'object_name': 'Article'},
            'article_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'corrections': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'harvested': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustrated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'newspaper_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'newspaper_title': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'page': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'page_text': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'page_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'yes'", 'max_length': '5'}),
            'title': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'trove_id': ('django.db.models.fields.IntegerField', [], {}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'word_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'frontpages.newspaper': {
            'Meta': {'object_name': 'Newspaper'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'newspaper_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'newspaper_title': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'frontpages.total': {
            'Meta': {'object_name': 'Total'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'month': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'newspaper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['frontpages.Newspaper']", 'null': 'True'}),
            'total_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['frontpages']