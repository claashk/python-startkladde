startkladde_sync_master.bsh
===========================
A bash script which synchronises the master database with a database on a
webserver.

The script performs the following tasks:

#. Execute :doc:`startkladde_backup.bsh <startkladde_backup>` on the local
   machine (*master*) to create a backup file.  
#. Send the backup file to the remote host (*server*) via scp. 

The server is expected to be configured as described in the article
:doc:`webserver synchronisation <server_sync>` to process the incoming backup
file with a call to :doc:`startkladde_sync_server.bsh <startkladde_sync_server>`

Requirements
------------
   
Synopsis
--------
.. code-block:: bash

   startkladde_sync_master.bsh
   
The following envirionment variables, which may be defined inside the script,
control the behaviour of the program:
   
.. program:: startkladde_sync_master.bsh

.. option:: LOCAL_SCP <path>

   Path to scp command on local machine. Defaults to :file:`/usr/bin/scp`
   
.. option:: BACKUP_DIR <path>

   Directory in which to store backups on local machine. Defaults to
   :file:`/home/user/backup`.
   
.. option:: BACKUP <path>

   Path to the :doc:`startkladde_backup.bsh <startkladde_backup>` script on the
   local machine. Defaults to :file:`/home/user/bin/startkladde_backup.bsh`
   
.. option:: SERVER <user>@<server>
  
   Username on remote server and URI or IP of the server. Defaults to
   **user@server**
