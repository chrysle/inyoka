# -*- coding: utf-8 -*-
"""
    inyoka.planet.tasks
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    The ``sync`` function should be called periodically to check for new
    articles.  It checks whether the last syncronization of a blog is more
    than ``PLANET_SYNC_TIME`` ago and updates them.

    It'd be ideal if ``sync`` was called every 30 minutes.


    :copyright: (c) 2007-2015 by the Inyoka Team, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
# Secure XML libraries till a python solution exists.
# We already patch in inyoka, hence we just import inyoka before feedparser.
import inyoka

# And further patch it so feedparser works :/
import xml.sax
make_parser = xml.sax.make_parser
xml.sax.make_parser = lambda x: make_parser()
# End XML patching.

import feedparser
import re
import socket
import logging

from time import time
from datetime import datetime

from django.utils.encoding import force_unicode
from django.utils.html import escape

from celery.task import periodic_task
from celery.task.schedules import crontab

from dateutil.parser import parse as dateutil_parse

from inyoka.planet.models import Blog, Entry
from inyoka.utils.html import cleanup_html


# set a default timeout. Otherwise fetching some feeds might cause the script
# to block forever
socket.setdefaulttimeout(20.0)

# enable logging
logger = logging.getLogger(__name__)

HTML_MIMETYPES = frozenset(('text/html', 'application/xml+xhtml', 'application/xhtml+xml'))
_par_re = re.compile(r'\n{2,}')


def nl2p(s):
    """Add paragraphs to a text."""
    return u'\n'.join(u'<p>%s</p>' % p for p in _par_re.split(s))


def dateutilDateHandler(aDateString):
    return dateutil_parse(aDateString).utctimetuple()

feedparser.registerDateHandler(dateutilDateHandler)


@periodic_task(run_every=crontab(minute='*/15'))
def sync():
    """
    Performs a synchronization.  Articles that are already syncronized aren't
    touched anymore.
    """
    for blog in Blog.objects.filter(active=True):
        logger.debug(u'syncing blog %s' % blog.name)
        # parse the feed. feedparser.parse will never given an exception
        # but the bozo bit might be defined.
        try:
            feed = feedparser.parse(blog.feed_url)
        except UnicodeDecodeError:
            logger.debug(u'UnicodeDecodeError on %s' % blog.feed_url)
            continue
        except LookupError:
            logger.debug(u'LookupError on %s' % blog.feed_url)
            continue

        blog_author = feed.get('author') or blog.name
        blog_author_detail = feed.get('author_detail')

        for entry in feed.entries:
            # get the guid. either the id if specified, otherwise the link.
            # if none is available we skip the entry.
            guid = entry.get('id') or entry.get('link')
            if not guid:
                logger.debug(u' no guid found, skipping')
                continue

            try:
                old_entry = Entry.objects.get(guid=guid)
            except Entry.DoesNotExist:
                old_entry = None

            # get title, url and text. skip if no title or no text is
            # given. if the link is missing we use the blog link.
            if entry.get('title_detail'):
                title = entry.title_detail.get('value') or ''
                if entry.title_detail.get('type') in HTML_MIMETYPES:
                    title = cleanup_html(title, make_xhtml=True,
                                         id_prefix='entry-title-%x' % int(time()))
                    # cleanup_html adds <p> around the text, remove it again
                    title = title[3:-4]
                else:
                    title = escape(title)
            else:
                logger.debug(u' no title found for %r, skipping' % guid)
                continue

            url = entry.get('link') or blog.blog_url
            text = 'content' in entry and entry.content[0] or \
                   entry.get('summary_detail')

            if not text:
                logger.debug(u'no text found for %r, skipping' % guid)
                continue

            # if we have an html text we use that, otherwise we HTML
            # escape the text and use that one. We also handle XHTML
            # with our tag soup parser for the moment.
            if text.get('type') in HTML_MIMETYPES:
                text = cleanup_html(text.get('value') or '', make_xhtml=True,
                                    id_prefix='entry-text-%x' % int(time()))
            else:
                text = escape(nl2p(text.get('value') or ''))

            # get the pub date and updated date. This is rather complex
            # because different feeds do different stuff
            pub_date = entry.get('published_parsed') or \
                entry.get('created_parsed') or \
                entry.get('date_parsed')
            updated = entry.get('updated_parsed') or pub_date
            pub_date = pub_date or updated

            # if we don't have a pub_date we skip.
            if not pub_date:
                logger.debug(u' no pub_date for %r found, skipping' % guid)
                continue

            # convert the time tuples to datetime objects.
            pub_date = datetime(*pub_date[:6])
            updated = datetime(*updated[:6])

            # get the blog author or fall back to blog default.
            author = entry.get('author') or blog_author
            author_detail = entry.get('author_detail') or blog_author_detail
            if not author and author_detail:
                author = author_detail.get('name')
            if not author:
                logger.debug(u' no author for entry %r found, skipping' % guid)
            author_homepage = author_detail and author_detail.get('href') \
                or url

            # create a new entry object based on the data collected or
            # update the old one.
            entry = old_entry or Entry()
            for n in ('blog', 'guid', 'title', 'url', 'text', 'pub_date',
                      'updated', 'author', 'author_homepage'):
                # prevent mysql warnings
                try:
                    max_length = entry._meta.get_field(n).max_length
                except AttributeError:
                    max_length = None
                if isinstance(locals()[n], basestring):
                    setattr(entry, n, force_unicode(locals()[n][:max_length]).encode('utf-8'))
                else:
                    setattr(entry, n, locals()[n])
            try:
                entry.save()
                logger.debug(u' synced entry %r' % guid)
            except Exception as exc:
                logger.debug(u' Error on entry %r: %r' % (guid, exc))
        blog.last_sync = datetime.utcnow()
        blog.save()