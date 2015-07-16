Create User Accounts Tool
=========================
Implementation of the :program:`update-users` tool contained in :program:`sk.py`.
Creates a user account for each member in the ``people`` table, if an email
adress is specified in the ``comments`` column.

Interface
---------

.. autoclass:: pysk.tools.UpdateUsers
   :members: