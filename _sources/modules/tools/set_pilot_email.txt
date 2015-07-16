Set Pilot Email Tool
====================
Implementation of the :program:`set-pilot-email` tool contained in
:program:`sk.py`.

Allows to import emails from the `RESI <http://resi.de>`_ database.

Extracting data from RESI
-------------------------
To create a html file in the proper format, login to `RESI <http://resi.de>`_
and open the `member list <http://app.resi.de/reg.nsf/MemberlistWeb>`_. Save the
page as html file and use it as input to :option:`sk.py set-pilot-email`.

Note that you must use the link above and not the member list link provided in
the RESI webinterface.

Interface
--------

.. autoclass:: pysk.tools.SetPilotEmail
   :members: