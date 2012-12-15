#-*- coding: utf-8 -*-
"""
    inyoka.portal.tests.test_versions
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2007-2012 by the Inyoka Team, see AUTHORS for more details.
    :license: GNU GPL, see LICENSE for more details.
"""
from django.test import TestCase

from inyoka.portal.utils import UbuntuVersion


class TestVersions(TestCase):

    def setUp(self):
        self.versions = [
            UbuntuVersion('5.04', 'Hoary Hedgehog'),
            UbuntuVersion('10.10', 'Maverick Meerkat', active=True),
            UbuntuVersion('10.04', 'Lucid Lynx', lts=True, active=True),
            UbuntuVersion('6.06', 'Drapper Drake', lts=True),
            UbuntuVersion('12.04', 'Precise Pangolin', lts=True, dev=True),
            UbuntuVersion('6.10', 'Edgy Eft')]

        self.versions_sorted = list(sorted(self.versions))

    def test_order(self):
        order = ['5.04', '6.06', '6.10', '10.04', '10.10', '12.04']
        versions = map(lambda v: v.number, self.versions_sorted)
        self.assertEqual(order, versions)