# -*- coding: utf-8 -*-

from model import Airplane, Flight, Pilot, LaunchMethod



class RecordError(Exception):
    """Exception raised by some methods in :class:`~.db.Record`
    
    Arguments:
        message(str): Message string containing error message
    """
    def __init__(self, message=None):

        # Call the base class constructor with the parameters it needs
        super(RecordError, self).__init__(message)


    def __str__(self):
        return "RecordError: " + self.message



class Record(object):
    """Record containing all information stored in database
    
    Arguments:
        flight (:class:`~.db.model.Flight`): Flight instance.
        plane (:class:`~.db.model.Airplane`): Plane instance.
        pilot (:class:`~.db.model.Pilot`): Pilot instance.
        copilot (:class:`~.db.model.Pilot`): Pilot instance.
        towplane (:class:`~.db.model.Airplane`): Airplane instance.
        towpilot (:class:`~.db.model.Pilot`): Pilot of towplane.
        launch_method (:class:`~.db.model.LaunchMethod`): LaunchMethod instance.
    """
    
    def __init__( self, flight=None,
                        plane=None,
                        pilot= None,
                        copilot=None,
                        towplane= None,
                        towpilot= None,
                        launch_method= None ):
        # None may be passed in some cases, so we protect agains this here
        if flight:
            self.flight= flight
        else:
            self.flight= Flight()

        if plane:
            self.plane= plane
        else:
            self.plane= Airplane()
            
        if pilot:
            self.pilot= pilot
        else:
            self.pilot= Pilot()
            
        if copilot:
            self.copilot= copilot
        else:
            self.copilot= Pilot()
            
        if towplane:
            self.towplane= towplane
        else:
            self.towplane= Airplane()
            
        if towpilot:
            self.towpilot= towpilot
        else:
            self.towpilot= Pilot()
            
        if launch_method:
            self.launch_method= launch_method
        else:
            self.launch_method= LaunchMethod()
        
        if not self.launch_method.type:
            if( self.towplane.registration
                 or ( self.towpilot.first_name and self.towpilot.last_name)
                 or self.launch_method.towplane_registration ):
                self.launch_method.type= "airtow"

        if self.launch_method.type == "airtow":
            if not self.launch_method.towplane_registration:
                self.launch_method.towplane_registration= self.towplane.registration
    

    def __str__(self):
        """Convert instance to string
        
        Return:
            String with core information        
        """
        retval= self.flight.departureTime()
        retval+= "-" + self.flight.landingTime(format="%H:%M")
        retval+= " " + str(self.plane)
        retval+= " " + self.pilot.last_name + "," + self.pilot.first_name
        
        if self.copilot.last_name and self.copilot.first_name:
            retval += " & " + self.copilot.last_name + "," \
                      + self.copilot.first_name
        
        if self.launch_method.log_string:
            retval += " ({0}, {1})".format(self.launch_method.log_string,
                                           self.launch_method.name)
            
        return retval
        
        
    def __repr__(self):
        return ("Startkladde Python Interface::Record('{0}')"
               .format(self.__str__()))
               
   
    def updateFlight(self):
        """Update flight information based on other attributes

        Raise:
           :class:`~.db.record.RecordError` if critical parameters are missing.
        
        Return:
            List with warning messages.
        """
        retval= []
        criticalParms= ["pilot", "plane"]
        otherParms= []

        if self.flight.mode.lower() != "inbound":
            criticalParms.append("launch_method")
        else:
            self.flight.launch_method_id= 0
        
        if self.launch_method.type == "airtow":
            otherParms.extend(["towplane", "towpilot"])
        else:
            self.flight.towplane_id= 0
            self.flight.towpilot_id= 0
 
        if self.copilot.first_name and self.copilot.last_name:
            otherParms.append("copilot")
        else:
            self.copilot_id= 0
        
        for param in criticalParms:
            self._setFlightParameter(param, critical=True)
            
        for param in otherParms:
            warn=self._setFlightParameter(param, critical=False)

            if warn:
                retval.append(warn)
        
        self.flight.update()        
        
        return retval
                

    def _setFlightParameter(self, param, critical=False):
        """Set a flight parameter
            
        Attempts to set self.flight.<param>_id from self.<param>.id
        
        If critical is True, and the parameter cannot be set, a
        RecordError will be raised.
    
        Arguments:
            param: String containing parameter name        
            critical: True for critical parameters, False otherwise
            
        Return:
            warning message
        """
        id= getattr(self, param).id
                
        if not id:            
            msg= "".join( ["Unknown ",
                           param.replace("_", " "),
                           ": '{0}'".format( getattr(self, param)) ])

            if critical:
                raise RecordError(msg)
            else:
                return msg
                    
        setattr(self.flight, param + '_id', id)
            
        return ""