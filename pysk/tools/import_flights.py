# -*- coding: utf-8 -*-

import io, os

from tool_base import ToolBase
from pysk.utils.iterMembers import copyMembers
from traceback import print_exc
from pysk.db.record import RecordError
from pysk.db import CsvReader
from pysk.db import ConflictHandler
from pysk.db.conflict_handler import INTERACTIVE, IGNORE_ALL_CONFLICTS, REJECT_ON_CONFLICT


class ImportFlights(ToolBase):
    """Import flights from csv file
    
    Arguments:
        parent (object): Parent tool object
    """
    def __init__(self, parent):

        super(ImportFlights, self).__init__(description=
            "Import flights into database from csv file(s)", parent=parent )

        self.config= self.defaultConfiguration(self.config)
        self._initCmdLineArguments()        

        #internal variables
        self.aliases= {"pilots": dict(),
                       "launch methods" : dict(),
                       "planes" : dict() }
                
        self._currentFile= None
        self._currentLine= 0
        

    def msg(self, message):
        """Print message to standard out
        
        Arguments:
            message (str): Message to print
        """
        self.log("In {0}:{1}: {2}".format( self._currentFile,
                                           self._currentLine,
                                           message) )


    def _exec(self):
        """Execute tool.
        
        Method called by super class
        """
        if not self.config.inputFiles:
            self.error("No input files specified.")
            self.displayHelp()
            return
        
        #read aliases, if any
        if self.config.alias_file:
            self.importAliases(self.config.alias_file)

        self.parent.connectDatabase()
        
        #read records from input file

        for path in self.config.inputFiles:
            self.createFlights( self.importCsv(path) )



    def _initCmdLineArguments(self):
        """Initialise all command line arguments.
        """
        self.parser.add_argument("inputFiles", nargs='*')

        self.parser.add_argument( "-a", "--alias-file",
                                  help="File containing aliases for planes, "
                                       "pilots and launch methods")
                                  
        self.parser.add_argument("-c", "--club",
                                 help="Restrict records to pilots/ planes, "
                                      "which belong to the given club")

        self.parser.add_argument( "-m", "--mode",
                                  help="Conflict handling. Specifies how to"
                                       "handle existing records",
                                  choices=['interactive', 'replace', 'ignore'],
                                  default=self.config.mode)
                                                                        
        self.parser.add_argument( "-s", "--separator",
                                  help="Field separator for csv records",
                                  default=self.config.separator)

        self.parser.add_argument("-D", "--date-format",
                                 help="Date format (in strftime notation)",
                                 default=self.config.date_format )

        self.parser.add_argument("-T", "--time-format",
                                 help="Time format (in strftime notation)",
                                 default=self.config.time_format)


            
    def importAliases(self, path):
        """Read alias names for planes, pilots or launch methods from file

        :TODO: Should be replaced by a general ini parser in utils        
        
        Aliases are stored in dictionary ``self.aliases[<string>]``.
        The expected format is ASCII with one header followed by a number of
        key value pairs in the form
        
        .. code-block:: none
        
           [<category>]
           <key>: <alias>
           <key>: <alias>
           ...
           
        ``<category>`` can be any field specified in ``self.aliases``. If
        ``<key>`` is a person's name, it should be provided in the form
        ``<last_name>, <first_name>``.
        
        Arguments:
            path (str): Path to text file containing aliases
        """
        dest= None        
        self.log("\nImporting alias file {0} ...\n".format(path))
        
        nFields= 0 # Number of fields per entry
        
        lineNumber= 0
        with io.open(path, encoding=self.config.encoding) as iFile:
            for line in iFile:
                lineNumber += 1
                
                line= line.encode("utf-8").strip()

                if not line:
                    continue
                
                if line[0] == "#":
                    continue
                
                if line[0] == '[' and line[-1] == ']':
                    category= line.rstrip(']').lstrip('[').strip().lower() 

                    try:
                        dest= self.aliases[category]
                    except KeyError:
                        dest= None
                    
                    if category == 'pilots':
                        nFields= 2
                    else:
                        nFields= 1
                    
                    continue

                if dest is None:
                    msg="In line {0}: ".format(lineNumber-1)
                    
                    if category:
                        msg+= "Unknown category '{0}'\n".format(category)
                    else:
                        msg+= "Missing category\n"
                    
                    msg+="Use [<cagegory>], where <cagetory> is one of\n"
                        
                    for cat in self.aliases.keys():
                        msg += " - " + cat + '\n'
                    
                    raise IOError(msg)
                                
                cols= line.split(":")
                
                if len(cols) != 2:
                    raise IOError("In line {0}: Found {1} columns, expected 2"
                               .format(lineNumber, len(cols)) )
                                
                key, value= cols[0].strip(), cols[1].strip()

                if nFields > 1:                
                    key= key.split(",")
                    value= value.split(",")

                    if len(key) != nFields:
                        raise IOError("In line {0}: Key contains {1} fields, "
                                      "expected {2}".format( lineNumber,
                                                             len(key),
                                                             nFields))

                    if len(value) != nFields:
                        raise IOError("In line {0}: Value contains {1} fields, "
                                      "expected {2}".format( lineNumber,
                                                             len(value),
                                                             nFields))
                    
                    key= (key[0].strip(), key[1].strip() )
                    value=(value[0].strip(), value[1].strip() )

                dest[key]= value

        for cat, vals in self.aliases.iteritems():
            if vals:
                self.log("-> Imported {0} {1}\n".format(len(vals), cat))


    def db(self):
        """Access to parent database
        
        Return:
            ``self.parent.db``
        """
        return self.parent.db


    def importCsv(self, path):
        """Import records from csv file
                
        Arguments:
            path (str): Path to input file
            
        Return:
            Iterable of imported records
        """
        csv= CsvReader( logStream= self.config.logStream,
                        verbose=self.config.verbose,
                        debug=self.config.debug)

        self.log("\nParsing input file '{0}' ...\n".format(path))
        self._currentFile= os.path.basename(path)            
            
        try:
            retval= csv( path,
                         delimiter=self.config.separator,
                         encoding=self.config.encoding,
                         dateformat=self.config.date_format,
                         timeformat=self.config.time_format,
                         mergeTowflights=True )
            
        except Exception as ex:
            self.error("{0}\n".format(ex))
                
            if self.config.debug:
                print_exc()                
                
        self.log("-> Imported {0} records\n".format( len(retval) ))
        
        return retval


    def createFlights(self, records):
        """Add flights to database
        
        Iterates over all records and extracts the flights which are going to
        be added to the database. If a flight to be added is simlar to an
        existing flight, one of the following actions will be taken depending
        on the mode setting:
        
        - If mode is 'ignore', the existing flights are kept and the new flight
          is ignored
        - If mode is 'interactive', the user is promted for an action for each
          collision. This is the default.
        - If mode is 'replace', existing flights are overwritten
         
        Arguments:
            records (iterable): Input records
        """
        missing= {"pilots": dict(),
                  "planes" : dict(),
                  "launch methods" : dict() }

        modeNumbers= {"ignore" : IGNORE_ALL_CONFLICTS,
                      "interactive" : INTERACTIVE, 
                      "replace" : REJECT_ON_CONFLICT }

        conflictHandler= ConflictHandler(db= self.parent.db,
                                         mode= modeNumbers[self.config.mode],
                                         verbose= self.config.verbose,
                                         logFunctor= self.msg)

        club= None
        if self.config.club:
            club= self.config.club.lower()

        for self._currentLine, rec in enumerate(records, 1):

            if not rec.flight:
                self.msg("No flight information. Record skipped\n\n")
                continue
                            
            #Look up pilots, plane and launch method in data base
            self._updatePlane(rec.plane, missing["planes"])
            self._updatePlane(rec.towplane, missing["planes"])
            self._updatePilot(rec.pilot, missing["pilots"])
            self._updatePilot(rec.copilot, missing["pilots"])
            self._updatePilot(rec.towpilot, missing["pilots"])
            self._updateLaunchMethod( rec.launch_method,
                                      missing["launch methods"] )

            # Skip record if club does not match       
            if( club
                and (not rec.pilot.club or club != rec.pilot.club.lower())
                and (not rec.copilot.club or club != rec.copilot.club.lower())
                and (not rec.plane.club or club != rec.plane.club.lower())):

                if self.config.verbose > 1:                
                    self.msg("Club mismatch. Record skipped\n\n")
                continue

            # Make sure record has necessary fields
            try:
                warnings=rec.updateFlight()
            except RecordError as ex:
                if self.config.verbose > 1:
                    self.msg("{0}. Record skipped\n\n".format(ex.message))
                continue
            
            if warnings and self.config.verbose > 1:
                self.msg( "".join([ "\n ->", "\n -> ".join(warnings), "\n"]))

            conflictHandler(rec)     
        
        self.log( "\nInserted {0} records\n".format(conflictHandler.nInserted) )        
        self.log( "Deleted {0} records\n".format(conflictHandler.nDeleted) )        

        for k,v in missing.iteritems():
            self._reportMissing(k, sorted( v.values() ) )

        self.db().commit()
                       
                        
    def _updatePilot(self, pilot, missing):
        """Try to complete pilot information with information in database
        
        Searches for pilot in database (by first and last name). If a match is
        found, pilot is reset to the respective database instance. If no match
        can be identified, pilot is moved to missing.
        
        Arguments:
            pilot (:class:`~.db.model.Pilot`):  Pilot instance to update from
               database
            missing (:class:`dict`): Dictionary of missing pilots
        """
        if not (pilot.last_name or pilot.first_name):
            return
            
        alias= self.aliases["pilots"].get((pilot.last_name, pilot.first_name))        
        
        if alias:
            pilot.first_name= alias[1]
            pilot.last_name= alias[0]

        try:
            copyMembers( self.db().getPilotByName( pilot.first_name,
                                                   pilot.last_name ),
                         pilot )
        except KeyError:
            missing[(pilot.last_name, pilot.first_name)]= pilot


    def _updatePlane(self, plane, missing):
        """Try to complete airplane information with information in database
        
        Searches for plane in database (by registration). If a match is
        found, plane is reset to the respective database instance. If no match
        can be identified, plane is moved to missing.
        
        Arguments:
            plane (:class:`~.db.model.Plane`): Plane instance to update from
               database
            missing (:class:`dict`): Dictionary of missing planes
        """
        if not plane.registration:
            return
        
        alias= self.aliases["planes"].get(plane.registration)        
        
        if alias:
            plane.registration= alias
            
        try:
            copyMembers( self.db().getPlaneByRegistration(plane.registration),
                         plane )
        except KeyError:
            missing[plane.registration]= plane


    def _updateLaunchMethod(self, method, missing):
        """Try to complete launch method information with information in
           database
        
        Searches for launchMethod in database (by name, short name or type). If
        a match is found, launchMethod is reset to the respective database
        instance. If no match can be identified, launchMethod is moved to
        missing.
        
        Arguments:
            method (:class:`~.db.model.LaunchMethod`): Launch method to update
               from database
            missing (:class:`dict`): Dictionary of missing launch methods
        """
        alias= self.aliases["launch methods"].get(method.name)        
        
        if alias:
            method.name= alias

        try:
            copyMembers( self.db().getLaunchMethodByName(method.name),
                         method )
            return 
        except KeyError:
            pass
        
        if method.type == "airtow":            

            try:
                copyMembers( self.db().getLaunchMethodByTowplane(method.towplane_registration),
                              method )
                return
            except KeyError:
                pass
            
            try:
                copyMembers( self.db().getLaunchMethodByName("Airtow (other)"),
                             method )
                return
            except KeyError:
                pass
            
        elif method.type == "self":
            
            try:
                copyMembers( self.db().getLaunchMethodByName("Self launch"),
                             method )
                return
            except KeyError:
                pass
        
        missing[method.name]= method


    def _reportMissing(self, string, items):
        """Reports missing items
            
        Arguments:
           string (str): String describing items
           iterms (iterable): Iterable containing missing items
        """
        if not items:
            return
        
        self.log("\n")
        self.warn("Found {0} missing {1}:\n".format( len(items), string) )
        
        for item in items:
            self.log(" -> {0}\n".format(str(item)) )


    @staticmethod
    def defaultConfiguration(config=ToolBase.defaultConfiguration()):
        """Get Default Configuration Options
        
        Arguments:
            config (object): Input configuration. Existing attributes will be
            overwritten.
        
        Return:
            Default configuration object
        """
        config.alias_file= None
        config.mode="interactive"
        config.club= None
        config.date_format="%Y-%m-%d"
        config.time_format="%H:%M"
        config.encoding="utf-8"
        config.separator=","

        return config        
                