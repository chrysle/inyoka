#-*- coding: utf-8 -*-
from mock import patch
from random import randint

from django.conf import settings
from django.test import TestCase

from inyoka.forum.acl import PRIVILEGES_BITS
from inyoka.forum.constants import TOPICS_PER_PAGE
from inyoka.forum.models import Forum, Topic, Post, Privilege
from inyoka.forum.views import topiclist
from inyoka.portal.user import User, PERMISSION_NAMES
from inyoka.portal.models import Subscription
from inyoka.utils.test import InyokaClient


class TestViews(TestCase):

    client_class = InyokaClient
    permissions = sum(PERMISSION_NAMES.keys())
    privileges = sum(PRIVILEGES_BITS.values())

    def setUp(self):
        self.admin = User.objects.register_user('admin', 'admin', 'admin', False)
        self.user = User.objects.register_user('user', 'user', 'user', False)
        self.admin._permissions = self.permissions
        self.admin.save()

        self.forum1 = Forum.objects.create(name='Forum 1')
        self.forum2 = Forum.objects.create(name='Forum 2', parent=self.forum1)
        self.forum3 = Forum.objects.create(name='Forum 3', parent=self.forum1)

        forums = [self.forum1, self.forum2, self.forum3]

        for f in forums:
            Privilege.objects.create(user=self.admin, forum=f,
                    positive=self.privileges, negative=0)

        self.topic = Topic.objects.create(title='A test Topic', author=self.user,
                forum=self.forum2)
        self.post = Post.objects.create(text=u'Post 1', author=self.user,
                topic=self.topic)

        self.client.defaults['HTTP_HOST'] = 'forum.%s' % settings.BASE_DOMAIN_NAME
        self.client.login(username='admin', password='admin')

    def setUp_pagination(self):
        """ Create enough topics for pagination test """

        def newpost(position, topic):
            Post.objects.create(topic=topic, text="More Posts " +
                                randint(1000, 100000).__str__(),
                                author=self.user, position=position)
        def newtopic():
            t = Topic.objects.create(title="Title " +
                                     randint(1000, 100000).__str__(),
                                     author=self.user, forum=self.forum3)
            p = Post.objects.create(topic=t, text="Post " +
                                    randint(1000, 100000).__str__(),
                                    author=self.user, position=0)
            t.first_post_id = p.id
            t.save()
            for i in xrange(1, 2):
                newpost(i, t)

        for i in xrange(1, 40):
            newtopic()


    def test_reported_topics(self):
        response = self.client.get('/reported_topics/')
        self.assertEqual(response.status_code, 200)

    @patch('inyoka.middlewares.security.SecurityMiddleware._make_token',
            return_value='csrf_key')
    @patch('inyoka.forum.views.send_notification')
    def test_movetopic(self, mock_send, mock_security):
        self.assertEqual(Topic.objects.get(id=self.topic.id).forum_id,
                self.forum2.id)
        response = self.client.post('/topic/%s/move/' % self.topic.slug,
                    {'_form_token': 'csrf_key', 'forum': self.forum3.id})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(mock_send.call_count, 1) #only the topic author
        mock_send.assert_called_with(self.user, 'topic_moved',
            u'Your topic “A test Topic“ was moved.', {
                'username': self.user.username, 'topic': self.topic,
                'mod': self.admin.username, 'forum_name': 'Forum 3',
                'old_forum_name': 'Forum 2'})

        self.assertEqual(Topic.objects.get(id=self.topic.id).forum_id,
                self.forum3.id)

    def test_subscribe(self):
        self.client.login(username='user', password='user')
        useraccess = Privilege.objects.create(user=self.user, forum=self.forum2,
            positive=PRIVILEGES_BITS['read'], negative=0)

        self.client.get('/topic/%s/subscribe/' % self.topic.slug)
        self.assertTrue(
                   Subscription.objects.user_subscribed(self.user, self.topic))

        # Test for unsubscribe-link in the usercp if the user has no more read 
        # access to a subscription
        useraccess.positive = 0
        useraccess.save()
        response = self.client.get('/usercp/subscriptions/', {}, False,
                         HTTP_HOST='portal.%s' % settings.BASE_DOMAIN_NAME)
        self.assertTrue(('/topic/%s/unsubscribe/?next=' % self.topic.slug)
                         in response.content.decode("utf-8"))

        forward_url = 'http://portal.%s/myfwd' % settings.BASE_DOMAIN_NAME
        response = self.client.get('/topic/%s/unsubscribe/' % self.topic.slug,
                                    { 'next': forward_url })
        self.assertFalse(
                   Subscription.objects.user_subscribed(self.user, self.topic))
        self.assertEqual(response['location'], forward_url)

    def test_continue(self):
        """ The Parameter continue was renamed into next """

        urls = ["/",
                "/forum/%s/" % self.forum2.slug,
                "/topic/%s/" % self.topic.slug]
        for url in urls:
            response = self.client.get(url)
            self.assertFalse('?continue=' in response.content.decode("utf-8"))

    def test_topiclist(self):
        self.setUp_pagination()
        response = self.client.get("/last24/")
        self.assertEqual(len(response.tmpl_context['topics']), TOPICS_PER_PAGE)
