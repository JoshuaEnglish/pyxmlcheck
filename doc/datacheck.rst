Data Type Checkers
==================

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


DateTimeCheck --- DateTime validation
-------------------------------------