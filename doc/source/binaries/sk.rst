Python Startkladde Command Line Tool
====================================

Python script for command line access to the Startkladde database. The script
is a wrapper for several tools. The following tools are currently supported:

.. toctree::
   :maxdepth: 1

   help <sk_help>
   import-flights <sk_import-flights>
   stats <sk_stats>



Synopsis
-------- 

.. program-output:: python bin/sk.py --help
   :cwd: ../../..

.. program:: sk.py

.. option:: tool

   Tool to invoke
         
  
Display statistics
------------------
.. program-output:: python bin/sk.py help stats
   :cwd: ../../..
   
Set Email Adress for Pilots
---------------------------
.. program-output:: python bin/sk.py help set-pilot-email
   :cwd: ../../..
