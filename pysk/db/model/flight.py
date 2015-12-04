# -*- coding: utf-8 -*-

#: Default time format used for string IO
TIME_FORMAT= "%Y-%m-%d %H:%M"
BOOLEAN={False : 0, True : 1}

class Flight(object):
    """Representation of a flight in the startkladde database
    
    Implements a single record in the Startkladde ``flights`` table. Each member
    represents the value of the column with the same name and type.

    Arguments:
        id (int): ID of this record in table ``flights``.
        plane_id (int): ID of :class:`.Airplane` record in table ``planes``
           (ref. :doc:`airplane`)
        pilot_id (int): ID of :class:`Pilot` record for the *pilot in
           command* (or student for two seated training) in table ``people``
           (ref. :doc:`pilot`).
        copilot_id (int): ID of :class:`Pilot` record for the copilot (or
           instructor in two seated training)  in table ``people``
           (ref. :doc:`pilot`).
        type (str): Flight type. One of 
 
            - '*normal*' (normal flight)
            - '*training_1*' (one seated training)
            - '*training_2*' (two seated training)
            - '*guest_external*' (guest flight)
            - '*guest_private*' (private guest flight)
        mode (str): Flight mode. One of

            - '*local*'
            - '*inbound*'
            - '*outbound*' 
        departed (int): ``1`` if flight is departed, ``0`` otherwise.
        landed (int): ``1`` if flight is landed, ``0`` otherwise.
        towflight_landed (int): ``1`` if towflight landed, ``0`` otherwise.
        launch_method_id (int): ID of applicable :class:`.LaunchMethod` record
           in table ``launch_methods`` (ref. :doc:`launch_method`)
        departure location (str): Departure location
        landing_location (str): Landing location
        num_landings (int): Number of landings
        departure_time (:class:`datetime`): Departure time
        landing_time (:class:`datetime`): Landing time
        towplane_id (int): ID of :class:`.Airplane` record for towplane in table
           ``planes`` (ref. :doc:`airplane`).
        towflight_mode (int): Mode of towflight. Same values as in *mode*
        towflight_landing_location (str): Location of tow flight landing
        towflight_landing_time (:class:`datetime`): Landing time of tow plane
        towpilot_id: ID of :class:`Pilot` record for the towpilot in table
           ``people`` (ref. :doc:`pilot`).
        pilot_last_name (str): **Deprecated**. Should be ``None``.
        pilot_first_name (str): **Deprecated**. Should be ``None``.
        copilot_last_name (str): **Deprecated**. Should be ``None``.
        copilot_first_name (str): **Deprecated**. Should be ``None``.
        towpilot_last_name (str): **Deprecated**. Should be ``None``.
        towpilot_first_name (str): **Deprecated**. Should be ``None``.
        comments (str): Eventual comments
        accounting_notes (str): Eventual accounting notes
    """    

    def __init__(self, id= None,
                       plane_id= None,
                       pilot_id= None,
                       copilot_id= None,
                       type= None,
                       mode= None,
                       departed= None,
                       landed= None,
                       towflight_landed= None,
                       launch_method_id= None,
                       departure_location= None,
                       landing_location= None,
                       num_landings= None,
                       departure_time= None,
                       landing_time= None,
                       towplane_id= None,
                       towflight_mode= None,
                       towflight_landing_location= None,
                       towflight_landing_time= None,
                       towpilot_id= None,
                       pilot_last_name= None,
                       pilot_first_name= None,
                       copilot_last_name= None,
                       copilot_first_name= None,
                       towpilot_last_name= None,
                       towpilot_first_name= None,
                       comments= None,
                       accounting_notes= None):
        """Create new Flight instance        
        """
        self.id= id
        self.plane_id= plane_id
        self.pilot_id= pilot_id
        self.copilot_id= copilot_id
        self.type= type
        self.mode= mode
        self.departed= departed
        self.landed= landed
        self.towflight_landed= towflight_landed
        self.launch_method_id= launch_method_id
        self.departure_location= departure_location
        self.landing_location= landing_location
        self.num_landings= num_landings
        self.departure_time= departure_time
        self.landing_time= landing_time
        self.towplane_id= towplane_id
        self.towflight_mode= towflight_mode
        self.towflight_landing_location= towflight_landing_location
        self.towflight_landing_time= towflight_landing_time
        self.towpilot_id= towpilot_id
        self.pilot_last_name= pilot_last_name
        self.pilot_first_name= pilot_first_name
        self.copilot_last_name= copilot_last_name
        self.copilot_first_name= copilot_first_name
        self.towpilot_last_name= towpilot_last_name
        self.towpilot_first_name= towpilot_first_name
        self.comments= comments
        self.accounting_notes= accounting_notes


    def __str__(self):
        """Convert instance to string
        
        Return:
            '``departure_time`` ``departure_location``'        
        """
        return "{0} {1}".format( self.departureTime(),
                                 self.departure_location)
                
        
    def __repr__(self):
        return ("Startkladde Python Interface::Flight('{0}')"
               .format(self.__str__()))


    def __lt__(self, other):
        """Compare two flights by their respective departure times
        
        Arguments:
            other (:class:`.Flight`): Instance to compare self to
        
        Return:
            ``True`` if and only if ``self.departure_time`` <
            ``other.departure_time``
        """
        return self.departure_time < other.departure_time


    def pic(self):
        """Get pilot in command

        Return:
            ID of pilot in command
        """
        if self.type == "training_2":
            return self.copilot_id
        else:
            return self.pilot_id
        

    def duration(self):
        """Get flight time
        
        Return:
            Flight time as :class:`timedelta` object
        """
        return self.landing_time - self.departure_time

        
    def departureTime(self, format=None):
        """Get departure time as string.
        
        Arguments:
            format (str): Output format (in :func:`strftime` notation).
               Defaults to :data:`~pysk.db.model.flight.TIME_FORMAT`.
        
        Return:
            Departure time as string in given format for local and outbound
            flights. Departure location for inbound flights.
        """
        if not self.departure_time:
            return ""

        if not format:
            format= TIME_FORMAT
            
        return self.departure_time.strftime(format)


    def landingTime(self, format=None):
        """Get landing time as string.
        
        Arguments:
            format (str): Output format (in :func:`strftime` notation).
               Defaults to :data:`~pysk.db.model.flight.TIME_FORMAT`.
        
        Return:
            Landing time as string in given format for local and inbound
            flights. Landing location for outbound flights.
        """
        if not self.landing_time:
            return ""
        
        if not format:
            format= TIME_FORMAT
            
        return self.landing_time.strftime(format)


    def similar(self, other):
        """Check if two flights are conflicting.
        
        Two flights are similar, if and only if their flight times overlap and
        either pilot and/or plane and/or copilot are identical.        
        
        Arguments:
            other (:class:`.Flight`): flight to check current instance against
        
        Return:
            ``True`` if and only if self and other are similar
        """
        if None in ( self.landing_time,
                     self.departure_time,
                     self.plane_id,
                     self.pilot_id ):
            raise RuntimeError("{0} is incomplete".format(self))
        
        if None in ( other.landing_time,
                     other.departure_time,
                     other.plane_id,
                     other.pilot_id ):
            raise RuntimeError("{0} is incomplete".format(other))

        
        return (
                (   (self.landing_time >= other.departure_time )
                and (self.departure_time <= other.landing_time) )
            and (   (self.pilot_id == other.pilot)
                or  (self.plane_id == other.plane_id)
                or  (self.copilot and self.copilot_id == other.copilot.id) ))


    def update(self):
        """Update members ``departed``, ``landed`` and ``towflight_landed``
        
        Sets members ``self.departed``, ``self.landed`` and
        ``self.towflight_landed`` from the information provided through
        ``landing_time``, ``departure_time`` and ``towflight_landing_time``
        """
        self.departed= BOOLEAN[self.departure_time is not None]
        self.landed= BOOLEAN[self.landing_time is not None]
        self.towflight_landed= BOOLEAN[self.towflight_landing_time is not None]


    @staticmethod
    def tableName():
        """Get name of MySQL table, where this data type is used
        
        Return:
            *'flights*'        
        """
        return "flights"
