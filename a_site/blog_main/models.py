#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from __future__ import unicode_literals
from django.db import models
# from django.utils.encoding import python_2_unicode_compatible


class Article(models.Model):

  title = models.CharField(u'标题', max_length = 50)
  contents = models.TextField(u'内容')
  times = models.IntegerField(u'阅读量', default = 0, editable = False)

  pub_date = models.DateTimeField(u'发表时间', auto_now_add = True, editable = True)
  update_time = models.DateTimeField(u'最后一次修改时间', auto_now = True, null = True)
  category = models.ManyToManyField('Category', through = 'Article_Category')

  def __str__(self):        # Python3
    return self.title

  def __unicode__(self):    # Python2
    return self.__str__()

  def category_list(self):     # 视作Article的一个属性
    return ','.join([i.name for i in self.category.all()])

  # def __str__(self):
    # return self.title
  class Meta:
    verbose_name = '文章'
    verbose_name_plural = verbose_name

class Category(models.Model):
  name = models.CharField(u'类名', max_length = 50)

  def __str__(self):        # Python3
    return self.name

  def __unicode__(self):    # Python2
    return self.__str__()

  # def article_list(self):
    # return ','.join([i.title for i in self.article_set.all()])

  class Meta:
    verbose_name = '类名'
    verbose_name_plural = verbose_name

class Article_Category(models.Model):
  '''
  多对多的关系表, model化 便于查询
  '''
  article = models.ForeignKey(Article)
  category = models.ForeignKey(Category)

