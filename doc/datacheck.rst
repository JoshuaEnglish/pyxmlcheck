Data Type Checkers
==================

.. py:currentmodule:: xcheck

Other standard datatypes have their own checkers.

BoolCheck --- Boolean Validation
--------------------------------

BoolCheck checks against a number of boolean-equivalent expressions.

.. class:: BoolCheck(*args, noneIsFalse)

    The optional attribute on top of the standard attributes:

    .. attribute:: noneIsFalse [default True]

        If **True**, accepts `None` or "None" and treates as **False**.

:class:`BoolCheck` accepts the following values and interprets them as **True**

    * `True`, "TRUE", "True", "true", "T", "t", "YES", "Yes", "yes", "Y", "y", "1"

:class:`BoolCheck` accepts the following values and interprets them as **False**

    * `False`, "FALSE", "False", "false", "F", "f", "NO", "No", "no", "N", "n", "0"




IntCheck --- Integer Validation
-------------------------------

.. autoclass:: IntCheck

Calling an :class:`IntCheck` instance supports the `as_string` keyword.

The following example shows the many ways :class:`IntCheck` accepts data:

.. code-block:: python

    from xcheck import IntCheck, ET

    value = IntCheck('value', min=2, max=12)
    text = '<value>5</value>'
    node = ET.fromstring(text)

    print value(9)
    print value('9')
    print value('9.0')
    print value(text)
    print value(node)

All of the above lines will print `True`.

DecimalCheck --- Float Validation
---------------------------------

.. autoclass:: DecimalCheck

DateTimeCheck --- DateTime validation
-------------------------------------


.. autoclass:: DatetimeCheck