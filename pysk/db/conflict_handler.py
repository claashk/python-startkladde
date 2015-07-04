# -*- coding: utf-8 -*-

from sys import stderr
from operator import attrgetter

from pysk.utils import UserQuery

#Warning flags
NONE                       = 0x0000 #: No warnings
ALL                        = 0xffff #: All warnings are set
MISSING_DEPARTURE_TIME     = 0x0001 #: Record is lacking departure time
MISSING_LANDING_TIME       = 0x0002 #: Record is lacking landing time
MISSING_DEPARTURE_LOCATION = 0x0004 #: Record is lacking departure location
MISSING_LANDING_LOCATION   = 0x0008 #: Record is lacking landing location
MISSING_LAUNCH_METHOD      = 0x0010 #: Record is lacking launch method information
MISSING_PILOT              = 0x0020 #: Record is lacking pilot information
MISSING_PLANE              = 0x0040 #: Record is missing airplane information

WARNINGS={ MISSING_DEPARTURE_TIME    : "missing departure time",
           MISSING_LANDING_TIME      : "missing landing time",
           MISSING_DEPARTURE_LOCATION: "missing departure location",
           MISSING_LANDING_LOCATION  : "missing landing location",
           MISSING_LAUNCH_METHOD     : "missing launch method",
           MISSING_PILOT             : "missing pilot",
           MISSING_PLANE             : "missing plane"  }
"""Dictionary containing a warning string message for each warning flag"""

#Modes
INTERACTIVE         = 1 #: Prompts user on conflict for manual resolution
IGNORE_ALL_CONFLICTS= 2 #: Import all records regardless of eventual conflicts
REJECT_ON_CONFLICT  = 3 #: Do not import records with conflicts


