# -*- coding: utf-8 -*-

from .tool_base import ToolBase

class Help(ToolBase):
    """Help tool implementation
    
    Displays a help messag for a given tool
    
    Arguments:
        parent (object): Parent :class:`~.ToolBase` object
        description (str): Description of the Help tool.
        **kwargs: Key word arguments forwarded to *parent* 
    """
    
    def __init__(self, parent,
                       description="Describe the usage of this program or its "
                                   "subcommands",
                       **kwargs):
        
        super(Help, self).__init__( parent=parent,
                                    description=description,
                                    **kwargs )

        self.parser.add_argument("tool", nargs=1)
        
        
        
    def _exec(self):
        """Help tool implementation
        """
        self.parent.commands.get( self.config.tool[0],
                                 self.parent ).displayHelp()
