CSV Reader Class
================
The :class:`.CsvReader` enables import of CSV files containing flight
information into the Startkladde database.

Expected Format
---------------
The csv format expected as input to the :meth:`.CsvReader.__call__` is similar to the
format produced by the Startkladde webinterface for csv export. Field delimiter,
encoding and the date- and time format can be specified via respective arguments
passed to :meth:`.CsvReader.__call__`.

Mandatory Columns
^^^^^^^^^^^^^^^^^
The first line of the file must contain a header containing the columns. The
given column names are first translated to internal column names using the
dictionary :attr:`.CsvReader.columnMap` (allows to support several languages).
At least the aliases for the columns defined in the set
:attr:`CsvReader.mandatoryColumns` must be defined. Optionally the columns
defined in the set :attr:`CsvReader.optionalColumns` may be present.

Date and Time Format
^^^^^^^^^^^^^^^^^^^^
Fields requiring date and time information must be formatted according to the
format string passed to :meth:`.CsvReader.__call__`

Special Values
^^^^^^^^^^^^^^
The columns *flight type* and *mode* require special values. Accepted are
the strings defined in the dictionaries :attr:`.CsvReader.flightTypeMap` and
:attr:`.CsvReader.flightModeMap`.
  

Interface
---------
.. autoclass:: pysk.db.CsvReader
   :members:
   :member-order: groupwise