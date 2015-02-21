# -*- coding: utf-8 -*-

def iterMembers(cls, ignore=None):
    """Iterate over all members of a class
    
    Arguments:
       cls: Class instance over which to iterate
       ignore: Iterable of members to ignore
        
    Yield:
        Tuple containing name and vlaue of each non executable class member
        in cls        
    """
    for name in dir(cls):
        if name.startswith('__') or (ignore and name in ignore):
            continue

        val= getattr(cls, name)

        if callable(val):
            continue
            
        yield name, val



def copyMembers(src, dest, ignore=None):
    """Copy all members of src to dest
    
    Arguments:
        src: Source object
        dest: Destination object
        ignore: Iterable of members to ignore during copy. Defaults to None.
        
    """
    for name,val in iterMembers(src, ignore):
        setattr(dest, name, val)



def equalMembers(cls1, cls2, ignore=None):
    """Check if two class instances have equal members
    
    Arguments:
        cls1: First object
        cls2: Second object
        ignore: Iterable of members to ignore in comparison. Defaults to None.
        
    Return
        True if and only if all not ignored members in cls1 and cls2 compare
        equal
    """
    for name,val in iterMembers(cls1, ignore):
        if val != getattr(cls2, name):
            return False
            
    return True
