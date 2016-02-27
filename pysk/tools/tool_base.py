# -*- coding: utf-8 -*-

import sys
import argparse
from traceback import print_exc
from codecs import getwriter

class ToolBase(object):
    """Base class for command line tools
    
    Arguments:
        parent: Parent, e.g. if tool is used as sub-tool of another tool.
           Defaults to None.
        description: Description forwarded to ArgumentParser.
        kwargs: Keyword arguments forwarded to constructor of ArgumentParser   
    """
    
    def __init__(self, parent= None,
                       description="A command line tool",
                       **kwargs ):

        self.nErrors= 0
        self.parent= parent
        
        self.config= self.defaultConfiguration()
        
        if self.parent:
            self.importConfiguration(parent.config)
        
        #Encoding is not set e.g. when piping. Maybe move this to Logger ?
        if self.config.outStream.encoding is None:
            self.config.outStream= getwriter("utf8")(self.config.outStream)

        if self.config.logStream.encoding is None:
            self.config.logStream= getwriter("utf8")(self.config.logStream)

        self.parser= argparse.ArgumentParser( add_help= False,
                                              description=description,
                                              **kwargs )
        
        self.parser.add_argument("-h", "--help",
                                 action= 'store_true')



    def __call__(self, args=None):
        """Process command line options and invoke self._exec
        
        Arguments:
            args: Command line arguments forwarded to argparse. Defaults to
               None. (i.e. sys.argv)
        """
        if self.config.parseCommandLine:
            self.parseCommandLineOptions(args)
            
        self._exec()


    def _exec(self):
        """Sample exec method, which should be overridden by derived class.
        """
        self.printHelp()


    def helpMessage(self):
        """Get help message as string
        
        Return:
            Help message as string
        """
        msg= self.parser.format_help()
        
        if self.parent:
            parentHelp= self.parent.helpMessage()
            
            pos= parentHelp.find("optional arguments:\n")
            
            msg+= parentHelp[pos:].replace("optional arguments",
                                           "\nglobal arguments")      
        return msg


    def displayHelp(self):
        """Print help to self.config.logStream
        """
        self.config.logStream.write( self.helpMessage() + "\n" )
                
                
    def parseCommandLineOptions(self, args=None):
        """Parse command line options
        
        Arguments:
            args: Arguments to parse. If None, defaults to command line
                arguments. Defaults to None.
        """
        config= self.parser.parse_args(args)

        if config.help is True:
            self.displayHelp()

        self.importConfiguration(config)


    def output(self, message):
        """Print log message to output stream
        
        Arguments:
            message (string): Message to print to stream
        """
        self.config.outStream.write( message )


    def log(self, message, verbose=0):
        """Print log message to output stream
        
        Arguments:
            message (string): Message to print to stream
            verbose (int): Verbose mode. Message is only printed, if
               self.verbose is greater or equal this value. Defaults to 0
               (print always)
        """
        if self.config.verbose < verbose:
            return
            
        self.config.logStream.write( message )


    def warn(self, message):
        """Print warning message to output stream
        
        Arguments:
            message (str): Message to print to stream
        """
        self.log("WARNING: {0}".format(message))


    def error(self, message):
        """Print error message to output stream
        
        Arguments:
            message (str): Message to print to stream
        """
        self.log("ERROR: {0}".format(message))
        self.nErrors+= 1
        

    def mayOverwrite(self, path=None, message=None, retries=None):
        """Check if a given file may be overwritten.
        
        Arguments:
            path (str): Path to file. Ignored if message is specified.
            message (str): Message displayed. Defaults to '<path> exists.
               Overwrite (yes/no) ?'
            retries (int): Number of retries allowed. An IOError is raised if
               the number is exceeded. A value of None, allows for infinite
               retries. Default is None.
        
        Return:
            True if and only if either self.config.force is True or the user
            approves.
        """
        if self.config.force:
            return True
            
        if not message:
            message= "'{0}' exists. Overwrite (yes/no)?".format(path)
            
        while retries is None or retries > 0:
            response = raw_input(message).strip().lower()
            
            if response in ('y', 'yes'):
                return True
            
            if response in ('n', 'no'):
                return False
        
            if retries is not None:
                retries-= 1

        raise IOError("Maximum number of retries reached.")



    def main(self):
        """Main wrapper
           
        Executes the tool as main routine. All exceptions are are caught and
        converted to error messages.
        
        The exit code is set to 0, if the program terminated successfully or to
        1 in case of errors.
        
        A stack trace is printed in addition to the error message, if
        config.debug is set to True.
        
        Return:
            exit code
        """
        state={0: "successfully", 1: "abnormally"}
        exitCode=1

        try:
            self.__call__()
            exitCode= 0
        
        except Exception as ex:
            self.error(str(ex) + "\n")
           
            if self.config.debug:
                print_exc()
        except SystemExit as ex:
            exitCode= ex.code
        except:
            self.error("Unknown error\n")

            if self.config.debug:
                print_exc()        
        
        if self.nErrors:
            self.log("\n{0} Errors occured!\n".format(self.nErrors))
        
        self.log("\nProgram terminated {0}!\n\n"
                 .format( state.get(exitCode, "abnormally") ), verbose=1)

        return exitCode            



    def importConfiguration(self, config):
        """Copy configuration options from another instance
        
        Adds each attribute found in config to the current configuration.
        Existing attributes will be overwritten.        
        
        Arguments:
            config: Configuration to copy
        """
        for attr in dir(config):
            if attr.startswith('__'):
                continue
            
            if callable( getattr(config, attr) ):
                continue
            
            setattr(self.config, attr, getattr(config, attr))



    @staticmethod
    def defaultConfiguration():
        """Get Default Configuration Options
        
        Return:
            Default configuration object with the following arguments
            
            - force= False
            - logStream= sys.stderr
            - outStream= sys.stdout
            - parseCommandLine= True
            - verbose= 1
            - debug= False
        """
        config= argparse.Namespace()
        config.force= False
        config.logStream= sys.stderr
        config.outStream= sys.stdout
        config.parseCommandLine= True
        config.verbose= 1
        config.debug= False

        return config        
