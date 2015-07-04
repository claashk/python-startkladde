# -*- coding: utf-8 -*-

class Table():
    """MySql table instance containing some meta information about a table

    Arguments:
        columns: Iterable of :class:`pysk.db.Column` instances storing
           information about a table column
    """    

    def __init__(self, columns=None):
        """Construct new table    
    
        """    
        self.columns= []
        
        if columns:
            for col in columns:
                self.appendColumn(col)

                
                
    def appendColumn(self, col):
        """Insert a column into the table
        
        Arguments:
            col (:class:`pysk.db.Column`): Column to insert
        """
        self.columns.append(col)
        

    def nColumns(self):
        """Get number of columns in this table
        
        Return:
            Number of columns in this table
        """
        return len(self.columns)


    def format(self):
        """Returns a tuple to be passed to INSERT INTO VALUES command.
        
        Return:
            format string
        """
        return "(" + ",".join( self.nColumns() * ["%s"] ) + ")"
        
        
    def getColumnByName(self, name):
        """Get column with a given name
        
        Arguments:
            name(string): Column name to search for
        
        Return:
            pysk.db.Column instance with the given name. Raises a KeyError if no
            such column exists
        """
        for col in self.columns:
            if col.name == name:
                return col
                
        raise KeyError("No such column: '{0}'".format(name))
        

    def iterColumns(self, cls):
        """Iterates over the columns of a given object
        
        The object must provide an attribute for each column in the current
        table.
        
        Return:
            Generator over the table columns filled with the values of cls
        """
        for col in self.columns:            
            yield getattr(cls, col.name)

        
    def iterColumnNames(self):
        """Iterate over column names
        
        Return:
            Generator over column names of this table
        """
        for col in self.columns:
            yield col.name
        
        
    def toTuple(self, cls):
        """Convert class into tuple based on attributes.
        
        Arguments:
            cls: Class containing an attribute with same name as each table
                column.
        
        Return:
            Tuple intended for insertion into table
        """
        return tuple( self.iterColumns(cls) )
            