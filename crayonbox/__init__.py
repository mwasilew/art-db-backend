# Copyright (C) 2015 Linaro Limited
#
# Author: Milosz Wasilewski <milosz.wasilewski@linaro.org>
#
# This file is part of Crayonbox.
#
# Testmanager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License version 3
# as published by the Free Software Foundation
#
# Testmanager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Testmanager.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import absolute_import

import os

from django.conf import settings
from .celery import app as celery_app


def setup():
    if not os.path.exists(settings.EXTERNAL_DIR['BASE']):
        os.mkdir(settings.EXTERNAL_DIR['BASE'])

setup()
