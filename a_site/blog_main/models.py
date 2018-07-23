#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from __future__ import unicode_literals

from django.db import models

from a_site.settings import OWNER

# from django.utils.encoding import python_2_unicode_compatible


class Article(models.Model):

  title = models.CharField(verbose_name=u'标题', max_length=100)
  digest = models.CharField(
    verbose_name=u'摘要', default='摘要:...', max_length=200)
  contents = models.TextField(verbose_name=u'内容')
  times = models.DecimalField(
    verbose_name=u'阅读量',
    default=0,
    max_digits=15,
    decimal_places=0,
    editable=False)
  # category = models.ManyToManyField('Category', through = 'Article_Category')
  category = models.ManyToManyField(u'Category', verbose_name=u'标签')
  is_original = models.BooleanField(verbose_name=u'原创', default=True)
  original_author = models.CharField(
    verbose_name=u'原文作者', default=OWNER, max_length=100, null=True, blank=True)
  original_url = models.URLField(
    verbose_name=u'原文地址(原创文可不填)', null=True, blank=True)

  # 下面两个时间为什么不在后台显示?
  pub_date = models.DateTimeField(
    verbose_name=u'发表时间', auto_now_add=True, editable=True)
  update_time = models.DateTimeField(
    verbose_name=u'最后一次修改时间', auto_now=True, null=True)

  def __str__(self):  # Python3
    return self.title

  def __unicode__(self):  # Python2
    return self.__str__()

  def category_list(self):  # 视作Article的一个属性
    return ','.join([i.name for i in self.category.all()])

  # def __str__(self):
  # return self.title
  class Meta:
    verbose_name = u'文章'
    verbose_name_plural = verbose_name


class Category(models.Model):
  '''
  分类向来是个大问题(标签或者分类会有从属, 交叉等关系)
  我现在不想解决这么复杂的问题, 手动设置吧
  '''
  name = models.CharField(verbose_name=u'标签', max_length=50)
  prefix_for_sort = models.CharField(
    verbose_name=u'标签前缀(用于子类标签排序)', default=u'1.1', max_length=60)

  def __str__(self):  # Python3
    return self.name

  def __unicode__(self):  # Python2
    return self.__str__()

  # def article_list(self):
  # return ','.join([i.title for i in self.article_set.all()])

  class Meta:
    verbose_name = u'标签'
    verbose_name_plural = verbose_name
    ordering = [u'prefix_for_sort']


# class Article_Category(models.Model):
# '''
# 多对多的关系表, model化可便于查询
# 但为什么会导致Article的category字段无法在admin后台显示?
# 因为: 自定义的显式的多对多model与隐式的方法集不同, 见文档
# 还是不要自定义, 我搞不定
# 另: 隐式的model名字是: Article_category
# '''
# article = models.ForeignKey(Article, on_delete=models.CASCADE)
# category = models.ForeignKey(Category, on_delete=models.CASCADE)


class PicManage(models.Model):
  name = models.CharField(
    verbose_name=u'名称', max_length=50, null=True, blank=True)
  # 没准改图片名比建日期目录更好一些.
  url = models.ImageField(
    verbose_name=u'URL', upload_to=u'uploadImages/%Y/%m/%d/')
  create_time = models.DateTimeField(u'创建时间', auto_now_add=True)

  def __str__(self):  # Python3
    return self.name

  def __unicode__(self):  # Python2
    return self.__str__()

  class Meta:
    verbose_name = u'图片'
    verbose_name_plural = verbose_name
