Synchronisation of the Startkladde Database with a Webserver
============================================================
This page desribes the synchronisation of a publicly accessible webserver
running the Startkladde Webinterface with a master device running the Startkladde
executable program.

.. contents::
   :depth: 3
      
Overview
--------
This page describes the synchronisation of the main startkladde database with a
webserver for decentralised access to the flight database. It is assumed, that
a single master database exists on a device, which is used to log flights at
the airfield (the *master*). Additionally a web server (the *server*) with a
copy of the master database exists, which runs the Startkladde webinterface. The
goal is to export the master database to the server database.

Master Configuration
--------------------
The master is a linux system with the following accounts:

* *flight*: account used for running the Startkladde executable
* *admin*: account for database & backup administration (not the same as root)
  This account should be used to execute the backup and synchronisation scripts.
* *root*: account for system administration

The mysql database on the master has two accounts:

* *startkladde* is the functional account used by the startkladde program
* *backup* has some additional rights needed to perform backup operations
  on the database.
  
The *flight* Account 
^^^^^^^^^^^^^^^^^^^^  
The *flight* account is intended as general access acount which is used to run
startkladde. Since this account is basically open to the public, the rights
of this account should be restricted to a minimum. It should e.g. not have read
access to any scripts containing passwords in clear text or any sensitive ssh
key files.

The Account *admin*
^^^^^^^^^^^^^^^^^^^
The admin account is the owner of all scripts for sync and should have more
rights in terms of database administration. The *admin* account must be
configured to act as an ssh client with passwordless login.

Server Configuration
--------------------
The server has a dedicated account *sync* for the synchronisation.


Backup Process
--------------
The backup follows the following sequence:

#. *flight* executes the
   :doc:`startkladde_sync_master.bsh <startkladde_sync_master>` script on the
   master. Since the script belongs to *admin*, the right to execute this script
   as *admin* must be granted to flight using
   `visudo <http://www.sudo.ws/man/1.8.13/visudo.man.html>`_
#. The startkladde_backup script is run by admin to create a backup file, which
   is transferred to the server using scp. Scp performs password-less login on
   the server using RSA. For this to work a public / private key pair has to
   exist in /home/admin/.ssh. The public key id_rsa.pub must be made availabe to
   the server.
#. The server must be configured to allow password-less login via ssh. This
   requires to add the public key of the client to
   /home/sync/.ssh/authorized_keys on the server. The respective line in
   authorized_keys should have the form (without any newlines):
   command="<path to startkladde_sync_server.sh>",no-port-forwarding,
   no-X11-forwarding,no-agent-forwarding,no-pty,<pub-key> 
   This automatically executes the sync_server script and exits and thus permits
   minimal possibilities for attackers.  
#. The sync_server script copies the backup file using scp, performs a backup of
   the current database using startkladde_backup and then restores the database
   using startkladde_restore with the backup file copied from the client.
  
