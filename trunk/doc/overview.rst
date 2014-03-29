.. py:module::xcheck

Overview
========

:mod:`xcheck` is used to validate xml in Python. It requires ElementTree
version 1.1.3. Most features can be used with other versions of ElementTree.

:class:`XCheck` objects can:

* use different rules to determine the content of |xml| elements
* validate ordered and unordered elements
* validate attributes and contents of elements
* :class:`xcheck` objects are callable, and can check:
        * real data
        * strings that represent real data
        * ElementTree.Element objects
        * Text representing an ElementTree.Element object

The :mod:`xcheck` module makes a few assumtions about |xml|-data, which, as
I see it, as a few limitations:

* No Meaningful Mixed Content: an element has either text or children,
  but not both.
* Whitespace between children of an element is ignored. This allows the
  |xml| to be written with human-readable line breaks.
* Spaces around an element's text is ignored. This means <x>a</a> and <x> a </x> are considered the same element and validate the same.


.. note ::
    Currently, :class:`XCheck` objects do not deal with namespaces.

:class:`XCheck` objects are called directly to check data::

    >>> from xcheck import TextCheck
    >>> nameCh = TextCheck('name', min_length = 2)
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

=============== ===========================================
Checker 	    Data to be checked
=============== ===========================================
XCheck		    The base checker, used for parent XML nodes
TextCheck	    Generic texts
EmailCheck	    Email Addresses
URLCheck	    URLs
IntCheck	    Integers
DecimalCheck	Floats
DatetimeCheck	Dates and times
BoolCheck	    Boolean values
SelectionCheck	Choice of various strings
ListCheck	    Lists of strings with filtering
=============== ===========================================

Other Helpful Things
--------------------

There are two extra tools that XMLCheck defines to make working with |xml|
easier.

:class:`Wrap`

    The :class:`Wrap` provides an interface between a checker and an element,
    creating a Python object::

        >>> from xcheck import XCheck, TextCheck, Wrap
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
        '<name><first>Josh</first><last>English</last></name>'
        >>> nameCh(name)
        True
        >>> nameObj = Wrap(nameCh, name)
        >>> nameObj._get_elem_value('first')
        'Josh'
        >>> nameObj._get_elem_value('last')
        'English'


    The :class:`Wrap` class can be subclassed to provide more meaninful
    attributes.

:func:`load_checker`

    The ``load_checker`` function Creates an :class:`XCheck` object from a
    definiton node. The rules for creating a definiton node are outlined
    in :doc:`loader`.