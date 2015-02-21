# -*- coding: utf-8 -*-

import unittest
from pysk.db import Database

# The following tests assume that a database startkladde-test exists with a
# user sk-test-user with password sk

class DatabaseTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db= Database( user="sk-test-user",
                          dbName="startkladde-test",
                          password="sk")

    @classmethod
    def tearDownClass(cls):
        cls.db.disconnect()


    def test_reconnect(self):
        self.db.disconnect()
        self.db.connect( user="sk-test-user",
                         dbName="startkladde-test",
                         password="sk")

#TODO: More tests required        

def suite():
    """Get Test suite object
    """
    return unittest.TestLoader().loadTestsFromTestCase(DatabaseTestCase)



if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run( suite() )