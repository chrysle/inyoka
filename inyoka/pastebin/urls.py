# -*- coding: utf-8 -*-
"""
    inyoka.pastebin.urls
    ~~~~~~~~~~~~~~~~~~~~

    The urls for the pastebin service.

    :copyright: (c) 2007-2014 by the Inyoka Team, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
from django.conf.urls import patterns

urlpatterns = patterns('inyoka.pastebin.views',
    (r'^$', 'index'),
    (r'^(\d+)/$', 'display'),
    (r'^raw/(\d+)/$', 'raw'),
    (r'^browse/$', 'browse'),
    (r'^delete/(\d+)/$', 'delete'),
)


handler404 = 'inyoka.utils.http.global_not_found'
