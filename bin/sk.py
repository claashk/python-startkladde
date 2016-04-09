#!/usr/bin/env python2 
# -*- coding: utf-8 -*-

import argparse, sys
from getpass import getpass

from pysk.tools import ToolBase
from pysk.tools import Help, ImportFlights, UpdateUsers, SetPilotEmail, Stats, Export
from pysk.db import Database


class AdminTool(ToolBase):
    """Tool for startkladde database administration
    
    Summarises a set of subcommands similar to e.g. svn tool.
    """
    def __init__(self):
        self.config= self.defaultConfiguration()

        self.commands={ "help": Help(self),
                        "import-flights" : ImportFlights(self),
                        "export" : Export(self),
                        "create-users" : UpdateUsers(self),
                        "set-pilot-email" : SetPilotEmail(self),
                        "stats" : Stats(self) 
                      }

        description="Administrate the Statkladde Database"
        super(AdminTool, self).__init__(description=description)
        self._initCmdLineArguments()        
        self.db= Database()


    def _exec(self):
        """Execute a given tool.
        """        
        self.setUsername()
        
        if not self.config.command:
            self.displayHelp()
        
        #execute sub-command
        cmd= self.commands[self.config.command]
        cmd(self.config.cmdArgs)
        self.nErrors+= cmd.nErrors
        
               
    def _initCmdLineArguments(self):
        """Initialise all command line arguments.
        """
        self.parser.add_argument("command",
                                 choices= list(self.commands.keys()) )

        self.parser.add_argument( "-u", "--user",
                                  help="Specify database username and hostname"
                                       ". Format <user>[@<host>]",
                                  default= self.config.user)

        self.parser.add_argument( "-p", "--password",
                                  nargs='?',
                                  help="Specify password. If no argument is "
                                       "provided, user is prompted.",
                                  default= self.config.password )

        self.parser.add_argument( "-d", "--database",
                                  help="Specify name of startkladde database",
                                  default= self.config.database)

        self.parser.add_argument( "-v", "--verbose",
                                  help="verbose mode setting",
                                  type=int,
                                  default= self.config.verbose)

        self.parser.add_argument( "cmdArgs",
                                  help="Subcommand arguments",
                                  nargs= argparse.REMAINDER )


    def helpMessage(self):
        msg= super(AdminTool, self).helpMessage()
        msg+= "\nAllowed commands are:\n"

        for cmd, obj in self.commands.items():
            msg+= "  {0}: {1}\n".format(cmd, obj.parser.description)

        return msg


    def connectDatabase(self):
        """Connect to database
        """
        self.log( "\nConnecting to database '{0}' ...\n"
                  .format(self.config.database),
                  verbose=1 )
        
        pw= self.config.password
        if pw is None:
            pw= getpass( prompt= "Please enter the password for {0}@{1}:\n"
                                 .format( self.config.username,
                                          self.config.hostname ),
                         stream= self.config.logStream )
        
        self.db.connect( host= self.config.hostname,
                         user= self.config.username,
                         password= pw,
                         dbName= self.config.database )



    def setUsername(self):
        """Process username field
        """
        fields= self.config.user.split("@")
        
        nFields= len(fields)
        
        if nFields == 1:
            self.config.username= fields[0]
            return
        
        if nFields == 2:
            self.config.username= fields[0].strip()
            self.config.hostname= fields[1].strip()
            return
            
        raise IOError( "Illegal user name '{0}'. Format is <user>[@<host>]"
                       .format(self.config.username) )
      
      

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
        config.debug=True
        config.database= "startkladde"
        config.hostname= "localhost"
        config.username= "startkladde"
        config.user= "@".join([config.username, config.hostname])
        config.password= None

        return config        



if __name__ == "__main__":
    tool=AdminTool()
    
    sys.exit( tool.main() )
