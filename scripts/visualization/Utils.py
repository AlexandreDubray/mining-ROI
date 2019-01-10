#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def get_html_dir():
    return os.path.join(SCRIPT_DIR, '..', '..', 'webapp')
