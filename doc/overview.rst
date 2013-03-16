Overview
========

:mod:`xcheck` is used to validate xml in Python. No other code is required.

:class:`XCheck` objects can:

* use different rules to determine the content of XML elements
* validate ordered and unordered elements
* :class:`xcheck` objects are callable, and can check:
        * real data
        * strings that represent real data
        * ElementTree.Element objects
        * Text representing an ElementTree.Element object

There are a few rules about the assumptions xcheck uses. :mod:`xcheck` is designed 
to validate XML-Data, which, as I see it, as a few limitations:

* No Meaningful Mixed Content: an element has either text or children, but not both.
* Whitespace between children of an element is ignored. This allows the xml to be written with human-readable line breaks.
* Spaces around an element's text is ignored. This means <x>a</a> and <x> a </x> are considered the same element and validate the same.


Currently, :class:`xcheck` objects do not deal with namespaces.

:class:`XCheck` objects are called directly to check data. ::
    
    >>> from xcheck import TextCheck
    >>> nameCh = TextCheck('name', minLength = 2)
    >>> nameCh('Josh')
    True
    >>> nameCh('J')
    
    Traceback (most recent call last):
      File "<pyshell#3>", line 1, in <module>
        name('J')
      File "C:\Python26\lib\site-packages\xcheck\xcheck.py", line 391, in __call__
        ok = self.checkContent(arg)
      File "C:\Python26\lib\site-packages\xcheck\xcheck.py", line 671, in checkContent
        raise self.error, "Text too short"
    XCheckError: Text too short
    >>> nameCh('<name>Josh</name>')
    True
    >>> from elementtree import ElementTree as ET
    >>> josh = ET.Element('name')
    >>> josh.text = 'Josh'
    >>> ET.dump(josh)
    <name>Josh</name>
    >>> nameCh(josh)
    True
    >>> 

The :mod:`xcheck` module defines the following classes:

:class:`XCheck`
        
    The base checker. Used only for parent nodes.
    
:class:`TextCheck`

    Checker for generic text

:class:`EmailCheck`

    Checker for email addresses
    
:class:`URLCheck`

    Checker for URLs (web address)

:class:`BoolCheck`

    Checker for boolian values

:class:`SelectionCheck`

    Checker for data from a selection of acceptable values.

:class:`IntCheck`

    Checker for integer values

:class:`DecimalCheck`

    Checker for float values

:class:`ListCheck`

    Checker for list-formatted strings

:class:`DateTimeCheck`

    Checker for dates and times

:class:`wrap`

    :class:`wrap` provides an interface between a checker and an element. ::

    >>> from xcheck import XCheck, TextCheck, wrap
    >>> first = TextCheck('first', minLength = 2)
    >>> last = TextCheck('last', minLength = 2)
    >>> nameCh = XCheck('name', children = [first, last])
    >>> from elementtree import ElementTree as ET
    >>> name = ET.Element('name')
    >>> fname = ET.SubElement(name, 'first')
    >>> fname.text = 'Josh'
    >>> lname = ET.SubElement(name, 'last')
    >>> lname.text = 'English'
    >>> ET.dump(name)
    <name><first>Josh</first><last>English</last></name>
    >>> nameCh(name)
    True
    >>> nameObj = wrap(nameCh, name)
    >>> nameObj._get_elem_value('first')
    'Josh'
    >>> nameObj._get_elem_value('last')
    'English'
    >>> 
