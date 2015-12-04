# -*- coding: utf-8 -*-

import unittest
from pysk.db import ConflictHandler
import pysk.db.conflict_handler as ch

# The following tests assume that a database startkladde-test exists with a
# user sk-test-user with password sk

class ConflictHandlerTestCase(unittest.TestCase):

    def setUp(self):
        self.handler= ConflictHandler()


    def warnString(self):
        return ",".join( self.handler.warnings() )


    def test_warnings(self):
        self.assertEqual( self.warnString(), "")
        
        self.handler.addWarning(ch.MISSING_LANDING_TIME)
        self.handler.addWarning(ch.MISSING_DEPARTURE_LOCATION)
        
        self.assertEqual( self.warnString(), "missing landing time"
                                             ",missing departure location")
                                             
        self.handler.disableWarning(ch.MISSING_DEPARTURE_LOCATION)
        self.assertEqual( self.warnString(), "missing landing time")
        self.handler.enableWarning(ch.MISSING_DEPARTURE_LOCATION)

        self.assertEqual( self.warnString(), "missing landing time"
                                             ",missing departure location")
        
        
        

#TODO: More tests required        

def suite():
    """Get Test suite object
    """
    return unittest.TestLoader().loadTestsFromTestCase(ConflictHandlerTestCase)



if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run( suite() )