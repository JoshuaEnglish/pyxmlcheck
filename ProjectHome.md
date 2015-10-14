xcheck 0.7.1 -- Tools for validating XML in Python

xcheck is used to validate XML in Python. Uses the ElementTree interface.

XCheck objects can:

  * use different rules to determine the content of XML elements
  * validate ordered and unordered elements
  * xcheck objects are callable, and can check:
    * real data
    * strings that represent real data
    * ElementTree.Element objects
    * Text representing an ElementTree.Element object

There are a few rules about the assumptions xcheck uses. xcheck is designed
to validate XML-Data, which, as I see it, as a few limitations:

  * No Meaningful Mixed Content: an element has either text or children, but not both.
  * Whitespace between children of an element is ignored. This allows the xml to be written with human-readable line breaks.
  * Spaces around an element's text is ignored. This means `<x>a</a>` and `<x> a </x>` are considered the same element and validate the same.

The documentation is still a work in progress and can be found at http://pythonhosted.org/XMLCheck/

The Updated download can be found at https://pypi.python.org/pypi/XMLCheck