class ConflictHandler(object):
    """Checks for conflicts in database and tries to resolve them
    """


    def __init__(self, db=None,
                       mode=INTERACTIVE,
                       verbose=1,
                       logFunctor=stderr.write):
        
        self.mode      = mode
        self._enabled  = ALL      
        self.verbose   = verbose
        self.logFunctor= logFunctor
        self.nInserted = 0 # number of inserted candidates
        self.nDeleted  = 0 # Number of erased flights
   
        self._db       = db
        self._candidate= None # Flight to add / to investigate
        self._conflicts= None
        self._warnings = NONE
        
        self._dialog= UserQuery(replies= {'a': "abort",
                                          'r': "replace conflicts",
                                          's': "skip/remove candidate",
                                          'i': "ignore conflict" },
                                defaultMessage="How do you want to proceed?\n")

        self._actions= {'a' : self.abort,
                        'r' : self.replaceConflicts,
                        's' : self.skipCandidate,
                        'i' : self.keepAll }
                

    def log(self, message):
        """Log function. Forwards messages to the callback log function.
        
        Arguments:
            message: Message to print to stream
        """
        self.logFunctor( message )


        
    def __call__(self, rec):
        """Invoke conflict handler

        Checks if the record is valid and if conflicts exist. Depending on the
        mode settings conflicts are resolved.
        
        Arguments:
            rec: Rec to investigate
        """
        self._candidate= rec
        self._warnings = NONE
        
        if not self.isValid(self._candidate.flight):
            
            if self.mode == INTERACTIVE or self.verbose > 1:  
                self.log("\nCandidate:\n  {0}\nhas warnings:\n -> {1}\n"
                         .format(rec, "\n -> ".join(self.warnings()) ))
                
            if self.mode == INTERACTIVE:
                self._actions[ self._dialog(selection=['a', 's', 'i']) ]()
            elif self.mode == REJECT_ON_CONFLICT:
                    self.skipCandidate()
            #else Mode is IGNORE_ALL_CONFLICTS -> continue
                       
        if not self._candidate:
            return
            
        self.handleConflicts(self._candidate.flight)

        #if there is still a candidate -> add it
        if self._candidate:
            self._db.insertFlights([self._candidate.flight], force=True)
            
         
        
    def isValid(self, flight):
        """Check flight for consistency
        
        Verifies that all requirements of a flight are met.
        
        Arguments:
            flight Flight to check
        """
        if not flight.departure_location:
            self.addWarning( MISSING_DEPARTURE_LOCATION )

        if not flight.landing_location:
            self.addWarning( MISSING_LANDING_LOCATION )

        if flight.mode != "inbound":
            if not flight.departure_time:
                self.addWarning( MISSING_DEPARTURE_TIME )
                                
        if flight.mode != "outbound":
            if not flight.landing_time:
                self.addWarning( MISSING_LANDING_TIME )

        #TODO check training flights for students
       
        return not self.hasWarnings()

    
    
    def handleConflicts(self, flight):
        """Identify potential conflicts for a given flight
        
        Arguments:
            flight: Flight to search conflicts for
        """
        self._conflicts= list( self._db.iterSimilarFlights( flight,
                                                            filter="id > '{0}'"
                                                            .format(flight.id)) )
        
        
        if not self._conflicts:
            #No conflicts found
            return
        
        #if flight to add is an exact duplicate of another flight -> skip it
        for other in self._conflicts:
            if self.isDuplicate(flight, other):
                self.skipCandidate()
                return
        
        if self.mode == INTERACTIVE:
            self.log("\nCandidate:\n  {0}\nhas conflicts:\n  {1}\n"
                     .format( self._candidate,
                              "\n  ".join(self.iterConflicts() )))            
            self._actions[ self._dialog(selection=['a', 'r', 's', 'i']) ]()
        elif self.mode == REJECT_ON_CONFLICT:
            self.skipCandidate()



    def addWarning(self, warning):
        """Set warning flag
        
        Sets the respective warning flag in self._flags
        
        Arguments:
            warning: Flag to set
        """
        self._warnings |= warning
        
        
        
    def enableWarning(self, warning):
        """Enable a given warning
        
        Arguments:
            warning: Warning
        """
        self._enabled |= warning
        
        
        
    def disableWarning(self, warning):
        """Disable a given warning
        
        Arguments:
            warning: Warning to disable        
        """
        self._enabled &= ~warning 


    def hasWarnings(self):
        """Check if current instance has enabled warnings
        
        Return:
            True if and only if this instance has at least one enabled warning
            flag            
        """
        return (self._warnings & self._enabled) > 0



    def warnings(self):
        """Get iterable over all warnings
        
        Yield:
            String for each active warning
        """
        active= self._enabled & self._warnings
        
        for warning, message in WARNINGS.iteritems():
            if warning & active:
                yield message


                
    def abort(self):
        """Raise runtime error
        """
        self._candidate= None
        raise RuntimeError("Program aborted by user.")
        
        
        
    def skipCandidate(self):
        """Skip or remove the candidate
        """
        if self._candidate and self._candidate.flight.id:
            self._db.deleteFlights([self._candidate.flight.id])
            self.nDeleted+= 1
            
        self._candidate=None
        return



    def keepAll(self):
        """Ignore conflicts and import/keep the candidate
        """
        return



    def replaceConflicts(self):
        """Replace all conflicting records by candidate
        """
        i0= 0
        if not self._candidate.flight.id:
            self.candidate.flight.id= self.conflicts[0].id
            self.nInserted+= 1
            i0= 1
        
        self._db.deleteFlights( map( attrgetter("id"), self._conflicts[i0:] ))
        self.nDeleted+= len(self._conflicts)         


         
    def iterConflicts(self):
        """Iterate conflicts as strings
        
        Yield:
            String representation of each conflict
        """
        return map(str, self._db.makeRecords( self._conflicts ))


    @staticmethod
    def isDuplicate(flight, other):
        """Check if a flight is an exact duplicate of another flight
        
        Arguments:
            flight: first flight
            other: second flight
            
        Return:
            True if and only if first flight is an exact duplicate of other
        """
        if(    flight.plane_id != other.plane_id
            or flight.pilot_id != other.pilot_id 
            or flight.copilot_id != other.copilot_id
            or flight.mode != other.mode
            or flight.type != other.type
            or flight.launch_method_id != other.launch_method_id ):
            return False
            
        if(     flight.mode != "inbound" and ( 
                   flight.departure_time != other.departure_time
                or flight.departure_location != other.departure_location )):
            return False

        if(     flight.mode != "outbound" and (
                    flight.landing_time != other.landing_time
                or  flight.landing_location != other.landing_location )):
            return False
          
        return True