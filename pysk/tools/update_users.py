# -*- coding: utf-8 -*-

from tool_base import ToolBase
from pysk.utils import Mailer

import io


class UpdateUsers(ToolBase):
    
    def __init__(self, parent):
        description=str("Creates a user account for each pilot in database"
        "One input file containing the message to be sent to each user shall"
        "be provided. To personalise the message, the fields ${first_name}, "
        "${last_name}, ${email}, ${username} and ${password} can be used.")
        
        super(UpdateUsers, self).__init__( description= description,
                                           parent=parent )

        self.config= self.defaultConfiguration(self.parent.config)
        self._initCmdLineArguments()        
        
        #internal variables
        self.mailer= None



    def _exec(self):
        """Execute the tool
        """
        self.parent.connectDatabase()
        self._initMailer()
        

        self.createUserAccounts()        
        


    def _initCmdLineArguments(self):
        """Initialise all command line arguments.
        """
        
        self.parser.add_argument("inputFiles", nargs=1)
                                  
        self.parser.add_argument("-c", "--club",
                                 help="Restrict records to pilots of the given"
                                      " club",
                                 default= self.config.club)

        self.parser.add_argument("-H", "--smtp-host",
                                 help="SMTP server address",
                                 default= self.config.smtp_host)

        self.parser.add_argument("-U", "--smtp-user",
                                 help="username for login to SMTP server",
                                 default= self.config.smtp_user)

        self.parser.add_argument("-P", "--smtp-password",
                                 help="password for login to SMTP server",
                                 default= self.config.smtp_password)
    
        self.parser.add_argument("-s", "--subject",
                                 help="subject used for Email messages",
                                 default= self.config.subject)

        self.parser.add_argument("-S", "--sender",
                                 help="Senders email address",
                                 default= self.config.sender)



    def _initMailer(self):
        """Initialise Mailer object and connect to SMTP server
        """
        if not self.config.smtp_host:
            raise RuntimeError("No SMTP server specified\n")

        if not self.config.smtp_user:
            raise RuntimeError("Username for SMTP server not specified\n")

        if not self.config.sender:
            self.warn("Sender email address not specified! Using username instead\n")
            self.config.sender= self.config.smtp_user

        self.mailer= Mailer( logStream= self.config.logStream,
                             verbose= self.config.verbose )

        self.log("Reading input message from {0}...\n"
                 .format(self.config.inputFiles[0]), verbose=1 )
                 
        with io.open(self.config.inputFiles[0]) as ifile:
            self.mailer.setMessage( "\n".join(ifile) )
        

        self.mailer.connect( self.config.smtp_host,
                             self.config.smtp_user,
                             self.config.smtp_password )
        


    def createUserAccounts(self):
        """Create user accounts and sent emails.
        """
        clubMessage="for all clubs"
        if self.config.club:
            clubMessage="for club '{0}'".format(self.config.club)
            
        self.log("Creating user accounts {0} ...\n".format(clubMessage),
                 verbose=1)
        
        for pilot, user, pwd in self.parent.db.createUsersFromPilots():
       
            self.log("Creating account for pilot {0} ...\n".format(pilot),
                      verbose=3)

            if self.config.club and self.config.club.lower() != pilot.club.lower():
                self.log("Skipped (account exists)\n", verbose=3)
                continue
            
            pilot.email= pilot.getCommentField("email")
            pilot.username= user.username
            
            if not pilot.email:
                self.warn("Could not create account for {0}: No email found\n"
                          .format(pilot) )
                continue
            
            pilot.password= pwd            
            self.log("Sending notification email to {0} ...\n"
                     .format(pilot.email),
                     verbose=3)
            self.mailer( recipients=[pilot],
                         subject= self.config.subject,
                         sender= self.config.sender )
            
            self.log("Adding user '{0}' to database ...\n"
                     .format(user.username),
                     verbose=3)

            self.parent.db.insertUsers([user])
            self.log("Successfully added user {0}\n".format(user.username),
                     verbose=2)        
        
        self.parent.db.commit()


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
        config.club         = None
        config.smtp_host    = "smtp.gmail.com"
        config.smtp_user    = None
        config.smtp_password= None
        config.subject      = "Your new Startkladde Account"
        config.sender       = None

        return config        
    
      


                    