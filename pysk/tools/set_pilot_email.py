# -*- coding: utf-8 -*-

import re, io
from tool_base import ToolBase


class SetPilotEmail(ToolBase):

    def __init__(self, parent):
        description=str( "Set email of pilots\n"
                         "Reads the email address of pilots from a html file"
                         "in RESI format and adds them to the database")
        
        super(SetPilotEmail, self).__init__( description=description,
                                             parent=parent )

        self.config= self.defaultConfiguration(self.config)
        self._initCmdLineArguments()        
        
        #internal variables
        self.emails= dict()



    def _exec(self):
        """Execute the tool
        """
    
        if not self.config.inputFiles:
            self.error("No input files specified.")
            self.displayHelp()
            return

        for path in self.config.inputFiles:
            try:
                self.log("\nParsing input file {0} ...\n".format(path))
                nImported= self.parseHtml(path)
            except Exception as ex:
                self.error("{0}\n".format(ex))
            
            self.log("Imported {0} Email addresses\n".format(nImported))

        self.parent.connectDatabase()
            
        self.log("Updating database ...\n")
        nUpdated=self.updateEmails()
        self.log("Updated {0} email addresses\n\n".format(nUpdated))
        
        self.parent.db.commit()


    
    def _initCmdLineArguments(self):
        """Initialise all command line arguments.
        """
        self.parser.add_argument("inputFiles", nargs='*')
                                  
        self.parser.add_argument("-c", "--club",
                                 help="Restrict records to pilots belonging"
                                      " to the given club")


    
    def parseHtml(self, path):
        """Parse Html file containing emails in same format as output by RESI
           and add emails to self.emails
        
        Parameters
        ----------
        path Input file

        Returns
        -------
        Number of extracted email addresses        
        """
        format=r".*<a href=\"http://app\.resi\.de/reg\.nsf.+\">(.*)</a>.*<a href=\"mailto:(.+)\">"

        pattern= re.compile(format)

        nExtracted= 0
        with io.open(path, mode="r", encoding="windows-1252") as file:
            for line in file:
                match=pattern.match(line)
                
                if not match:
                    continue
                
                name= match.group(1).replace("_", " ").strip().encode("utf8")
                email= match.group(2).encode("utf8")
                
                self.emails[name]= email
                nExtracted+= 1
        
        return nExtracted
        
        
        
    def updateEmails(self, remove=False):
        """Reset Emails of all pilots in database
        
        Returns
        -------
        Number of updated records           
        """
        filter= None
        if self.config.club:
            filter="club='{0}'".format(self.config.club)
            
        nUpdated= 0        
        for p in self.parent.db.iterPilots(filter=filter):
            email= self.emails.get( " ".join([ p.last_name.replace("'", ""), 
                                               p.first_name.replace("'", "")]))
                
            if not email:
                self.log("Found no email for '{0}'\n".format(p))
                    
                if not remove:                    
                    continue
                
            p.setCommentField("email", email)
            nUpdated+= 1

            self.parent.db.insertPilots([p], force=True)

        return nUpdated


        
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
        config.club= None

        return config        
