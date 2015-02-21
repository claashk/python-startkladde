# -*- coding: utf-8 -*-


from tool_base import ToolBase
from datetime import datetime, timedelta

DATE_FORMAT="%Y-%m-%d"
TIME_FORMAT="%H:%M"


class Stats(ToolBase):
    
    def __init__(self, parent):

        super(Stats, self).__init__(description=
            "Calculate statistics for a given plane", parent=parent )

        self.config= self.defaultConfiguration(self.config)
        self._initCmdLineArguments()        

        self._plane= None
        
        self._currentPic = None
        self._currentFrom= None
        self._currentTo  = None
        self._currentDay = None
        self._seats      = None
        
        self._firstStart= None
        self._lastLanding= None        
        
        self._nLandings     = 0
        self._nLandingsToday= 0
        self._nLandingsTotal= 0
        
        self.flightTime     = timedelta()
        self.flightTimeToday= timedelta()
        self.flightTimeTotal= timedelta()

        self._mandatoryFields= ["departure_time",
                                "landing_time",
                                "departure_location",
                                "landing_location"]


    def _exec(self):
        """Execute tool.
        
        Method called by super class
        """
        if not self.config.registrations:
            self.error("The registration of at least one plane has to be "
                       "specified!")
            self.displayHelp()
            return
        
        self.parent.connectDatabase()
        
        #read records from input file

        for registration in self.config.registrations:
            self.printStats( registration )



    def printStats(self, registration):
        """Print stats for a plane
        
        Arguments:
            registration: Registration of plane for which to print stats
        
        Raise:
            KeyError if no plane with this registration exists in Database
        """
        
        for flight in self.flights(registration):

            # Make sure all required fields are present
            errors= self.hasErrors(flight)
            if errors:
                self.error("In flight\n  {0}\n -> {1}\n"
                    .format( self.parent.db.makeRecord(flight) ,
                             "\n -> ".join(errors) ) )
                       
            # If this is the first flight -> create new entry            
            if not self._currentPic:
                self.newDay(flight)
                self.newEntry(flight)
                self.printHeader()
                continue

            # If we may add to an existing record -> add
            if self.mayAdd(flight):
                self.addEntry(flight)
                continue
            
            # Print current entry
            self.printEntry()            
            
            #Check if sums shall be printed.
            if self._currentDay != self.date(flight):
                self.printDailySums()
                self.newDay(flight)
                self.printHeader()
                
            self.newEntry(flight)
       
        self.printEntry()
        self.printDailySums()
            


    def hasErrors(self, flight):
        """Make sure flight is valid
        
        Arguments:
            flight: Flight to validate
            
        Return:
            List containing errors
        """
        errors=[]

        for field in self._mandatoryFields:
            if not getattr(flight, field):
                errors.append("missing {0}".format(field))
                
        return errors



    def mayAdd(self, flight):
        """Check if flight may be added to current entry
        
        Return:
            True if and only if flight may be added to current entry        
        """
        if self._currentPic != flight.pic():
            return False
            
        if self._currentFrom != flight.departure_location:
            return False
            
        if self._currentTo != flight.landing_location:
            return False

        if self._currentDay != self.date( flight):
            return False
            
        return True
        
        
        
    def newEntry(self, flight):
        """Start new entry
        
        Arguments:
            flight: Flight for which to start a new entry
        """
        self._currentPic = flight.pic()
        self._currentFrom= flight.departure_location
        self._currentTo  = flight.landing_location
                                              
        self._seats= set()
        
        self._firstStart = flight.departure_time
        self._nLandings     = 0
        self.flightTime     = timedelta()
        
        self.addEntry(flight)



    def newDay(self, flight):
        """Start new day
        
        Arguments:
            flight: Flight for which to start a new entry
        """
        self._currentDay = self.date(flight)
                                              
        self._nLandingsToday     = 0
        self.flightTimeToday     = timedelta()
        


    def addEntry(self, flight):
        """Add flight to current entry
        
        Arguments:
            flight: Flight to add to current entry
        """
        if flight.copilot_id:
            self._seats.add("2")
        else:
            self._seats.add("1")

        self._lastLanding= flight.landing_time        

        self._nLandings     += 1
        self._nLandingsToday+= 1
        self._nLandingsTotal+= 1
        
        dt= flight.duration()        
        
        self.flightTime     += dt
        self.flightTimeToday+= dt 
        self.flightTimeTotal+= dt



    def printHeader(self):
        """Print current entry to stdout
        """
        self.log(80*"+" + "\n")
        self.log( u"Datum|Nachname,      |Anz|Startort       |Start|# Ldg\n"
                  u"     |Vorname        |Crw|Landeort       |Ldg  |Zeit\n")
      


    def printEntry(self):
        """Print current entry to stdout
        """
        pilot= self.parent.db.pilot(self._currentPic)

        if self._nLandings == self._nLandingsToday:
            #First entry of the day -> user header delimiter
            self.log(80*"+" + "\n")
        else:
            self.log(80*"-" + "\n")
       
        self.log( u"{0}.{1}|{3:15s}|{5:3s}|{6:15s}|{8}|{10:5d}\n"
                  u"{2} |{4:15s}|   |{7:15s}|{9}|{11}\n"
                  .format( self._currentDay[8:10],
                           self._currentDay[5:7],
                           self._currentDay[0:4],
                           pilot.last_name.decode("utf8") + ",",
                           pilot.first_name.decode("utf8"),
                           "/".join(self._seats),
                           self._currentFrom.decode("utf8"),
                           self._currentTo.decode("utf8"),
                           datetime.strftime(self._firstStart, TIME_FORMAT),
                           datetime.strftime(self._lastLanding, TIME_FORMAT),
                           self._nLandings,
                           self.flightTimeStr(self.flightTime)))



    def printDailySums(self):
        """Print daily sums
        """
        self.log(80*"=" + "\n")
        self.log( "{0}{1:5d}\n"
                  u"{0}{2}\n"
                  .format( 48 * " ",
                           self._nLandingsToday,
                           self.flightTimeStr(self.flightTimeToday)))

        self.log("\n\n")    
    
    
    
    def printTotals(self):
        self.log("Total: TODO")



    def flights(self, registration):
        """Filter flights in database to plane and time constraints
        
        Arguments:
            registration: Plan registration        
        
        Return:
            Iterable of flights
        """
        timeFilter= self.timeConstraints()

        if timeFilter:
            timeFilter=" AND ({0})".format(timeFilter)
        
        self._plane= self.parent.db.getPlaneByRegistration(registration)

        filter="(plane_id = '{0}'){1}".format(self._plane.id, timeFilter)
        

        return self.parent.db.iterFlights( filter=filter,
                                           order="departure_time")



    def _initCmdLineArguments(self):
        """Initialise all command line arguments.
        """
        self.parser.add_argument("registrations", nargs='*')

        self.parser.add_argument("-t", "--time",
                                 help="Single date or date range. Format is"
                                 "YYYY-MM-DD for a single date and " 
                                 "<begin>:<end> for a range.")


    def timeConstraints(self):
        """Convert user specified time constraints to MySQL search string
        
        Return:
            MySQL compatible search string specifying the time range to search
        """
        begin= None
        end  = None
        if self.config.time:
            tmp= self.config.time.split(":")
            if len(tmp) == 1:
                begin= datetime.strptime(tmp[0], DATE_FORMAT)
                end= begin + timedelta(days=1)
            elif(len(tmp) == 2):
                if tmp[0]:
                    begin= datetime.strptime(tmp[0], DATE_FORMAT)
                
                if tmp[1]:
                    end= datetime.strptime(tmp[1], DATE_FORMAT)
                    
            else:
                raise RuntimeError( "Invalid time string '{0}'"
                                    .format(self.config.time) )

        parts=[]
        
        if begin:
            parts.append( "(departure_time >= '{0}')"
                          .format( datetime.strftime(begin, DATE_FORMAT) ) )
        if end:
            parts.append( "(departure_time < '{0}')"
                          .format( datetime.strftime(end, DATE_FORMAT) ) )
                        
        return " AND ".join(parts)

                

    @staticmethod    
    def date(flight):
        """Get date of flight as string
        
        Arguments:
            flight: Flight
            
        Return:
            Departure date of flight as string
        """
        return datetime.strftime(flight.departure_time, DATE_FORMAT)        



    @staticmethod
    def flightTimeStr(dt):
        """Print flight time to string in format HH:SS
        """
        s=int( dt.total_seconds() )

        hrs= s // 3600
        minutes= (s - hrs * 3600) // 60

        return "{0:02d}:{1:02d}".format(hrs, minutes)        



    @staticmethod
    def defaultConfiguration(config=ToolBase.defaultConfiguration()):
        """Get Default Configuration Options
        
        Parameters
        ----------
        config Input configuration. Existing attributes will be overwritten.
        
        Returns
        -------
        Default configuration object
        """
        config.time= None

        return config        

                    