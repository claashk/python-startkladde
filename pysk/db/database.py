# -*- coding: utf-8 -*-"

import MySQLdb as mdb
from subprocess import check_output

from pysk.db.model import Airplane, Flight, LaunchMethod, Pilot, User
from .table import Table
from .column import Column 
from .record import Record


class Database(object):
    """Interface for MySQL database used by Startkladde

    If *password* is not ``None``, a new connection to the database will be
    attempted.        
        
    Arguments:
        host (str): Hostname. Defaults to '*localhost*'
        user (str): MySQL username. Defaults to '*startkladde*'.
        password (str): Password for user. Defaults to ``None``.
        dbName (str): Name of Database to open. Defaults to '*startkladde*'.        
    """
    def __init__(self, host='localhost',
                       user='startkladde',
                       password=None,
                       dbName='startkladde'):
        """Create new Database instance
        """
        self._sk= None
        self._cursor= None
        
        if(password):
            self.connect(host, user, password, dbName)        
    
    
    def connect(self, host='localhost',
                      user='startkladde',
                      password=None,
                      dbName='startkladde'):
        """Connect to MySQL server
        
        Arguments:
            host (str): Hostname. Defaults to '*localhost*'.
            user (str): MySQL username. Defaults to '*startkladde*'.
            password (str): Password for user. Defaults to ``None``.
            dbName (str): Name of Database to open. Defaults to '*startkladde*'.        
        """
        self._sk= mdb.connect(host, user, password, dbName)
        self._cursor= self._sk.cursor()

        
    def disconnect(self):
        """Disconnect from database"""
        self._sk.close()        
        
        
    def commit(self):
        """Commit all changes to the database
        """
        self._sk.commit()
        
        
    def listTables(self):
        """Get list of tables                
                    
        Return:
            List of tables
        """
        self._cursor.execute("SHOW TABLES")
        
        retval=[]
        for table in self._cursor.fetchall():
            retval.append( table[0] )
        
        return retval


    def getTables(self):
        """Get information about tables                
                    
        Return:
            Dictionary with table name as key and :class:`.db.Table` instance as
            value
        """
        tables= self.listTables()
        retval= dict()        
        
        for tableName in tables:
            self._cursor.execute("DESCRIBE `{0}`".format(tableName))

            table= retval.setdefault(tableName, Table())
            
            for item in self._cursor.fetchall():
                table.appendColumn( Column( name= item[0],
                                            dataType= item[1],
                                            allowsNull= item[2].upper() == "YES",
                                            index= item[3],
                                            defaultValue= item[4],
                                            extra= item[5].lower() ))
        
        return retval
                

    def iterate(self, cls, filter=None, order=None):
        """Iterate over the rows of a given table                
        
        Arguments:
            cls: Class specifying the table. Must provide a static method
               tableName, which returns the name of the selected table and a
               constructor which accepts the returned tuple.
            filter (str): Any filter string in the format passed to *SQL*
               ``WHERE`` command. If *None*, no filter is applied. Defaults to
               *None*.
            order (str): Optional order key. Passed verbatim to *SQL*
               ``ORDER BY`` statement. Defaults to *None*.
            
        Return:
            Generator yielding an instance of *cls* for each table row
        """
        whereStr=""
        orderStr=""
        
        if(filter is not None):
            whereStr=" WHERE {0}".format(filter)

        if order:
            orderStr=" ORDER BY {0}".format(order)            
        
        self._cursor.execute( "SELECT * FROM {0}{1}{2}"
                              .format( cls.tableName(),
                                       whereStr,
                                       orderStr ))
        
        for row in self._cursor:
            yield cls(*row)


    def iterPlanes(self, filter=None):
        """Iterate over all airplanes in database
            
        Arguments:
            filter (str): Any filter string accepted by *SQL*'s ``WHERE``
               command. If *None*, no filter is applied. Defaults to *None*.
                
        Return:
            Generator yielding an :class:`.db.model.Airplane` instance for each
            airplane in database matching the filter criteria.
        """
        return self.iterate(Airplane, filter)
        
        
    def iterPilots(self, filter=None):
        """Iterate over all pilots in database
            
        Arguments:
            filter (str): Any filter string accepted by *SQL*'s ``WHERE``
               command. If *None*, no filter is applied. Defaults to *None*.
                
        Return:
            Generator yielding an :class:`.db.model.Pilot` instance for each
            airplane in database matching the filter criteria.
        """
        return self.iterate(Pilot, filter)


    def iterUsers(self, filter=None):
        """Iterate over all users in database
            
        Arguments:
            filter (str): Any filter string accepted by *SQL*'s ``WHERE``
               command. If *None*, no filter is applied. Defaults to *None*.
                
        Return:
            Generator yielding an :class:`.db.model.User` instance for each
            airplane in database matching the filter criteria.
        """
        return self.iterate(User, filter)


    def iterFlights(self, filter=None, order=None):
        """Iterate over all flights in database
            
        Arguments:
            filter (str): Any filter string accepted by *SQL*'s ``WHERE``
               command. If *None*, no filter is applied. Defaults to *None*.
            order (str): Parameter by which to order. Passed verbatim to *SQL*'s
               ``ORDER BY`` statement. Defaults to *None*.
                
        Return:
            Generator yielding an :class:`.db.model.Flight` instance for each
            airplane in database matching the filter criteria.
        """
        return self.iterate(Flight, filter, order)


    def iterSimultaneousFlights(self, flight):
        """Iterate over all flights, which overlap with the given flight

        Raises an exception if either landing or departure time are not
        specified in *flight*.
        
        Arguments:
            flight (:class:`.db.model.Flight`): Flight for which to get
               overlapping flights
        
        Return:
            Generator yielding a :class:`.db.model.Flight` instance for each
            flight in database overlapping with *flight*.
        """        
        return self.iterFlights(filter= "(landing_time >= '{0}') AND "
                                        "(departure_time <= '{1}')"
                                        .format( flight.departureTime(),
                                                 flight.landingTime() ))


    def iterSimilarFlights(self, flight, filter=None):
        """Get all flights from database, which are similar to a given flight

        A flight is *similar* to another flight, if it is conducted by the same
        pilot or with the same airplane in an overlapping time span.

        Raises an exception if either landing or departure time are not
        specified in flight.
        
        Arguments:
            flight (:class:`.db.model.Flight`): Flight for which to get
               overlapping flights
        
        Return:
            Generator yielding a :class:`.db.model.Flight` instance for each
            flight in database simlar to *flight*.
        """
        selection= str(
            "(mode='local') "
            "AND ( (landing_time >= '{0}') AND (departure_time <= '{1}') )"
            "AND ( (pilot_id = '{2}') OR (copilot_id = '{2}')"
               "OR (plane_id = '{3}') ").format(
            flight.departureTime(),
            flight.landingTime(),
            flight.pilot_id,
            flight.plane_id )

        if flight.copilot_id:
            selection+= "OR (pilot_id = '{0}') OR (copilot_id = '{0}')".format(
                        flight.copilot_id)
            
        selection+= ")" #Bracket behind AND
        
        if filter:
            selection += "AND ({0})".format(filter)
        
        return self.iterFlights(filter= selection)


    def getDictionary(self, iterable, key='id'):
        """Creates a dictionary of a given table                
        
        Arguments:
            iterable (iterable): Iterable containing table rows             
            key (str): The key used in the dictionary to return. Can be the name
               of any attribute provided by the iterable's elements. If a tuple
               of attribute strings is passed, the key will be the tuple of the
               associated attributes. Defaults to 'id'.

        Return:
            Dictionary containing a row in the specified table as value. The
            associated key is the respective member chosen through parameter
            *key*.
        """
        retval= dict()

        if type(key) == tuple:        
            for row in iterable:
                tmp= []
                for k in key: 
                    tmp.append( getattr(row, k) )                
                retval[tuple(tmp)]= row
        else:
            for row in iterable:
                retval[getattr(row, key)]= row
            
        return retval
        
        
    def insert(self, cls, rows, force=False):
        """Insert new values into a table                
        
        Arguments:
             cls (class): Class specifying the table. Must provide a static method
                :meth:`tableName`, which returns the name of the selected table
             rows (iterable): Rows to insert into the table. Each element shall
                provide an attribute for each table column with the same name as
                the column, i.e. :meth:`.db.Table.toTuple` (*row*) must be well
                defined for each element.
            force (bool): If True, existing rows are overwritten. Otherwise they
               are ignored. Defaults to False.
        """
        tableInfo= self.getTables()[ cls.tableName() ]
        commands={True : "REPLACE", False : "INSERT IGNORE"}
        command= "{0} INTO {1} VALUES {2}".format( commands[force],
                                                   cls.tableName(),
                                                   tableInfo.format() )
        
        for row in rows:        
            self._cursor.execute(command, tableInfo.toTuple(row))
         
    
    def insertUsers(self, users, force=False):
        """Insert users.
        
        Shortcut for
        
        .. code-block:: python
        
           self.insert(cls=User, table=users, force=force)
        
        Arguments:
            users (iterable): List of users to insert
            force (bool): Overwrite existing users. Defaults to False.
        """
        self.insert(User, users, force)
    
                
    def insertFlights(self, flights, force=False):
        """Insert flights.
        
        Shortcut for
        
        .. code-block:: python
        
           self.insert(cls=Flight, table=flights, force=force)
        
        Arguments:
            flights (iterable): List of flights to insert
            force (bool): Overwrite existing flights. Defaults to False.
        """
        self.insert(Flight, flights, force)


    def insertPilots(self, pilots, force=False):
        """Insert pilots.
        
        Shortcut for
        
        .. code-block:: python
        
           self.insert(cls=Pilot, table=flights, force=force)
        
        Arguments:
            pilots (iterable): List of pilots to insert
            force (bool): Overwrite existing pilots. Defaults to False.
        """
        self.insert(Pilot, pilots, force)


    def orderTable(self, cls):
        """Orders a given table
        
        .. warning:: "Deprecated. Raises RuntimeError"
        
        Reorders the ids in a given table by the natural sort order.
        
        Arguments:
            cls (class): Class containing table name
        """
        raise RuntimeError("Not good. Works only for flights")
        #TODO Depending id columns in other tables have to be updated!        
        
        values= sorted( self.getDictionary(cls).values() )

        id=0

        for v in values:
            id+= 1
            v.id= id
        
        self.insert(cls, values, force=True)


    def delete(self, cls, filter=None, data=None):
        """Delete records from table                
        
        Arguments:
            cls (class): Class representing the table from which to delete.
               Must provide a static method tableName, which returns the name of
               the selected table
            filter (str): Passed verbatim to *SQL*'s ``WHERE`` clause
               to identify the rows to be deleted. If filter is *None* or the
               empty string, all rows will be deleted. Defaults to *None*.
            data:  Data argument passed verbatim to
               `cursor.execute <http://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html>`_.
               as second argument (*param*). Defaults to *None*.
        """
        command= "DELETE FROM {0}".format( cls.tableName() )
        
        if filter:
            command+= " WHERE {0}".format(filter)
        
        self._cursor.execute(command, data)


    def deleteById(self, cls, ids):
        """Delete records by id
        
        Arguments:
            cls (class): Class specifying the table. Must provide a static
               method :meth:`tableName` returning the name of the selected table
            ids (iterable): ids to be deleted. Each element should be
               convertible to an integer.
        """
        if not ids:
            return
            
        filter= "id IN (" + ",".join( len(ids) * ['%s'] ) + ')'
                
        self.delete(cls, filter=filter, data=ids)        


    def deleteFlights(self, ids):
        """Delete flights by id
        
        Arguments:
            ids (iterable): IDs to delete
        """
        self.deleteById(Flight, ids)

        
    def deletePilots(self, ids):
        """Delete pilots by id
        
        Arguments:
            ids (iterable): IDs to delete
        """
        self.deleteById(Pilot, ids)


    def deleteUsers(self, ids):
        """Delete users by id
        
        Arguments:
            ids (iterable): IDs to delete
        """
        self.deleteById(User, ids)
        
        
    def createUsersFromPilots(self):
        """Generate a user account for each pilot in database
        
        Generates a user account with auto-generated password for each pilot,
        which does not have a standard account yet. The username is of the form
        ``<first_name>.<last_name>`` and the password will be autogenerated to
        a random initial value.
        
        The user account is not added to the database.
        
        Arguments:
            exclude (iterable): List of regular expression objects. Usernames
               matching any expression in this list are skipped. Defaults to
               *None*.
            club (str): Club for which to create user accounts. If *None*, no
               filter by club is applied. Otherwise, users accounts are
               exclusively generated for the specified club. Defaults to *None*.
        
        Return:
            Generator of tuples containing ``(pilot, user, password)``.
        """
        existingUsers= set()
        
        for user in self.iterUsers():
            existingUsers.add( user.username )

        passwords= []

        for pilot in self.iterPilots():

            username= pilot.generateUsername()
            
            if username in existingUsers:
                continue
            
            if not passwords:
                #generate new passwords
                passwords= check_output( ["/usr/bin/pwgen",
                                          "-1", # single column
                                          "-n", #include numbers
                                          "-c", # capitalize
                                          "8",  #8 characters
                                          "128" ] ).split()

            password= passwords.pop()
            
            yield  ( pilot,
                     User( username= username,
                           password= User.hashPassword(password),
                           perm_club_admin= 0,
                           perm_read_flight_db= 0,
                           club= pilot.club,
                           person_id= pilot.id,
                           comments=None ),
                     password )
                
                

    def update(self, cls, assignment, filter=None):
        """Update value in table
        
        Uses mysql ``UPDATE`` statement to update values of a table.
        
        Arguments:
            cls (class): Class for which to update the respective table
            assignment (str): Update information in format compatible with MySQL
               ``SET`` clause of ``UPDATE`` statement
            filter (str): Optional filter string passed verbatim to ``WHERE``
               statement.

        Example:
            Assuming *db* is a connected :class:`.db.Database` instance, the
            following code replaces each occurence of the ``pilot_id`` 3 with a
            ``pilot_id`` of 5 in table *Flights*:
        
            .. code-block:: python
            
               import pysk.db.model.Flight as Flight
               [...]
               db.update(Flight, "pilot_id=5", "pilot_id=3")
          
        """
        command="UPDATE {0} SET {1}".format(cls.tableName(), assignment)
        
        if filter:
            command= " ".join([command, "WHERE", filter])
        
        self._cursor.execute(command)
                

    def updateFlight(self, assignment, filter=None):
        """Update fields of selected flights
        
        Arguments:
            assignment (str): Update information in format compatible with MySQL
               ``SET`` clause of ``UPDATE`` statement.
            filter (str): Optional filter string passed verbatim to ``WHERE``
               statement.
        """
        self.update(assignment, filter)
        
        
    def unique(self, cls, filter):
        """Get unique result of a query
        
        Arguments:
            cls (class): Class to select
            filter (str): Filter criteria
        
        Return:
            Instance of *cls* matching query, if and only if the query returns
            exactly one result. Otherwise a :class:`KeyError` is raised.
        """        
        retval= None
        
        for result in self.iterate(cls, filter=filter):
            if not retval:
                retval= result
            else:
                raise KeyError("Found more than one result matching '{0}'"
                               .format(filter) )

        if not retval:
            raise KeyError("Found no result matching '{0}'".format(filter))
        
        return retval


    def uniqueById(self, cls, id):
        """Get unique result of a query
        
        Arguments:
            cls (class): Class to select
            id (int): ID of item to select
        
        Return:
            Instance of *cls* matching query, if and only if the query returns
            exactly one result. Otherwise a :class:`KeyError` is raised.
        """
        if not id:
            return None
            
        return self.unique(cls, filter="id={0}".format(id))


    def pilot(self, id):
        """Get Pilot by id
        
        Argument:
            id (int): ID of item to select
        
        Return:
            :class:`.db.model.Pilot` instance with ID *id*. Raises
            :class:`KeyError` if no matching item is found.
        """
        return self.uniqueById(Pilot, id)


    def plane(self, id):
        """Get Airplane by id
        
        Argument:
            id (int): ID of item to select
        
        Return:
            :class:`.db.model.Airplane` instance with ID *id*. Raises
            :class:`KeyError` if no matching item is found.
        """
        return self.uniqueById(Airplane, id)


    def launchMethod(self, id):
        """Get launch method by id
        
        Argument:
            id (int): ID of item to select
        
        Return:
            :class:`.db.model.LaunchMethod` instance with ID *id*. Raises
            :class:`KeyError` if no matching item is found.
        """
        return self.uniqueById(LaunchMethod, id)


    def getPilotByName(self, firstName, lastName):
        """Get pilot id by name
        
        Raises a :class:`KeyError` if either no pilots or more than one pilot
        with this name exist.        
        
        Arguments:
            firstName (str): First name of pilot
            lastName (str): Last name of pilot
        
        Return:
            Matching :class:`db.model.Pilot` instance
        """
        selection="first_name='{0}' AND last_name='{1}'".format( firstName,
                                                                 lastName )                 
        return self.unique(Pilot, selection)

            
    def getPlaneByRegistration(self, registration):
        """Get aircraft id by registration
        
        Raises a :class:`KeyError` if either no plane or more than one plane
        with this *registration* exist.        
        
        Arguments:
            registration (str): Registration ID of aircraft
        
        Return:
            Matching :class:`db.model.Airplane` instance
        """
        return self.unique(Airplane, filter="registration='{0}'".format(registration))        

        
    def getLaunchMethodByName(self, name, allowShortNames=True):
        """Get launch method id by name
        
        Raises a :class:`KeyError` if either no launch method or more than one
        launch method with the given *name* exist.        
        
        Arguments:
            name (str): Name of launch method to find
            allowShortNames (bool): If True, name and short name of launch
               method are searched. Otherwise only the long name is matched.
        
        Return:
            Matching :class:`db.model.LaunchMethod` instance
        """
        selection="name='{0}'".format(name)
        
        if allowShortNames:
            selection= "".join([ selection,
                                 " OR (short_name='{0}')".format(name) ])
        
        return self.unique(LaunchMethod, filter=selection)


    def getLaunchMethodByTowplane(self, registration):
        """Get launch method by registration of towplane
        
        Raises a :class:`KeyError` if either no launch method or more than one
        launch method with the given towplane *registration* exists.        
        
        Arguments:
            registration (str): Towplane registration ID
        
        Return:
            Matching :class:`db.model.LaunchMethod` instance
        """
        selection= "".join([ "(type='airtow') AND (towplane_registration = '",
                             registration,
                             "')" ])
                
        return self.unique(LaunchMethod, filter=selection)

    
    def makeRecords(self, flights):
        """Convert flights into full records
        
        Arguments:
            flights (iterable): Iterable of :class:`.db.model.Flight` objects
        
        Return:
            Generator yielding a :class:`.db.Record` instance per flight in
            *flights*.
        """
        for flight in flights:
            rec= Record(flight= flight,
                        plane= self.plane(flight.plane_id),
                        pilot= self.pilot(flight.pilot_id),
                        copilot= self.pilot(flight.copilot_id),
                        towpilot= self.pilot(flight.towpilot_id),
                        launch_method= self.launchMethod(flight.launch_method_id) )

            if rec.launch_method.type == 'airtow':
                #towplane_id is never set on flight
                #set towplane for record
                towplane= rec.launch_method.towplane_registration
                if towplane:
                    rec.towplane= self.getPlaneByRegistration(towplane)
                    rec.towplane_id= rec.towplane.id
            
            yield rec

    @staticmethod    
    def copy(src, dest, ignoreID=True):
        """Copies all attributes of *src* to *dest*
        
        Arguments:
            src (object): Source dataset
            dest (object): Destination dataset
            ignoreID (bool): If ``True``, member *id* is ignored. Defaults to
               ``True``.
        """
        for attr in dir(src):
            if attr.startswith('__'):
                continue

            if callable( getattr(src, attr) ):
                continue
            
            if ignoreID and attr == "id":
                continue
            
            setattr(dest, attr, getattr(src, attr))
        