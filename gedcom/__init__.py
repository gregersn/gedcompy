# -*- coding: utf8 -*-
"""
Library for reading and writing GEDCOM files.

https://en.wikipedia.org/wiki/GEDCOM
"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division

import re
import numbers
import os.path
import six

from ._version import __version__

from .note import *
from .individual import *
from .event import *
from .gedcomfile import *
from .family import *
