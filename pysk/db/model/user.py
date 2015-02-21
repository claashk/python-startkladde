# -*- coding: utf-8 -*-
"""
Created on Fri Apr 18 13:02:20 2014

@author: claas
"""

from hashlib import sha1
           
           
           
class User():
    """User representation used in Startkladde Database"""
    
    def __init__(self, id= None,
                       username= None,
                       password= None,
                       perm_club_admin= None,
                       perm_read_flight_db= None,
                       club= None,
                       person_id=None,
                       comments=None ):
        """Create new User instance
        
        Parameters
        ----------
        ID ID used in Startkladde database
        
        username User name

        password Password

        perm_club_admin Club admin rights. (use 1 for granted, 0 otherwise)

        perm_read_flight_db Allowed to read flight database (use 1 for yes)

        club Club

        person_id ID of related person in pilot database        
        
        comments any comments
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
        
        Returns
        -------
        <username>        
        """
        return "{0}".format(self.username)
        
        
        
    def __repr__(self):
        return ("Startkladde Python Interface::User('{0}')"
               .format(self.__str__()))



    def __eq__(self, other):
        """Equal comparison
        
        Two users are defined equal, if and only if their usernames are equal
        
        Parameters
        ----------
        other Other instance to compare to
                
        
        Returns
        -------
        True if and only if self and other are equal
        """
        return self.username == other.username



    def __hash__(self):
        """Hash for object.
        
        Returns
        -------
        username.hash
        """
        return self.username.__hash__()



    def setPassword(self, password):
        """Set new password for user
        
        Parameters
        ----------
        password  String containing new passoword (as clear text)
        """
        self.password= self.hashPassword(password)
        
        


    @staticmethod
    def hashPassword(password):
        """Hash Password similar to startkladde
        
        Returns
        -------
        Hashed version of password compatible with values stored in
        user.password
        """
        return "*" + sha1( sha1(password).digest() ).hexdigest().upper()



    @staticmethod
    def tableName():
        """Get name of MySQL table, where this data type is used
        
        Returns
        -------
        "users"        
        """
        return "users"
        