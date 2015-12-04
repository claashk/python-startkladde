#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from unittest import TextTestRunner, defaultTestLoader
import os

def suite():
    currentDir= os.path.dirname(__file__)
    topDir= os.path.dirname(currentDir)
    return defaultTestLoader.discover( start_dir=currentDir,
                                       pattern="*.py",
                                       top_level_dir=topDir )

if __name__ == '__main__':
    TextTestRunner(verbosity=2).run( suite() )
