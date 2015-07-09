# -*- coding: utf-8 -*-
"""
Created on Fri Apr 18 13:02:20 2014

@author: claas
"""

from hashlib import sha1
           
           
           
class User(object):
    """Implementation of a user record for the Startkladde users table
    
    Stores one record of the database containing a registred user of the 
    Startkladde webinterface.
    
    Arguments:
        id (int): ID of this user record in table ``users``
        username (str): Login
        password (str): Password hash (see :meth:`~.model.User.hashPassword`)
        perm_club_admin (int): Club admin rights. (use ``1`` for *granted*,
           ``0`` for *not granted*)
        perm_read_flight_db (int): Allowed to read flight database (use ``1``
           for *yes*, ``0`` for *no*)
        club (str): Club name
        person_id (int): ID of related person record in ``people`` table
           (ref :doc:`pilot`)        
        comments (str): Comments
"""
    
    def __init__(self, id= None,
                       username= None,
                       password= None,
                       perm_club_admin= None,
                       perm_read_flight_db= None,
                       club= None,
                       person_id=None,
                       comments=None ):
        """Create new User instance
        """                 
        self.id= id
        self.username= username
        self.password= password
        self.perm_club_admin= perm_club_admin
        self.perm_read_flight_db= perm_read_flight_db
        self.club= club
        self.person_id= person_id
        self.comments= comments


    def __str__(self):
        """Convert instance to string
        
        Return:
            ``username``        
        """
        return "{0}".format(self.username)
        
        
    def __repr__(self):
        return ("Startkladde Python Interface::User('{0}')"
               .format(self.__str__()))


    def __eq__(self, other):
        """Equal comparison
        
        Two users are defined equal, if and only if their usernames are equal
        
        Arguments:
            other (:class:`~.model.User`): Instance to compare to
                
        Return:
            ``True`` if and only if ``self`` and *other* are equal
        """
        return self.username == other.username


    def __hash__(self):
        """Hash for object.
        
        Return:
            ``username.__hash__()``
        """
        return self.username.__hash__()


    def setPassword(self, password):
        """Set new password for user
        
        Resets the current :attr:`~.model.User.password` to *password*, after
        hashing the input string with :meth:`~.model.User.hashPassword`.
        
        Arguments:
            password (str): Clear text password 
        """
        self.password= self.hashPassword(password)    
        

    @staticmethod
    def hashPassword(password):
        """Hash Password similar to startkladde
        
        Return:
            Hashed version of password as required for storage in
            :attr:`~.model.User.password`
        """
        return "*" + sha1( sha1(password).digest() ).hexdigest().upper()


    @staticmethod
    def tableName():
        """Get name of MySQL table, where this data type is used
        
        Return:
            '*users*'        
        """
        return "users"
        