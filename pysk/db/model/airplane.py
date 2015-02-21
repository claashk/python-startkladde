# -*- coding: utf-8 -*-
"""
Created on Fri Apr 18 13:02:20 2014

@author: claas
"""
        
class Airplane(object):
    """Airplane representation used in Startkladde database
    """
    
    def __init__(self, id= None,
                       registration= None,
                       club= None,
                       num_seats= None,
                       type= None,
                       category= None,
                       callsign= None,
                       comments= None):
        """Create a new airplane instance
        
        Arguments:
            id: unique ID used in Startkladde database
            registration: Airplane registration
            club: Club name to which airplane belongs as string
            num_seats: Number of seats
            type: Type (Manufacturer & Model) of the plane as string
            category: Category. Use one of the following:
                - 'airplane'
                - 'glider'
                - 'motorglider'
                - 'ultralight'
            callsign: Callsign (e.g. competition call sign for gliders)
            comments: any comment
        """
        self.id= id
        self.registration= registration
        self.club= club
        self.num_seats= num_seats
        self.type= type
        self.category= category
        self.callsign= callsign
        self.comments= comments
        
        
        
    def __str__(self):
        """Convert instance to string
        
        Return:
            <registration> as string        
        """
        return "{0}".format(self.registration)
        
        
        
    def __repr__(self):
        return ("Startkladde Python Interface::Airplane('{0}')"
               .format(self.__str__()))



    def __eq__(self, other):
        """Equal comparison
        
        Two airplanes are defined equal, if and only if their registration is
        equal.
        
        Arguments:
            other: Other instance to compare to
        
        Return:
            True if and only if self and other are equal
        """
        return self.registration == other.registration



    def __lt__(self, other):
        """Less comparison by registration string
        
        Arguments:
            other: Other instance to compare to
        
        Return:
            True if and only if self is less than other
        """
        return self.registration < other.registration


    def __hash__(self):
        """Hash for object.
        
        Return:
            self.registration.__hash__
        """
        return self.registration.__hash__()



    @staticmethod    
    def tableName():
        """Get name of MySQL table, where this data type is used
        
        Return:
            "planes"        
        """
        return "planes"
        
        
        