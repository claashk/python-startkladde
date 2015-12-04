# -*- coding: utf-8 -*-

import csv, codecs, sys
from traceback import print_exc
from datetime import datetime

from pysk.db.model import Flight, Pilot, Airplane, LaunchMethod
from .record import Record


class CsvReader(object):
    """Csv Reader for Startkladde flights
    
    Arguments:
       logStream: Stream used for log messages
       verbose (int): Verbose mode setting.
       debug(bool): Enable debug mode.
    """
    
    #: Mandatory columns in input files
    mandatoryColumns={
        "date",
        "plane_registration",
        "pilot_first_name",
        "copilot_first_name",
        "copilot_last_name",
        "flight_type",
        "num_landings",
        "flight_mode",
        "departure_time",
        "landing_time",
        "launch_method",
        "departure_location",
        "landing_location",
        "comments",
        "accounting_notes"
    }

    #: Optional columns in input files
    optionalColumns={
        "towplane_registration",
        "towflight_mode",
        "towflight_landing_time",
        "towflight_landing_location",
        "towflight_pilot"
    }    
    
    
    #: Column map from csv to internal names
    columnMap={
        "datum"                       : "date",
        "kennzeichen"                 : "plane_registration",
        "pilot vorname"               : "pilot_first_name",
        "pilot nachname"              : "pilot_last_name",
        "begleiter vorname"           : "copilot_first_name",
        "begleiter nachname"          : "copilot_last_name",
        "flugtyp"                     : "flight_type",
        "anzahl landungen"            : "num_landings",
        "modus"                       : "flight_mode",
        "startzeit"                   : "departure_time",
        "landezeit"                   : "landing_time",
        "startart"                    : "launch_method",
        "kennzeichen schleppflugzeug" : "towplane_registration",
        "modus schleppflugzeug"       : "towflight_mode",
        "landung schleppflugzeug"     : "towflight_landing_time",
        "startort"                    : "departure_location",
        "zielort"                     : "landing_location",
        "zielort schleppflugzeug"     : "towflight_landing_location",
        "bemerkungen"                 : "comments",
        "abrechnungshinweis"          : "accounting_notes",
        "dbid"                        : "flight_id"
    }
  
    #: Map for flight types  
    flightTypeMap={
        "normalflug"        : "normal",
        "schulung (1)"      : "training_1",
        "schulung (2)"      : "training_2",
        "gastflug"          : "guest_external",
        "gastflug (e)"      : "guest_external",
        "gastflug (p)"      : "guest_private",
        "schlepp"           : "towflight" 
    }


    #: Map for flight types  
    flightModeMap={
        "lokal"   : "local",
        "kommt" : "inbound",
        "geht" : "outbound",
    }


    #: Map for tow flight comments  
    towflightKeys=[
        "schleppflug",
        "towflight"
    ]
    
    
    def __init__(self, logStream=sys.stderr, verbose=1, debug=False):
        """Create new reader instance        
        """
        
        self.timeformat= None
        self.verbose= verbose
        self.decoder=None
        self.encoder= codecs.getencoder("utf-8")
        self.logStream= logStream
        self._initColumns()
        self.debug=debug
        
        
    def log(self, message, verbose=0):
        """Print log message
        
        Arguments:
           message (str): Log message to print
           verbose (int): Verbose mode from which on the message is printed
        """
        if self.verbose < verbose:
            return
            
        self.logStream.write( message )

        
    def warn(self, message):
        """Print warning message
        
        Arguments:
           message (str): Warning to print (regardless of verbose mode setting)
        """
        self.log("WARNING: " + message )



    def error(self, message):
        """Print error message
        
        Arguments:
           message (str): Error message to print
        """
        self.log("ERROR: " + message)

    
    def __call__(self, path,
                       delimiter=";",
                       encoding="utf8",
                       dateformat="%Y-%m-%d",
                       timeformat="%H:%M",
                       mergeTowflights=True):
        """Read input file and return a list of flights
        
        Arguments:
           path (str): Path to input file
           delimiter (str): Field delimiter. Defaults to ';'
           encoding (str): Encoding of input file (e.g. 'utf8' or 'windows-1252').
              Defaults to 'utf8'
           dateformat (str): Date format used in csv (notation as in strptime).
              Defaults to '%Y-%m-%d'
           timeformat (str): Time format used in csv (notation as in strptime).
              Defaults to '%H:%M'
           mergeTowflights (bool): If towflights are listed in a separate line,
              merge respective flights with towflights. Defaults to True
        
        Return:
            List of :class:`.Record` instances with one record per line in input
            file
        """
        self.timeformat=dateformat + "T" + timeformat
        self.decoder= codecs.getdecoder(encoding)

        reader= csv.reader( open(path, mode='r'), delimiter=delimiter)
        
        retval= []
        
        self.log("Analysing header fields ...\n", verbose=2)
        self.analyseHeader( reader.next() )

        self.nErrors= 0
        for record in reader:
            try:
                if(len(record) > 0):
                    retval.append( self.importRecord(record) )
            except(Exception) as ex:
                self.nErrors+= 1
                self.error( "while processing line {0}: {1}\n"
                            .format( reader.line_num, str(ex) ))

                if self.debug:
                    print_exc()                



        if(self.nErrors > 0):
            self.warn("{0} errors occured!\n".format(self.nErrors) )
                                  
        if mergeTowflights:
            nTowflights= len(retval)
            self._mergeTowflights(retval)
            nTowflights-= len(retval)
            
            self.log("-> Merged {0} towflights\n".format(nTowflights))
        
        return retval


    def analyseHeader(self, header):
        """Analyse header string of csv file to identify needed columns
        
        Arguments:
            header: Header object passed by csv reader.
        """
        
        columns=dict()
        i=0
        for field in header:

            fieldname= self.encoder( self.decoder(field)[0] )[0].lower()

            try:
                key= CsvReader.columnMap[ fieldname ]
                columns[key]= i
            except KeyError:
                pass
            
            i+= 1
        
        for key,value in columns.iteritems():
            setattr(self, key, value)


    def importRecord(self, record):
        """Convert csv record to database Record
        
        Arguments:
            record: csv record as passed by python csv reader
        
        Return:
            :class:`pysk.db.Record` instance
        """
        self.currentRecord= record
        return Record( flight       = self.getFlight(),
                       plane        = self.getPlane(),
                       pilot        = self.getPilot(),
                       copilot      = self.getCopilot(),
                       towplane     = self.getTowplane(),
                       towpilot     = self.getTowpilot(),
                       launch_method= self.getLaunchMethod() )
            

    def getFlight(self):
        """Extract flight information from current record
        
        Return:
            :class:`pysk.db.model.Flight` instance
        """
        return Flight(
          id                        = self.get("flight_id"),
          type                      = self.getFlightType(),
          mode                      = self.getMode(),
          departure_location        = self.get("departure_location"),
          landing_location          = self.get("landing_location"),
          num_landings              = self.get("num_landings"),
          departure_time            = self.getDepartureTime(),
          landing_time              = self.getLandingTime(),
          towflight_mode            = self.getTowflightMode(),
          towflight_landing_location= self.get("towflight_landing_location"),
          towflight_landing_time    = self.getTowflightLandingTime(),
          comments                  = self.get("comments"),
          accounting_notes          = self.get("accounting_notes") )
        

    def get(self, field):
        """Get field from current record by name

        Raises a KeyError if mandatory field is not found
        
        Arguments:
           field (str): Name of field to return

        Return:
           value or None if no such field exists        
        """
        i= getattr(self, field, None)
        
        if(i is not None):
            return self.encoder( self.decoder( self.currentRecord[i] )[0] )[0]
                        
        if field in CsvReader.mandatoryColumns:
            raise KeyError("Mandatory field '{0}' not found".format(field))
        
        return None


    def getFlightType(self):
        """Get flight type
        
        Return:
            Flight type as defined in :attr:`.flightTypeMap`
        """
        key= self.get("flight_type").lower()
        if(key is not None and len(key) > 0):
            return CsvReader.flightTypeMap[key]
        
        return None


    def getMode(self):
        """Get flight mode of current record
        
        Return:
           Flight mode as defined in :attr:`.flightModeMap`
        """
        key= self.get("flight_mode").lower()
        if key:
            return CsvReader.flightModeMap[key]
        
        return None


    def getTowflightMode(self):
        """Get towflight mode of current record
        
        Return:
           Flight mode as defined in :attr:`.flightModeMap`
        """
        key= self.get("towflight_mode").lower()
        if key:
            return CsvReader.flightModeMap[key]
        
        return None


    def getPlane(self):
        """Extract plane information from current record
        
        Return:
            :class:`db.model.Airplane` instance
        """
        registration= self.get("plane_registration")
        
        if registration:
            return Airplane(registration= registration)

        return None


    def getTowplane(self):
        """Extract towplane information from current record
        
        Return:
            :class:`.db.model.Airplane` instance or *None* if no towplane
               registration exists
        """
        registration= self.get("towplane_registration")
        if registration:
            return Airplane(registration= registration)
        
        return None


    def getPilot(self):
        """Extract pilot from current record
        
        Return:
            :class:`db.model.Pilot` instance
        """
        firstName= self.get("pilot_first_name")
        lastName= self.get("pilot_last_name")
        
        if firstName or lastName:
            return Pilot(first_name= firstName, last_name=lastName)

        return None

        
    def getCopilot(self):
        """Extract copilot from current record
        
        Return:
            :class:`db.model.Pilot` instance or *None*
        """
        firstName= self.get("copilot_first_name")
        lastName= self.get("copilot_last_name")
        
        if firstName or lastName:
            return Pilot(first_name= firstName, last_name=lastName)

        return None

        
    def getTowpilot(self):
        """Extract towpilot from current record
        
        Return:
            :class:`db.model.Pilot` instance or *None*
        """
        firstName= self.get("towpilot_first_name")
        lastName= self.get("towpilot_last_name")
        
        if firstName or lastName:
            return Pilot(first_name= firstName, last_name=lastName)

        return None


    def getLaunchMethod(self):
        """Extract launch method from current record
        
        Return:
            :class:`db.model.LaunchMethod` instance or *None*
        """
        name= self.get("launch_method")
        
        if name:
            return LaunchMethod( name= name )

        return None


    def getDepartureTime(self):
        """Extract departure time from record
        
        Return:
            :class:`datetime.datetime` instance
        """
        return self._getTime( self.get("date"), self.get("departure_time") )


    def getLandingTime(self):
        """Extract landing time from current record
        
        Return:
            :class:`datetime.datetime` instance
        """
        return self._getTime( self.get("date"), self.get("landing_time") )


    def getTowflightLandingTime(self):
        """Extract towflight landing time from current record
        
        Return:
            :class:`datetime.datetime` instance
        """
        return self._getTime( self.get("date"),
                              self.get("towflight_landing_time") )
        

    def _isTowflight(self, flight):
        """Check if a flight is a towflight for another flight
        
        Arguments:
            flight (db.model.Flight): Flight to check
        
        Return:
            True if and only if flight is a towflight
        """
        if flight.type.lower() == "towflight":
            return True
        return False


    def _findRecordById(self, records, id):
        """Finds a record with a given flight id
        
        Arguments:
            records(iterable): Iterable containing records
            id(int): Flight id to find

        Return:
            Matching record or *None* if no such flight can be found        
        """
        if id == None:
            return None
        
        for rec in records:
            if rec.flight.id == id:
                return rec
        
        return None
            

    def _mergeTowflights(self, records):
        """Merge towflights with respective glider flights

        Upon successful completion, all pure towflight records in records will
        be merged with the respective flight records. The pure towflight
        reocords are removed
        
        Arguments:
            records: List of records        
        """
        nRec= len(records)
        
        i=0
        while i != nRec:
            src= records[i]
            
            i+= 1
            
            if not self._isTowflight( src.flight ):
                continue
            
            dest= self._findRecordById( records, src.flight.id )

            if dest is None:
                sys.stderr.write("ERROR: No matching flight for towflight {0}\n"
                                 .format(src.flight.id))
                continue
            
            if src.flight.departure_time != dest.flight.departure_time:
                sys.stderr.write("ERROR: Departure time mismatch for towflight"
                                 " {0}\n".format(src.flight.id) )
                continue
            
            if src.flight.departure_location != dest.flight.departure_location:
                sys.stderr.write("ERROR: Departure location mismatch for towflight"
                                 " {0}\n".format(src.flight.id) )
                continue
            
            #set towflight of destination flight
            dest.flight.towflight_mode     = src.flight.mode
            dest.towflight_landing_location= src.flight.landing_location
            dest.towflight_landing_time    = src.flight.landing_time
            dest.towplane                  = src.plane
            dest.towpilot                  = src.pilot
            
            #remove towflight
            i-= 1
            nRec-= 1
            records.pop(i)


    def _getTime(self, date, time):
        """Convert separate date and time strings to datetime object
            
        Arguments:
            date (str): Date string
            time (str): Time string
            
        Return:
            :class:`datetime.datetime` object
        """
        if(date is None or time is None or len(date) == 0 or len(time) == 0):
            return None
        
        return datetime.strptime( date + 'T' + time, self.timeformat )
        
        
    def _initColumns(self):
        """Initialise index of each column with None
        """
        for key in CsvReader.mandatoryColumns:
            setattr(self, key, None)
            
        for key in CsvReader.optionalColumns:
            setattr(self, key, None)
        
            
    def _checkMandadortyColumns(self):
        """Checks if all mandatory columns have been found.
        
        Raises KeyError if a missing column has been identified
        """
        for key in CsvReader.mandatoryColumns:
            if(getattr(self, key, None) is None):
                raise KeyError("Mandatory column {0} not found")


        