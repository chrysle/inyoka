"""
    inyoka.utils.feeds
    ~~~~~~~~~~~~~~~~~~~

    Utils for creating an atom feed.

    :copyright: (c) 2007-2023 by the Inyoka Team, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
from django.conf import settings
from django.contrib.syndication.views import Feed
from django.http import Http404
from django.utils.feedgenerator import Atom1Feed
from django.utils.text import Truncator

from inyoka.utils.urls import href


class InyokaAtomFeed(Feed):
    feed_type = Atom1Feed
    MODES = frozenset(('full', 'short', 'title'))
    supports_modes = True

    def _check_content_mode(self, kwargs):
        if not self.supports_modes:
            return

        self.mode = kwargs.get('mode')
        if self.mode not in self.MODES:
            raise Http404()

    def _check_item_count(self, kwargs):
        count = int(kwargs['count'])

        try:
            available = settings.AVAILABLE_FEED_COUNTS[self.name]
        except KeyError:
            raise Http404()

        count = min(count, max(available))

        if count not in available:
            raise Http404()

        self.count = count

    def get_object(self, request, *args, **kwargs):
        self._check_content_mode(kwargs)
        self._check_item_count(kwargs)

    def feed_copyright(self):
        return href('portal', 'lizenz')

    def _shorten_html(self, html):
        return Truncator(html).words(100, html=True)
