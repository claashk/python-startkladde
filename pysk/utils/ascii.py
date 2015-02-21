# -*- coding: utf-8 -*-

REPLACEMENTS={ "ä" : "ae",
               "Ä" : "Ae",
               "ö" : "oe",
               "Ö" : "Oe",
               "ü" : "ue",
               "Ü" : "Ue",
               "'" : ""    }
   


def toAscii(string):
    """Convert string to ASCII string
    
    Replaces all non-ASCII characters by suitable replacements
    
    Arguments:
        string: input string
        
    Return:
        string with all non-ASCII characters replaced
    """
    retval= string
       
    for letter, replacement in REPLACEMENTS.iteritems():
        retval= retval.replace(letter, replacement)
            
    return retval

