#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from __future__ import unicode_literals

import logging

from django.core.paginator import EmptyPage
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger
from django.db.models import Count, Q
from django.http import Http404, HttpResponseServerError
from django.shortcuts import render, redirect
# from .forms import SearchForm
from .models import Article, Category, Article_Category

logger = logging.getLogger('django')

def index(request, pagenum = 1):
  '''
  首页
  '''
  # article_list = Article.objects.order_by('id').reverse()[:2]

  article_all = Article.objects.order_by('-id')

  return render(request, 'index.html',
                context = {'article_list'  : make_paginator(article_all, pagenum),
                           'category_dict' : get_category_dict()})

def article_display(request, article_id):
  '''
  文章显示页
  '''
  try:
    a_article = Article.objects.get(id = article_id)
    a_article.times += 1
    a_article.save()
    return render(request, 'blog_main/article_display.html',
                  context = {'a_article': a_article})
  except Article.DoesNotExist as e:
    # NotFound's status code is 404
    raise Http404
  except Article.MultipleObjectsReturned as e:
    raise HttpResponseServerError

def article_list_by_category(request, category_id, pagenum = 1):
  '''
  显示一个(指定的分类里的所有文章的)列表页
  '''
  try:
    current_category = Category.objects.get(id = category_id)
    article_all = current_category.article_set.all().order_by('-id')
    return render(request, 'list_by_category.html',
                  context = {'current_category' : current_category,
                             'article_list'     : make_paginator(article_all, pagenum),
                             'category_dict'    : get_category_dict()})
  except Category.DoesNotExist as e:
    # NotFound's status code is 404
    raise Http404
  except Category.MultipleObjectsReturned as e:
    raise HttpResponseServerError

def article_list_by_search(request, pagenum = 1):
  '''
  kw in 标题 or 内容
  1. 在所有文章中搜索
  2. 在当前分类中搜索
  '''
  kw = request.GET.get('q', '')
  category_id = request.GET.get('c_id', '')
  c_count = request.GET.getlist('c_count')

  if not kw:
    if category_id:
      return redirect('/category/' + category_id + '/page/1')
    else:
      return redirect('/')

  if category_id:
    try:
      current_category = Category.objects.get(id = category_id)
    except Category.DoesNotExist as e:
      raise Http404
    except Category.MultipleObjectsReturned as e:
      raise HttpResponseServerError
    manager = current_category.article_set
  else:
    current_category = None
    manager = Article.objects

  #蛋疼的构造
  a_c_group = Article_Category.objects.values('article_id')\
                                      .annotate(count = Count('article_id'))

  if len(c_count) == 0:
    # 无标签的文章id列表
    a_c_group = a_c_group.filter(count = 0).values('article_id')
    qs = manager.filter(id__in = a_c_group)

  elif len(c_count) == 1:
    if '1' in c_count:
      # 单标签的文章id列表
      a_c_group = a_c_group.filter(count = 1).values('article_id')
      qs = manager.filter(id__in = a_c_group)
    elif '2' in c_count:
      # 多标签的文章id列表
      a_c_group = a_c_group.filter(count__gt = 1).values('article_id')
      qs = manager.filter(id__in = a_c_group)
    else:
      raise Http404('c_count not in ["1", "2"], why?')

  elif len(c_count) == 2:
    # 搜索时不管标签
    qs = manager

  else:
    raise Http404('c_count>2, why?')

  # if qs is not manager:
    # print(qs.query)

  article_all = qs.filter(Q(title__icontains = kw) | Q(contents__icontains = kw))\
                       .order_by('-id')

  return render(request, 'list_by_search.html',
                context = {'article_list'     : make_paginator(article_all, pagenum),
                           'category_dict'    : get_category_dict(),
                           'kw'               : kw,
                           'current_category' : current_category})

def get_category_dict():
  '''
  页面上右侧的分类列表
  通用方法, 私有的, 不应该写成静态的
  return dict #dict是无序的~
  '''
  category_all = Category.objects.all()
  category_dict = {}
  for an_category in category_all:
    category_dict[an_category] = len(an_category.article_set.all())

  return category_dict

def make_paginator(article_all, pagenum, limit = 3):
  '''
  实现翻页按钮逻辑
  '''
  paginator = Paginator(article_all, limit)

  try:
    article_sublist = paginator.page(pagenum)  # 获取某页对应的记录
  except PageNotAnInteger:  # 如果页码不是个整数
    article_sublist = paginator.page(1)  # 取第一页的记录
  except EmptyPage:  # 如果页码太大，没有相应的记录
    article_sublist = paginator.page(paginator.num_pages)  # 取最后一页的记录

  return article_sublist
