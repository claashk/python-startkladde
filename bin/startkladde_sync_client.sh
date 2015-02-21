#!/bin/bash

# Creates a backup of the startkladde database and sends it to the server

LOCAL_SCP="/usr/bin/scp"                         #Local scp command for file transfer
BACKUP_DIR="/home/user/backup"                   #Directory containing backups
BACKUP="/home/user/bin/startkladde_backup.sh"    #Backup command
SERVER="user@server"                             #user@host for ssh login

#Do not edit beyond this point

PROGRAM_NAME=$(basename $0 .sh)

#Write message to stderr preceeded by program name
function message() {
  printf "${PROGRAM_NAME}: $*" >& 2
}

#Abort program after error
function abort() {
  message "Program terminated abnormally!\n"
  exit 1
}

#Create backup of current database
if ! ${BACKUP} ${BACKUP_DIR}; then
  message "Backup failed\n"
  abort
fi

#Identify latest backup file
file="$(ls -t ${BACKUP_DIR}/*_backup.tgz | head -n1)"

if ! [ -f "$file" ]; then
  message "${BACKUP_DIR} contains no backup files\n"
  abort
fi

#copy file to server and initialise server_sync

if ! ${LOCAL_SCP} "${file}" "${SERVER}:/"; then
  abort
fi

message "Program terminated successfully\n\n"
exit 0

