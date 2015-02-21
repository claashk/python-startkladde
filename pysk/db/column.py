# -*- coding: utf-8 -*-


class Column(object):
    """Represenation of a single column in a MySQL Table
    """
    
    def __init__(self, name=None,
                       dataType=None,
                       allowsNull=False,
                       index=None,
                       defaultValue=None,
                       extra='' ):
        """Construt column
    
        Arguments:
            name: Column name
            dataType: Data type
            allowsNull: True if and only if NULL is a valid value
            index: Index type of this column. PRI (primary), UNI (unique) or
                MUL (multiple)
            defaultValue: The default value for the column
            extra: Extra information, such as 'auto_increment'
        """                       
        self.name= name
        self.dataType= dataType
        self.allowsNull= allowsNull
        self.index= index
        self.defaultValue= defaultValue
        self.extra= extra

        
        
    def isPrimaryIndex(self):
        """Check if column is the primary index
        
        Return:
            True if and only if the current column is the primary index
        """
        return self.index == 'PRI'


        
    def hasAutoIncrement(self):
        """Check if column is incremented automatically
        
        Return:
            True if and only if the current column is incremented automatically
        """
        return 'auto_increment' in self.extra
        
        
        
    def default(self):
        """Default value as escaped string required in MySQL statements

        Return:
            '<val>' or NULL        
        """
        if self.defaultValue is None:
            return "NULL"
        else:
            return "'{0}'".format(self.defaultValue)
