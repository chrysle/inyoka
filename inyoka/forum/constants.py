# -*- coding: utf-8 -*-
"""
    inyoka.forum.constants
    ~~~~~~~~~~~~~~~~~~~~~~

    Various constants for the forum application.

    :copyright: (c) 2011-2023 by the Inyoka Team, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
from PIL import Image
from django.utils.translation import ugettext_lazy

from inyoka.portal.utils import get_ubuntu_versions

# initialize PIL to make Image.ID available
Image.init()
SUPPORTED_IMAGE_TYPES = ['image/%s' % m.lower() for m in Image.ID]


POSTS_PER_PAGE = 15
TOPICS_PER_PAGE = 30
CACHE_PAGES_COUNT = 5

UBUNTU_DISTROS = {
    'none': ugettext_lazy('No Ubuntu'),
    'edubuntu': ugettext_lazy('Edubuntu'),
    'kubuntu': ugettext_lazy('Kubuntu'),
    'server': ugettext_lazy('Server'),
    'ubuntu': ugettext_lazy('Ubuntu'),
    'xubuntu': ugettext_lazy('Xubuntu'),
    'lubuntu': ugettext_lazy('Lubuntu'),
    'gnome': ugettext_lazy('Ubuntu GNOME'),
    'touch': ugettext_lazy('Ubuntu Touch'),
    'mate': ugettext_lazy('Ubuntu MATE'),
    'budgie': ugettext_lazy('Ubuntu Budgie'),
}

UBUNTU_DISTROS_SELECT_EXCLUDE = (
    'gnome',
)


def get_simple_version_choices():
    return [(v.number, str(v)) for v in get_ubuntu_versions() if v.is_active()]


def get_version_choices():
    return [('', ugettext_lazy('Version'))] + get_simple_version_choices()


def get_distro_choices( exclude:bool=False ):
    if(exclude):
        UBUNTU_DISTROS_SELECT = UBUNTU_DISTROS.copy()

        for key in UBUNTU_DISTROS_SELECT_EXCLUDE:
            UBUNTU_DISTROS_SELECT.pop(key)

        return [('', ugettext_lazy('Distribution'))] + list(UBUNTU_DISTROS_SELECT.items())

    return [('', ugettext_lazy('Distribution'))] + list(UBUNTU_DISTROS.items())
