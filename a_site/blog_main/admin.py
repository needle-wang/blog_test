#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
from __future__ import unicode_literals

from django import forms
from django.contrib import admin

from pagedown.widgets import AdminPagedownWidget

from .models import Article, Category, PicManage


class ArticleForm(forms.ModelForm):
  # 这里的字段是重写的字段
  # category = forms.ModelMultipleChoiceField(Category.objects.all(), label = u'标签')
  # 注意此处的content就是markdown编辑器所在, 但不会保存数据, 只供预览
  contents = forms.CharField(label=u'内容', widget=AdminPagedownWidget())

  class Meta:
    model = Article
    # fields保存的是可显示出来的字段
    fields = '__all__'
    # fields = ['contents', 'category']
    # fields = ['contents']


class ArticleAdmin(admin.ModelAdmin):
  list_display = ('title', 'category_list', 'pub_date', 'update_time', 'id')
  form = ArticleForm
  # 横向显示复选框
  filter_horizontal = ['category']
  # 后台显示页面中加入搜索功能
  search_fields = ['title']


admin.site.register(Article, ArticleAdmin)


class CategoryAdmin(admin.ModelAdmin):
  list_display = ('name', 'prefix_for_sort')
  # list_display = ('id', 'name', 'article_list')
  search_fields = ['name']


admin.site.register(Category, CategoryAdmin)


class PicManageAdmin(admin.ModelAdmin):
  list_display = ('name', 'url', 'create_time')
  # 替换后台的change_list.html
  # 其实就是想, 将新增功能的表单加到后台显示页中
  change_list_template = 'admin_pic_list.html'
  search_fields = ['name', 'url']
  # 这个属性是干嘛用的?
  fields = ['name', 'url']
  # 去掉 图片列表上方的 "动作 ... 执行"
  # actions_on_top = False


admin.site.register(PicManage, PicManageAdmin)
