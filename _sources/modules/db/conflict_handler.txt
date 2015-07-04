Conflict Handler
================
The conflict handler is used to solve conflicts occuring during the import of
csv files.

Interface
---------

.. autoclass:: pysk.db.ConflictHandler
   :members:
   
   
Constants
---------

Warning Flags
^^^^^^^^^^^^^

.. autodata:: pysk.db.conflict_handler.NONE

.. autodata:: pysk.db.conflict_handler.ALL

.. autodata:: pysk.db.conflict_handler.MISSING_DEPARTURE_TIME

.. autodata:: pysk.db.conflict_handler.MISSING_LANDING_TIME

.. autodata:: pysk.db.conflict_handler.MISSING_DEPARTURE_LOCATION

.. autodata:: pysk.db.conflict_handler.MISSING_LANDING_LOCATION

.. autodata:: pysk.db.conflict_handler.MISSING_LAUNCH_METHOD

.. autodata:: pysk.db.conflict_handler.MISSING_PILOT

.. autodata:: pysk.db.conflict_handler.MISSING_PLANE


Warning Messages
^^^^^^^^^^^^^^^^

.. autodata:: pysk.db.conflict_handler.WARNINGS


Possible Modes
^^^^^^^^^^^^^^
.. autodata:: pysk.db.conflict_handler.INTERACTIVE


.. autodata:: pysk.db.conflict_handler.IGNORE_ALL_CONFLICTS


.. autodata:: pysk.db.conflict_handler.REJECT_ON_CONFLICT
