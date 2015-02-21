# -*- coding: utf-8 -*-

import unittest
from pysk.db import Database
from pysk.db.model import Airplane, Flight, LaunchMethod, Pilot, User

# The following tests assume that a database startkladde-test exists with a
# user sk-test-user with password sk

class ModelTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db= Database( user="sk-test-user",
                          dbName="startkladde-test",
                          password="sk")

    @classmethod
    def tearDownClass(cls):
        cls.db.disconnect()

        
        
    def assertIsSameModel(self, cls):
        """Helper function to assert that model and table are identical
        
        Arguments:
            cls Model instance
        """
        table= self.db.getTables()[ cls.tableName() ]
        
        for x in table.iterColumns(cls):
            self.assertIsNone(x)



    def test_Models(self):
        self.assertIsSameModel( Airplane() )        
        self.assertIsSameModel( Flight() )        
        self.assertIsSameModel( LaunchMethod() )        
        self.assertIsSameModel( Pilot() )        
        self.assertIsSameModel( User() )        



def suite():
    """Get Test suite object
    """
    return unittest.TestLoader().loadTestsFromTestCase(ModelTestCase)



if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run( suite() )