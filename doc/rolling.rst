Rolling your own
================

Creating your own validator is easy. Keep these rules in mind:

* Subclass :class:`xcheck`
* Capture custom attributes inthe __call__ method
* Append any custom attributes to the ``_object_atts`` list
* write a `checkContent` method
* write a `normalizeContent` method


.. note::
    There is no mechanism for loading custom checkers with the
    :func:`load_chekcer` function, but the :meth:`to_definition_node` method
    should generate something.

For example, :mod:`xcheck` does not have a built-in ComplexCheck class.

Lets assume that we want to allow `None` as well. We want to be able to return
a string representation, a complex number, and a (real, imag) tuple when
validating an object.

.. literalinclude:: ..\examples\complexcheck.py
    :lines: 1-64

A simple set of unit tests can verify your new checker is working.

.. literalinclude:: ..\examples\complexcheck.py
    :lines: 66-