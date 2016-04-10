# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import sys
from os import path as osPath
import csv
import io

from .tool_base import ToolBase


DATE_FORMAT="%Y-%m-%d"
TIME_FORMAT="%H:%M"


class Export(ToolBase):
    """Export Database
  
    Arguments:
        parent (:class:`~pysk.tools.ToolBase`): Parent tool
    """
    
    def __init__(self, parent):

        super(Export, self).__init__(description=
            "Export database", parent=parent )

        self.config= self.defaultConfiguration(self.config)
        self._initCmdLineArguments()
        self.flightTypes= {
            "normal"         : "Normalflug",
            "training_1"     : "Schulung(1)",
            "training_2"     : "Schulung(2)",
            "guest_external" : "Gastflug(E)",       
            "guest_private"  : "Gastflug"       
        }


    def _exec(self):
        """Execute tool.
        
        Method called by super class
        """
        self.parent.connectDatabase()
        
        if not self.config.ofile or self.config.ofile == "-":
            self.log("Dumping database to stdout...")
            self.writeCsv(sys.stdout)
        else:
            self.log("Writing output to {0}...".format(self.config.ofile))
            if osPath.isfile(self.config.ofile) and not self.mayOverwrite(self.config.ofile):
                raise RuntimeError("Aborted by user")
            with io.open(self.config.ofile, mode="wb") as os:
                self.writeCsv(os)

        self.log("Completed.")            


    def writeCsv(self, os):
        """Write output to csv file
        
        Arguments:
            os (stream): Output stream        
        """        
        writer= csv.writer(os, dialect='excel')
        writer.writerow([
            "Datum",
            "Nummer",
            "Kennzeichen",
            "LFZ Typ",
            "LFZ Verein",
            "Pilot Nachame",
            "Pilot Vorname",
            "Pilot Verein",
            "Pilot VID (leer)",
            "Begleiter Nachname",
            "Begleiter Vorname",
            "Begleiter Verein",
            "Begleiter VID (leer)",
            "Flugtyp",
            "Anzahl Landungen",
            "Modus",
            "Startzeit",
            "Landezeit",
            "Flugdauer",
            "Startart",
            "Kennz. Schleppflugzeug (leer)",
            "Modus Schleppflugzeug (leer)",
            "Landung Schleppflugzeug (leer)",
            "Startort",
            "Zielort",
            "Zielort Schleppflugzeug",
            "Bemerkungen",
            "Abrechnungshinweis",
            "DBID"
        ])
        
        count= 1
        for rec in self.records():
            writer.writerow([
                self.date(rec.flight),
                count,
                rec.plane.registration,
                rec.plane.type,
                rec.plane.club,
                rec.pilot.last_name,
                rec.pilot.first_name,
                rec.pilot.club,
                None,
                rec.copilot.last_name,
                rec.copilot.first_name,
                rec.copilot.club,
                None,
                self.flightTypes[rec.flight.type],
                rec.flight.num_landings,
                rec.flight.mode,
                rec.flight.departureTime(TIME_FORMAT),
                rec.flight.landingTime(TIME_FORMAT),
                self.flightTimeStr(rec.flight.duration()),
                rec.launch_method.log_string,
                None,
                None,
                None,
                rec.flight.departure_location,
                rec.flight.landing_location,
                None, #Landing location towplane
                rec.flight.comments, #Bemerkungen
                rec.flight.accounting_notes,
                rec.flight.id
            ])
            count+= 1
            
            if rec.launch_method.type == 'airtow':
                #print towflight
                writer.writerow([
                    self.date(rec.flight),
                    count,
                    rec.towplane.registration,
                    rec.towplane.type,
                    rec.towplane.club,
                    rec.towpilot.last_name,
                    rec.towpilot.first_name,
                    rec.towpilot.club,
                    None, # pilot VID
                    None, #Copilot last name
                    None, # - first name
                    None, # club
                    None, # VID
                    "Schlepp", #Flugtyp
                    0, #Anz. Landungen
                    rec.flight.towflight_mode,
                    rec.flight.departureTime(TIME_FORMAT),
                    rec.flight.towLandingTime(TIME_FORMAT),
                    self.flightTimeStr(rec.flight.towFlightDuration()),
                    "ES",
                    None,
                    None,
                    None,
                    rec.flight.departure_location,
                    rec.flight.towflight_landing_location,
                    None, #towplance landing location
                    "Schleppflug für Flug Nr. {0}".format(rec.flight.id),
                    None,
                    rec.flight.id
                ])
                count+= 1

            
    def records(self):
        """Filter records in database
        
        Return:
            Iterable: Record instances matching time constraints
        """
        timeFilter= self.timeConstraints()
        db= self.parent.db
        return db.makeRecords(db.iterFlights(filter=timeFilter,
                                             order="departure_time"))


    def _initCmdLineArguments(self):
        """Initialise all command line arguments.
        """
        self.parser.add_argument("time", nargs='*')

        self.parser.add_argument("-o", "--ofile",
                                 help="Path to output file",
                                 default= self.config.ofile)

        self.parser.add_argument("-f", "--force",
                                 help="Overwrite existing files without warning",
                                 default= self.config.force,
                                 action="store_true")

    def timeConstraints(self):
        """Convert user specified time constraints to MySQL search string
        
        Return:
            str: MySQL compatible search string specifying the time range to search
        """
        begin= None
        end  = None
        retval= []
        for t in self.config.time:
            tmp= t.split(":")
            if len(tmp) == 1:
                begin= datetime.strptime(tmp[0], DATE_FORMAT)
                end= begin + timedelta(days=1)
            elif len(tmp) == 2:
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

            if parts:
                retval.append(u"".join(["(", " AND ".join(parts), ")"]))
        
        return u" OR ".join(retval)
                

    @staticmethod    
    def date(flight):
        """Get date of flight as string
        
        Arguments:
            flight (:class:`~.db.model.Flight`): Flight to check            
        
        Return:
            Departure date of flight as string
        """
        return datetime.strftime(flight.departure_time, DATE_FORMAT)        


    @staticmethod
    def flightTimeStr(dt):
        """Print flight time to string
        
        Arguments:
            dt (:class:`datetime`): datetime object containing time span
            
        Return:
            int: Time span as string in format ``HH``\:``MM``.
        """
        if dt is None:
            return ""
        s=int( dt.total_seconds() )
        hrs= s // 3600
        minutes= (s - hrs * 3600) // 60
        return "{0:02d}:{1:02d}".format(hrs, minutes)        


    @staticmethod
    def defaultConfiguration(config=ToolBase.defaultConfiguration()):
        """Get default configuration options
        
        Arguments:
            config (object): Input configuration. Existing attributes will be
               overwritten.
        
        Return:
            Default configuration object
        """
        config.time  = None
        config.ofile = "-"

        return config        

                    