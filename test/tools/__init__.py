#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from unittest import defaultTestLoader, TextTestRunner
import os

def suite():
    currentDir= os.path.dirname(__file__)
    topDir= os.path.dirname( os.path.join(currentDir, "..") )
    return defaultTestLoader.discover( start_dir=currentDir,
                                       pattern="*.py",
                                       top_level_dir=topDir )


if __name__ == '__main__':
    TextTestRunner(verbosity=2).run( suite() )
 