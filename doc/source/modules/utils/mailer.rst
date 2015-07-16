Mailer Class
============
Supports sending automated emails to a list of recipients. The message body
is formed according to a template, which allows to insert fields, which are
automatically replaced by individual text for each recipient.

Example
-------
A message may look like this:

.. code-block:: none

   Hi ${first_name}!

   You receive this reminder email, because your are registred at the URI 
   http://www.example.com with the following credentials:

     Username: ${username}
     Password: ${password()}

   Regards,
   The Webmaster
   
When invoking :meth:`~.utils.Mailer.__call__` with this string, then each
*recipient* object passed as argument shall provide the members ``first_name``,
``last_name`` and ``username``. Additionally a dictionary with key '*password*'
and an unary functor as value shall be passed as the *functors* argument. The
functor will be executed with each *recipient* as argument and the result will
replace the ``${password()}`` field.

Interface
---------
.. autoclass:: pysk.utils.Mailer
   :members:
   :member-order: groupwise
   
   
Message Element Interface
-------------------------
Internally, each message is composed of several
:class:`~.utils.mailer.MessageElement` instances, each of which represents
either a literal string or an attribute to be retrieved from each *recipient*
or an unary functor to be invoked with a *recpient* as argument.

.. autoclass:: pysk.utils.mailer.MessageElement
   :members:
   :member-order: groupwise
