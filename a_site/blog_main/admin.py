#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from __future__ import unicode_literals

from django import forms
from django.contrib import admin
from pagedown.widgets import AdminPagedownWidget

from .models import Article, Category



class ArticleForm(forms.ModelForm):
  # 这里的字段是重写的字段
  # category = forms.ModelMultipleChoiceField(Category.objects.all(), label = u'标签')
  # 注意此处的content就是markdown编辑器所在, 但不会保存数据, 只供预览
  contents = forms.CharField(label = u'内容', widget=AdminPagedownWidget())

  class Meta:
    model = Article
    # fields保存的是可显示出来的字段
    fields = '__all__'
    # fields = ['contents', 'category']
    # fields = ['contents']

class ArticleAdmin(admin.ModelAdmin):
  list_display = ('title', 'category_list', 'pub_date','update_time', 'id')
  form = ArticleForm

admin.site.register(Article, ArticleAdmin)

class CategoryAdmin(admin.ModelAdmin):
  list_display = ('name', 'prefix_for_sort')
  # list_display = ('id', 'name', 'article_list')

admin.site.register(Category, CategoryAdmin)
