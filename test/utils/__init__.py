# -*- coding: utf-8 -*-

import unittest
import ascii

def suite():
    return unittest.TestSuite([ ascii.suite() ])


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run( suite() )
 