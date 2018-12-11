.. image:: opsmop.png
   :alt: OpsMop Logo

.. _local:

Local
-----

The simplest way to use OpsMop to use is with the local command line.  Soon there 
will also be :ref:`pull` and :ref:`push` modes. 

Opsmop uses policy files written in a pure-Python DSL.  The command line simply
loads a policy file and runs it.

See :ref:`language` for more about the contents of those files.

.. _check:

Check Mode
==========

Check mode runs a policy and reports on actions that should be changed, but does not
make any changes (use :ref:`apply` to make changes).  This is often called a 'dry-run' mode, 
and dry-run support is a first-class citizen of OpsMop::

   cd opsmop-demo/content
   python3 hello.py --check --local

.. _validate:

Validate Mode
=============

To just look for missing files and bad parameters, without running the full check mode,
you can also run::

   cd opsmop-demo/content
   python3 hello.py --validate --local

.. _apply:

Apply Mode
==========

Apply mode runs a policy, plans what changes are needed, and also runs the policy::

    cd opsmop-demo/content
    python3 hello.py --apply --local

.. note:
    OpsMop enforces that planned actions reported in check mode
    match those ran in apply mode. This encourages all modules to have
    have well-implemented dry-run simulations.

Additional Arguments
====================

For -\\-tags, see :ref:`tags`


Next Steps
==========

See :ref:`language`



