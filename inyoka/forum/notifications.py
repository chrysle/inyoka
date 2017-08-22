# -*- coding: utf-8 -*-
"""
    inyoka.forum.notifications
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Utilities for forum notifications.

    :copyright: (c) 2007-2017 by the Inyoka Team, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
from celery import shared_task
from django.conf import settings
from django.utils import translation
from django.utils.translation import ugettext as _

from inyoka.utils import ctype
from inyoka.utils.logger import logger
from inyoka.utils.notification import queue_notifications


def send_newtopic_notifications(user, post, topic, forum):
    from inyoka.portal.models import User
    # NOTE: we always notify about new topics, even if the forum was
    # not visited, because unlike the posts you won't see
    # other new topics

    version_number = topic.get_ubuntu_version()

    data = {'author_unsubscribe': post.author.get_absolute_url('unsubscribe'),
          'author_username': post.author.username,
          'forum_id': forum.id,
          'forum_name': forum.name,
          'forum_unsubscribe': forum.get_absolute_url('unsubscribe'),
          'post_url': post.get_absolute_url(),
          'topic_title': topic.title,
          'topic_version': str(topic.get_ubuntu_version()),
          'topic_version_number': version_number.number if version_number else None}

    queue_notifications.delay(user.id, 'user_new_topic',
        _(u'%(username)s has created a new topic') % {
            'username': data.get('author_username')},
        data,
        include_notified=True,
        filter={'content_type_id': ctype(User).pk, 'object_id': user.id},
        callback=notify_forum_subscriptions.subtask(args=(user.id, data)))


@shared_task
def notify_forum_subscriptions(notified_users, request_user_id, data):
    from inyoka.forum.models import Forum
    with translation.override(settings.LANGUAGE_CODE):
        # Inform users who subscribed to the forum
        queue_notifications.delay(request_user_id, 'new_topic', _(
            u'“%(topic)s” – Topic in forum “%(forum)s”') % {
                'forum': data.get('forum_name'),
                'topic': data.get('topic_title')
            },
            data,
            include_notified=True,
            filter={
                'content_type_id': ctype(Forum).pk,
                'object_id': data.get('forum_id')
            },
            callback=notify_ubuntu_version_subscriptions.subtask(
                args=(request_user_id, data)
            ),
            exclude={'user_id__in': notified_users},
        )


@shared_task
def notify_ubuntu_version_subscriptions(notified_users, request_user_id, data):
    with translation.override(settings.LANGUAGE_CODE):
        if data.get('topic_version') is not None:
            queue_notifications.delay(request_user_id, 'new_topic_ubuntu_version',
                _(u'“%(topic)s” – Topic with version %(version)s') % {
                    'version': data.get('topic_version'),
                    'topic': data.get('topic_title')},
                data,
                include_notified=True,
                filter={'ubuntu_version': data.get('topic_version_number')},
                exclude={'user_id__in': notified_users})


def send_edit_notifications(user, post, topic, forum):
    from inyoka.forum.models import Topic

    data = {'author_unsubscribe': post.author.get_absolute_url('unsubscribe'),
          'author_username': post.author.username,
          'forum_name': forum.name,
          'post_url': post.get_absolute_url(),
          'topic_id': topic.id,
          'topic_title': topic.title,
          'topic_unsubscribe': topic.get_absolute_url('unsubscribe')}

    # notify about new answer in topic for topic-subscriptions
    queue_notifications.delay(user.id, 'new_post',
        _(u'“%(topic)s” – Reply from “%(username)s“') % {
            'topic': data.get('topic_title'),
            'username': data.get('author_username')},
        data,
        filter={'content_type_id': ctype(Topic).pk, 'object_id': data.get('topic_id')},
        callback=notify_member_subscriptions.subtask(args=(user.id, data)))


@shared_task
def notify_member_subscriptions(notified_users, request_user_id, data):
    from inyoka.portal.models import User
    # notify about new answer in topic for member-subscriptions
    queue_notifications.delay(
        request_user_id,
        'user_new_post',
        _(u'New answer from user „{username}”').format(username=data.get('author_username')),
        data, include_notified=True,
        filter={'content_type_id': ctype(User).pk, 'object_id': request_user_id},
        exclude={'user_id__in': notified_users})


def send_discussion_notification(user, page):
    from inyoka.wiki.models import Page
    data = {'creator': user.username,
          'page_id': page.id,
          'page_title': page.title,
          'page_unsubscribe': page.get_absolute_url('unsubscribe'),
          'topic_unsubscribe': page.topic.get_absolute_url('subscribe'),
          'topic_url': page.topic.get_absolute_url()}

    # also notify if the user has not yet visited the page,
    # since otherwise he would never know about the topic
    queue_notifications.delay(user.id, 'new_page_discussion',
        _(u'New discussion regarding the page “%(page)s” created') % {
            'page': data.get('page_title')},
        data,
        filter={'content_type_id': ctype(Page).pk, 'object_id': data.get('page_id')})


def send_deletion_notification(user, topic, reason):
    from inyoka.forum.models import Topic
    data = {'mod': user.username,
          'reason': reason,
          'topic_id': topic.id,
          'topic_title': topic.title}

    queue_notifications.delay(user.id, 'topic_deleted',
        _(u'The topic “%(topic)s” has been deleted') % {
            'topic': data.get('topic_title')},
        data,
        filter={'content_type_id': ctype(Topic).pk, 'object_id': data.get('topic_id')})


def send_notification_for_topics(request_user_id, template, template_args, subject, topic_ids, include_forums=False,
                                 forum_ids=None):
    from inyoka.forum.models import Topic, Forum

    notification_args = {
        'request_user_id': request_user_id,
        'template': template,
        'subject': subject,
        'args': template_args
    }

    topic_subscribers = {
        'content_type_id': ctype(Topic).pk,
        'object_id__in': topic_ids,
    }
    notified_users = queue_notifications(filter=topic_subscribers, **notification_args)

    logger.debug('Notified for template {}: {}'.format(template, notified_users))

    if include_forums:
        forum_subscribers = {
            'content_type_id': ctype(Forum).pk,
            'object_id__in': forum_ids,
        }
        notified_users = queue_notifications(filter=forum_subscribers, exclude={'user_id__in': notified_users}, **notification_args)
        logger.debug('Notified for include_forums with template {}: {}'.format(template, notified_users))
