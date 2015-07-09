Database Model
==============
The Startkladde MySQL database consists of several tables, which store
information about flights, people and airplanes. The package
:mod:`pysk.db.model` implements the database model in python. The package
features one class per table in the database.

Tables
------
Each table in the database is implemented in terms of a single class in
:mod:`pysk.db.model`. These table classes are intenden to store data of a single
record, i.e. of one row in the respective table. The associated members have the
same names as the respective columns in the represented table. Additionally
each table class contains a static method :meth:`tableName` which returns the
name of the modeled table. The following tables are supported:

.. toctree::
   :maxdepth: 0
   :titlesonly:

   airplane
   flight
   launch_method
   pilot
   user

.. automodule:: pysk.db.model
