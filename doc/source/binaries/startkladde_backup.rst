Backups of the Startkladde MySQL Database
=========================================
Backups of the Startkladde MySQL database can be performed with the bash script
:program:`startkladde_backup.bsh`

Functionality
-------------
The script uses the program
`mysqldump <https://dev.mysql.com/doc/refman/5.1/en/mysqldump.html>`_
to create MySQL scripts of all tables and stores them in a file called
:file:`<date>_<db>_backup.tgz`, where

* <date> is the current date in format *YYYYmmdd_HHMMSS*
* <db> is the name of the MySQL database, which has been backuped


Synopsis
--------

.. program:: startkladde_backup.bsh

.. code-block:: bash

   startkladde_backup.bsh <dir>

The following command line options are accepted:

.. option:: dir

   <dir> is the directory, where the output archives containing the backup are
   stored. Defaults to the current working directory.
   
The following envirionment variables, which may be defined inside the script,
control the behaviour of the program:
   
.. option:: USER <username>

   username of MySQL user performing the backup. Defaults to *backup*
   
.. option:: PASS <password>
   
   Password for :option:`USER`. Defaults to *sk*.

.. option:: DBNAME <database>   
   
   Name of the database to backup. Defaults to *startkladde*

