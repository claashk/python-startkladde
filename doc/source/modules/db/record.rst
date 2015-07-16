Record Class
============
The :class:`.db.Record` class constitutes a full record in the database. In
contrast to :class:`.db.model.Flight`, it contains full information about pilots,
planes and launch methods instead of references to other database tables.
  

Interface
---------
.. autoclass:: pysk.db.Record
   :members:


Exceptions
----------
.. autoclass:: pysk.db.record.RecordError
   :members:
