#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import unittest
from pysk.utils.ascii import toAscii

class AsciiTestCase(unittest.TestCase):

    def test_toAscii(self):
        self.assertEqual( toAscii("älter"), "aelter" )
        self.assertEqual( toAscii("Die Älteren"), "Die Aelteren" )      
        self.assertEqual( toAscii("über"), "ueber" )
        self.assertEqual( toAscii("Über"), "Ueber" )
        self.assertEqual( toAscii("örtlich"), "oertlich" )
        self.assertEqual( toAscii("Das Örtliche"), "Das Oertliche" )
        self.assertEqual( toAscii("O'Neal"), "ONeal" )



def suite():
    """Get Test suite object
    """
    return unittest.TestLoader().loadTestsFromTestCase(AsciiTestCase)



if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run( suite() )