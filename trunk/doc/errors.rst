Errors
=======

Calling any of the data checkers (e.g. IntCheck, TextCheck) with invalid data
should raise the expected exception.  Calling an IntCheck with a string value
of 'fail' should raise a ValueError, just as calling `int('fail')` would in
the intepreter.

The :mod:`xcheck` module defines the following execptions:

.. exception:: XCheckError

    This is the root error, subclassed from Exception, and is used as the generic error in all `xcheck` objects.

.. exception:: MismatchedTagError

    Occurs when the validator expected one tag, and got another.

.. exception:: UnknownAttributeError

    Raised when a checker comes across an attribute of an element that
    it does not know about

.. exception:: AttributeError

    Occurs for general XML attribute related issuse

.. exception:: UncheckedAttributeError

    Occurs when an XML Element has an attribute the checker didn't touch

.. exception:: MissingChildError

    Raised when a required child element is missing

.. exception:: UnexpectedChildError

    Raised when the checker encounters a child element it doesn't know about.