# -*- coding: utf-8 -*-
"""
Created on Fri Apr 18 13:02:20 2014

@author: claas
"""

from smtplib import SMTP, SMTPRecipientsRefused
from getpass import getpass

from email.mime.text import MIMEText
import re, sys



class MessageElement(object):
    """A message consists of strings and fields.
    
    The MessageElement represents both string and field elements

    Parameters
    ----------
    value The Message element value. Either a string, which will be returned
          verbatim, or an attribute, which will be extracted from an object
          during runtime.

    type Type of the message element. Allowed values are "attribute", "functor"
         and "string". Defaults to string.
    """

    ATTRIBUTE_TYPE= 0
    STRING_TYPE   = 1
    FUNCTOR_TYPE  = 2    
    
    TYPES={"attribute": ATTRIBUTE_TYPE,
           "functor" : FUNCTOR_TYPE,
           "string" : STRING_TYPE }    
    
    def __init__(self, value="", type="string"):
        
        self.type= MessageElement.TYPES[type]
        
        if self.type == self.FUNCTOR_TYPE:
            self.value= value
        else:
            self.value= unicode(value)


        
    def __call__(self, obj=None):
        """Method called when message is constructed.
        
        Parameters
        ----------
        obj Object from which to extract parameters. Defaults to None.
        
        Returns
        -------
        Message part as string
        """
        if self.type == self.ATTRIBUTE_TYPE:
            return unicode( getattr(obj, self.value) )
        elif self.type == self.FUNCTOR_TYPE:
            return self.value( obj )
        else:
            return self.value




class Mailer(object):
    """Write automated emails to a set of addresses
    
    Parameters
    ----------
    host IP or hostname or SMTP mail server. If None, no login is attempted.
         Defaults to None.
    
    user Username for login to server. If None, no login is attempted.
         Defaults to None.

    password Password for login to server. Defaults to None.

    logStream Stream used for messages. Defaults to stderr

    verbose Verbose mode setting. Defaults to 1.
    """    
    def __init__(self, host=None,
                       user=None,
                       password=None,
                       logStream=sys.stderr,
                       verbose=1 ):

        self.server= SMTP()
        self.fieldPattern= re.compile(r"\$\{(.+)\}")
        self.logStream= logStream
        self.verbose=verbose
        
        if host and user:
            self.connect(host, user, password)



    def log(self, msg, verbose=0):
        """Print log message
        
        Parameters
        ----------
        msg Message to print
        
        verbose Verbose mode. Message is not printed, if verbose is greater
                than self.verbose. Defaults to zero.
        """
        if verbose > self.verbose:
            return
        
        self.logStream.write(msg)
        

                
    def connect(self, hostname, username, password=None):
        """Connect to SMTP server
        
        Parameters
        ----------
        hostname Hostname
        
        username User name to login to server
        
        password Password used for login
        """
        self.log("Connecting to server {0}\n".format(hostname), verbose=1)
        self.server.connect(hostname)
        self.server.ehlo()
        if self.server.has_extn("starttls"):
            self.log("Using securte TLS\n", verbose=1)
            self.server.starttls()
            self.server.ehlo()
        else:
            self.log("Server does not support TLS\n")
        
        self.log("Logging in to server {0} as user {1}\n".format( hostname,
                                                                  username),
                 verbose=1)
        
        if password is None:
            password= getpass(prompt="Please enter the password for {0}@{1}:\n"
                                     .format( username, hostname ),
                              stream= self.logStream )

        self.server.login(username, password)
        
        
    
    def __call__(self, recipients,
                       message=None,
                       subject= "",
                       sender= None,
                       email= MessageElement("email", type="attribute") ) :
        """Send messages to a number of recipients.
        
        Parameters
        ----------
        recipients Iterable of recipient objects. Each object must contain
                   the fields specified in message as well as an attribute
                   for the email address
                   
        message    Message to send. If not specified, the message set via the
                   constructor or a call to setMessage is used.

        subject    Subject used for all messages. Defaults to ""
        
        sender     Sender email address. Defaults to None.

        email      Functor which returns the email from each recipient object.
                   Defaults to MessageElement("email", type="attribute")
                   
        Returns
        -------
        Dictionary containing Error messages
        """
        if message:
            self.setMessage(message)
        
        if not self.message:
            raise RuntimeError("No message specified")
        
        errors= dict()        
        
        for recipient in recipients:
            msg=MIMEText( _text=self.getMessage(recipient), _charset='utf-8' )
            
            dest= email( recipient )            
            
            msg["Subject"]= subject
            msg["From"]= sender
            msg["To"]= dest             
            
            try:
                errors.update( self.server.sendmail( sender,
                                                     [dest],
                                                     msg.as_string() ))
            except SMTPRecipientsRefused as ex:
                errors.update( ex.recipients )
                        
        return errors
        
        
        
    def setMessage(self, msg, functors=None):
        """Sets the message to send
        
        Parameters
        ----------
        msg  String containing message. Fields to be replaced from other
             objects shall be marked as ${attributeName}
             
        functors Dictionary with functors. If this is provided, a field of the
                 form ${name()} will be replaced by "functors[name]", which
                 should be a unary function accepting a recipient object as
                 parameter. Defaults to None.
                 

        Exceptions
        ----------
        Raises a KeyError if functor fields are found but no functors are
        passed
        """
        self.message=[]       

        match= self.fieldPattern.search(msg)        
        
        begin=0
        while(match):
            self.message.append( MessageElement( msg[begin:match.start()] ) )

            v= match.group(1)

            if v.endswith("()"):

                if not functors:
                    raise KeyError("Found functor field, but no functors!")
                
                t= "functor"
                v= functors[ v[:-2] ]
            else:
                t= "attribute"
            
            self.message.append( MessageElement( value= v, type= t ))
            begin= match.end()
            match= self.fieldPattern.search(msg, pos= begin)
        
        self.message.append( MessageElement(msg[begin:]) )



    def msgGenerator(self, obj):
        """Iterate over all message elements
        
        Parameters
        ----------
        obj Object from which to extract missing fields
        """
        for element in self.message:
            yield element(obj)
            
            
            
    def getMessage(self, obj):
        """Create message for a given object
        
        Parameters
        ----------
        obj Object from which to create fields. Must contain an attribute with
            same name for each field.
            
        Returns
        -------
        Message with fields replaced from data object
        """
        return "".join( self.msgGenerator(obj) )

