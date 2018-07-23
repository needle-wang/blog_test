#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from __future__ import unicode_literals

from django.apps import AppConfig


class BlogMainConfig(AppConfig):
  name = 'blog_main'  # 这是model的名字, 不能改
  verbose_name = '博客app'
