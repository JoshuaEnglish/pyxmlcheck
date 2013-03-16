Text Validators
===============================

Most validators work with text. These checkers check against fomatting rules

TextCheck
----------

TextCheck relies on the `re` module, and the `decimal` module.

.. class:: TextCheck(minLength = 0, maxLength = Infinity, pattern=None)

    The three optional on top of the standard attributes:
    
    .. attribute:: minLength [default 0]
    
        The minimum length of the string that is allowed
    
    .. attribute:: maxLength [default Infinity]
    
        The maximum length of the string
    
    .. attribute:: pattern [default None]
    
        A regular expression that, if not **None**, will check the value
        against the regular expression

EmailCheck
-----------

.. class:: EmailCheck

    EmailCheck is a subclass of text checker. It relies on a regular
    expression, so overriding the pattern attribute is ignored.
    
    .. attribute:: allowNone [default = True]
    
        Validates `None` or "None" instead of an email address
    
    .. attribute:: allowBlank [default = False]
    
        Validates a blank string as well as an email address
