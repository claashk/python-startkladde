# -*- coding: utf-8 -*-
import re           
from pysk.utils.ascii import toAscii
           
class Pilot():
    """Pilot representation used in Startkladde Database

    Arguments:
        id (int): ID of this record in ``people`` table.        
        last_name (str): Pilot last name.
        first_name (str): Pilot first name.
        club (str): Name of Club.
        nickname (str): Pilot nickname.
        club_id (int): ID of club (**deprecated**).
        comments (str): Comments field.
        medical_validity: :class:``datetime`` object holding expiration date of
           medical
        check_medical_validity (int): Shall Startkladde warn if medical is
           expired ? Use ``1`` for *yes* and ``0`` for *no*.
    """
    
    def __init__(self, id= None,
                       last_name= None,
                       first_name= None,
                       club= None,
                       nickname= None,
                       club_id= None,
                       comments= None,
                       medical_validity=None,
                       check_medical_validity= None):
        """Create new Pilot instance
        """                 
        self.id= id
        self.last_name= last_name
        self.first_name= first_name
        self.club= club
        self.nickname= nickname
        self.club_id= club_id
        self.comments= comments
        self.medical_validity= medical_validity
        self.check_medical_validity= check_medical_validity


    def __str__(self):
        """Convert instance to string
        
        Return:
            '``last_name``, ``first_name``'        
        """
        return "{0}, {1}".format(self.last_name, self.first_name)
                
        
    def __repr__(self):
        return ("Startkladde Python Interface::Pilot('{0}')"
               .format(self.__str__()))


    def __eq__(self, other):
        """Equal comparison
        
        Two pilots are defined equal, if and only if their first and last names
        are equal.
        
        Arguments:
            other (:class:`~.model.Pilot`): Other instance to compare to
        
        Return:
            ``True`` if and only if ``self`` and *other* are equal.
        """
        return self.last_name == other.last_name and self.first_name == other.first_name


    def __lt__(self, other):
        """Less comparison by last name and first name
                
        Arguments:
            other (:class:`~.model.Pilot`): Other instance to compare to
        
        Return:
            ``True`` if and only if ``self`` is less than *other*.
        """
        return( (self.last_name, self.first_name)
              < (other.last_name, other.first_name) )
    
    
    def __hash__(self):
        """Hash for object.
        
        Return:
            ``(self.last_name, self.first_name).__hash__``
        """
        return (self.last_name, self.first_name).__hash__()
        
        
    def generateUsername(self):
        """Generate default user name of the form '``first_name``.\ ``last_name``'
        
        Return:
            Username as string (all lowercase without special characters)
        """
        retval= "{0}.{1}".format( self.first_name.split()[0].lower(),
                                  self.last_name.split()[-1].lower() )
                                  
        return toAscii(retval)
        

    def getCommentField(self, key):
        """Gets field from comment.
        
        Comment fields are strings of the format '``key`` = ``value``'
        
        Arguments:
            key (str): Name of key to retrieve
        
        Return:
            value associated with *key* or ``None`` if *key* does not exist.
        """
        if not self.comments:
            return None
            
        pattern= re.compile(key + r"\s*=\s*'(.+)'")
        
        match= pattern.search(self.comments)
        
        if not match:
            return None
            
        return match.group(1)

        
    def setCommentField(self, key, value):
        """Set comment field.
        
        Comment fields are strings of the format '``key`` = ``value``'
        
        Arguments:
            key (str): Name of key to set
            value (str): Value string. If ``None``, the key value pair is
               removed, if it exists.
        """
        if not key:
            raise KeyError()
            
        comment= ""
        if value:
            comment= "{0}='{1}'".format(key, value)        

        if not self.comments:
            self.comments= comment
            return
            
        pattern= re.compile(key + r"s*=\s*'.+'")
        
        match= pattern.search(self.comments)
                
        if match:
            #key exists -> replace
            self.comments= ( self.comments[0:match.start(0)].strip()
                             + comment
                             + self.comments[match.end(0):] ).strip()
        else:
            self.comments+= "; " + comment


    @staticmethod
    def tableName():
        """Get name of MySQL table, where this data type is used
        
        Return:
            '*people*'        
        """
        return "people"

        
    @staticmethod
    def getMail(pilot):
        """Retrieve email address from :class:`~.model.Pilot` object
        
        The email is stored as comment field with key *email*.
        
        Arguments:
            pilot (:class:`~.model.Pilot`): Object to extract mail from
        
        Return:
            String containing pilot's email
        """
        return pilot.getCommentField['email']
