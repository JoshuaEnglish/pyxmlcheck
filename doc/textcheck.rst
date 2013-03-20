Text Validators
===============================

.. py:currentmodule:: xcheck

Most validators work with text. These checkers check against fomatting rules

TextCheck
---------

.. autoclass:: TextCheck

EmailCheck
-----------

.. class:: EmailCheck

    EmailCheck is a subclass of text checker. It relies on a regular
    expression, so overriding the pattern attribute is ignored.

    .. attribute:: allowNone [default = True]

        Validates `None` or "None" instead of an email address

    .. attribute:: allowBlank [default = False]

        Validates a blank string as well as an email address

URLCheck
--------

.. autoclass:: URLCheck

