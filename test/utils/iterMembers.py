# -*- coding: utf-8 -*-

import unittest
from pysk.utils.iterMembers import iterMembers, copyMembers, equalMembers

class Object(object):
    pass



class IterMembersTestCase(unittest.TestCase):

    def setUp(self):
        self.o1= Object()
        self.o1.first= "first"
        self.o1.second= 2
        self.o1.third= 3.        
        
        self.o2= Object()
        self.o2.first= "third"
        self.o2.second= 3
        self.o2.third= None        



    def test_iterMembers(self):
        names, values= zip( *iterMembers(self.o1) )                
        self.assertItemsEqual(names, ["first", "second", "third"])
        self.assertItemsEqual(values, ["first", 2, 3.])
        names, values= zip( *iterMembers(self.o1, ignore=["second"]) )                
        self.assertItemsEqual(names, ["first", "third"])
        self.assertItemsEqual(values, ["first", 3.])



    def test_copyMembers(self):
        copyMembers(self.o1, self.o2)        
        names, values= zip( *iterMembers(self.o2) )                
        self.assertItemsEqual(names, ["first", "second", "third"])
        self.assertItemsEqual(values, ["first", 2, 3.])

        self.o3= Object()
        copyMembers(self.o1, self.o3, ignore=["second"])        
        names, values= zip( *iterMembers(self.o3) )                
        self.assertItemsEqual(names, ["first", "third"])
        self.assertItemsEqual(values, ["first", 3.])



    def test_equalMembers(self):
        self.assertTrue( equalMembers(self.o1, self.o1) )
        self.assertFalse( equalMembers(self.o1, self.o2) )
        self.o2.first= self.o1.first
        self.o2.second= self.o1.second
        self.assertTrue( equalMembers(self.o1, self.o2, ignore=["third"]) )
        self.assertFalse( equalMembers(self.o1, self.o2) )
        


def suite():
    """Get Test suite object
    """
    return unittest.TestLoader().loadTestsFromTestCase(IterMembersTestCase)



if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run( suite() )