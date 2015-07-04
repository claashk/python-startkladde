GitHub Related Information
==========================
`Python Startkladde <https://github.com/claashk/python-startkladde>`_ is hosted
on GitHub and the Sphinx generated html documentation is published on
`GitHub Project Pages <http://claashk.github.io/python-startkladde/index.html>`_.

The following sections describe how to set up the documentation and how to clone
and push to the repository.

Publishing Documentation with GitHub Project Pages
--------------------------------------------------
`GitHub <http://github.com>`_ allows to upload html documentation in a separate
branch called *gh-pages*. The html documentation is then available at
`http://claashk.github.io/python-startkladde`_.

Setting Up the Branch
^^^^^^^^^^^^^^^^^^^^^
Setting up the branch follows the
`GitHub documentation <https://help.github.com/articles/creating-project-pages-manually>`_.
To initalize the *gh-pages* branch with the automatically created documentation
created by `Sphinx <http://sphinx-doc.org>`_ in the :file:`doc/build/html`, it
is required to clone the entire repository into this directory:

.. code-block:: bash

   cd doc/build/
   git clone git@github.com:claashk/python-startkladde.git html
   cd html
   git checkout --orphan gh-pages
   git rm -rf .
   
This creates an orphan *gh-pages* branch without any content.

Disabling Jekyll
^^^^^^^^^^^^^^^^
Additionally the Jekyll Tool installed on GitHub has to be disabled, to avoid
that files and directories starting with an underscore are ignored. This can be
achieved by simply adding a file called :file:`./doc/build/html/.nojekyll` to
the base directory of the new branch:

.. code-block:: bash

   touch .nojekyll
   git add .nojekyll
   
Creating and Publishing Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The documentation can be created as usual by calling

.. code-block:: bash
   
   make html

in :file:`./doc`.

To publish the such created documentation on GitHub, the *gh-pages* branch has
to be commited and pushed to GitHub

.. code-block:: bash

   cd doc/build/html
   git add *
   git commit -a -m "Uploaded current documentation to GitHub"
   git push github gh-pages
   


