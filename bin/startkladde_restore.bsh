#!/bin/bash 

# Restore database from backup file
# Usage: restore_database.sh file
#   file is an archive file created by create_backup.sh

USER="backup"            # Name of the db user
PASS="sk"                # Password of user
DBNAME="startkladde"     # Name of database to restore

IGNORE="users club flight-time-by-registration"      # list of tables which are not restored

#Do not edit beyond this point

PROGRAM_NAME="$(basename $0 .sh)"

function plainMessage() {
  printf "$*" >&2
}


function message() {
  plainMessage "${PROGRAM_NAME}: $*"
}

function resume() {
  plainMessage "done\n"
}

#Clean up file or directory
# Usage CleanUp <name>, where <name> is either a file or a directory
function cleanUp() {

  if [[ -d "$1" ]]; then
    message "Cleaning up ${1} ... "
    rm -r -f "$1"
    resume
  else 
    if [[ -f "$1" ]]; then
      message "Cleaning up ${1} ... "
      rm -f "$1"
      resume
    fi
  fi
  
  return 0
}

# Abort program with exit code 1
function abort() {
  plainMessage "failed\n"
  cat ${logFile}
  cleanUp ${backupDir}
  cleanUp ${logFile}
  message "Program terminated abnormally\n\n"
  exit 1
}

#Test for command line argument
if [[ $# -gt 0 ]]; then
  
  archive=$1 #Set output directory
  
  if [[ $# -gt 1 ]]; then
    message "WARNING: All but first command line arguments ignored\n"
  fi
else
  message "No archive file specified\n"
  exit 0
fi

#Set key and backupDir
key=$(basename ${archive} ".tgz")
backupDir="/tmp/${key}"
logFile="/tmp/${key}.log"

#delete directory if it exists
cleanUp "${backupDir}"

#extract data to backupDir

message "Extracting archive '${archive}'..."
if tar -C $(dirname ${backupDir}) -x -f ${archive} >& "$logFile"; then
  resume
else
  abort
fi

#set options for mysqldump
options="-u ${USER} -p${PASS}"
options="${options} --fields-terminated-by=\t"
options="${options} --fields-enclosed-by=\""
options="${options} --silent"


message "Processing tables in '$backupDir'...\n"
for iFile in ${backupDir}/*.sql; do
  
  tableName=$(basename ${iFile} ".sql")
  
  if [[ ${IGNORE} =~ ${tableName} ]]; then
    continue
  fi 

  #re-create table
  plainMessage " -> Creating table '${tableName}'... "
 
  if mysql ${DBNAME} -u ${USER} -p${PASS} < ${iFile} >& "$logFile"; then
    resume
  else
    abort
  fi

  #re-create table
  plainMessage " -> Importing ${tableName}... "
 
  if mysqlimport ${options} ${DBNAME} ${backupDir}/${tableName}.txt >& "$logFile"; then
    resume
  else
    abort
  fi
  
done

cleanUp "$logFile"
cleanUp "$backupDir"

message "Program terminated successfully\n\n"
exit 0
