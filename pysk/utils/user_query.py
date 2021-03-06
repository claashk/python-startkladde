# -*- coding: utf-8 -*-

from sys import stdout

class UserQuery(object):
    """Query user via stdout
        
    Arguments:
        replies(:class:`dict`): Dictionary of allowed replies, with reply
           letter as key and description as value.
        maxRetries(int): Number of allowed retries.
        defaultMessage(str): Message supplied to user.
    """
    
    def __init__(self, replies={'y' : 'yes', 'n' : 'no'},
                       maxRetries=10,
                       defaultMessage="Proceed ?"):
        """Constructor
        """
        self.replies= replies
        self.maxRetries= 10
        self.defaultMessage=defaultMessage
        
                
    def __call__(self, message=None, selection=None, retries=None):
        """Get response from user
        
        Prints *message* to :attr:`stdout` and returns the first valid user
        reply.
        
        Arguments:
            message (str): Message to forward to user. Defaults to standard
               message set in constructor
            selection (iterable): Subset of reply keys passed to constructor via
               replies
            retries (int): Maximum number of retries. Defaults to *maxRetries*
               set in constructor.
    
        Return:
            User response
            
        Raise:
            :class:`IOError` if maximum number of retries is exceeded.
        """
        options= "[{0}]".format( ", ".join( self.iterOptions(selection) ) )
        response=""

        if not selection:
            selection= self.replies.keys()
            
        if not message:
            message= self.defaultMessage

        if not retries:
            retries= self.maxRetries
               
        stdout.write(message + " ")            
            
        while retries > 0 and response not in selection:
            retries -= 1            
            stdout.write(options)
            response = raw_input().strip().lower()

        if not retries:
            raise IOError("Maximum number of retries reached.")
        
        return response
            
            
    def iterOptions(self, selection=None):
        """Iterate over possible options
        
        Arguments:
            selection (iterable): Subset of replies defined in
               :attr:`self.replies`. Defaults to all known replies.
        
        Yield:
           Option description with associated key
        """
        if not selection:
            for r ,m in self.replies.iteritems():
                yield "{0} ({1})".format(m, r)
        else:
            for r in selection:
                yield "{0} ({1})".format(self.replies[r], r)
                
