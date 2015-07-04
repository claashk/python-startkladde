Tools package
=============
The functionality of the different packages is made available from the command
line in terms of several executable tools. To avoid pollution of the global
namespace with numerous tools, all tools are summarised by the executable
interface :doc:`../../binaries/executables`.

Each tool available through sk.py is implemented as a separate module in the
package tools. To avoid duplication of code, all tools should derive from
:py:class:`pysk.tools.ToolBase`


.. toctree::
   :maxdepth: 2

   tool_base

.. automodule:: pysk.tools
