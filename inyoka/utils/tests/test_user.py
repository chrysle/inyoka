#-*- coding: utf-8 -*-
"""
    inyoka.utils.tests.test_user
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2007-2012 by the Inyoka Team, see AUTHORS for more details.
    :license: GNU GPL, see LICENSE for more details.
"""
import unittest
from hashlib import sha1
from django.conf import settings
from inyoka.portal.user import User
from inyoka.utils.user import gen_activation_key


class TestUtilsUser(unittest.TestCase):
    def setUp(self):
        self.user = User.objects.register_user('testing', 'example@example.com',
                                               'pwd', False)

    def tearDown(self):
        self.user.delete()

    def test_gen_activation_key(self):
        # We need to fakly generate the hash here because we're using the
        # user.id and MySQL does not handle primary keys well during
        # unittests runs so that we get the wrong id here everytime.
        # This way we cannot use a pregenerated key :(
        hash = sha1(('%d%s%s%s' % (self.user.id, self.user.username,
                                   settings.SECRET_KEY, self.user.email)))
        hash = hash.digest()[:9].encode('base64') \
                   .strip('\n=').replace('/', '_').replace('+', '-')
        self.assertEqual(gen_activation_key(self.user), hash)
