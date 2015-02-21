# -*- coding: utf-8 -*-
"""
Created on Fri Apr 18 13:02:20 2014

@author: claas
"""

class LaunchMethod():
    "Startkladde launchmethod representation"""
    
    def __init__(self, id=None,
                       name= None,
                       short_name= None,
                       log_string= None,
                       keyboard_shortcut= None,
                       type= None,
                       towplane_registration= None,
                       person_required=None,
                       comments= None):
        """Create new Launch Method
        
        Parameters are ordered in the same order as stored in SQL database
        Thus a tuple received from a query can be passed as argument to this
        constructor.        
        
        Arguments:
            id: Unique ID (for SQL Database)
            name: Name of launch method
            short_name: Short name
            log_string: String used in pilot log book ('W' or 'FS')
            keyboard_shortcut: Keyboard short cut
            type: Launch type. ('airtow', 'winch', 'self')
            towplane_registration: Registration for tow planes
            person_required: A person (pilot, operator) is required for this
                launch method. Use 1 for True, 0 for False                        
            comments: Any comment
        """
        self.id= id
        self.name= name
        self.short_name= short_name
        self.log_string= log_string
        self.keyboard_shortcut= keyboard_shortcut
        self.type= type
        self.towplane_registration= towplane_registration
        self.person_required= person_required
        self.comments= comments



    def __str__(self):
        """Convert instance to string
        
        Return:
            <name>        
        """
        return "{0}".format(self.name)
        
        
        
    def __repr__(self):
        return ("Startkladde Python Interface::LaunchMethod('{0}')"
               .format(self.__str__()))
               
               
               
    def __eq__(self, other):
        """Equal comparison
        
        Two launch methods are defined equal, if and only if their names are
        equal.
        
        Arguments:
            other: Other instance to compare to                
        
        Return:
            True if and only if self and other are equal
        """
        return self.name == other.name



    def __hash__(self):
        """Hash for object.
        
        Return:
            self.name.__hash__
        """
        return self.name.__hash__()



    @staticmethod
    def tableName():
        """Get name of MySQL table, where this data type is used
        
        Return:
            "launch_methods"        
        """
        return "launch_methods"
        