`xcheck` --- XML validation tools
=======================================

.. module:: xcheck
    :synopsis: XML validation tools
    :platform: All
.. moduleauthor:: Josh English <Joshua.R.English@gmail.com>

The :mod:`xcheck` module contains classes for validating XML elements. It uses
the :mod:`ElementTree` interface.

The :mod:`xcheck` module defines the following execption:

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

:class:`xcheck` -- The Master Class
-------------------------------------------------

:class:`xcheck` defines the structure of the XML data, and validates
XML data

.. class:: XCheck(name, [**kwargs])

    This is the default XCheck object that can handle attributes and children

    .. attribute:: name

        required. This is the name of the XML element tag the checker will validate.

    .. attribute:: min_occurs ([default = 1])

        The minimum number of times the element must appear as a child.
        To make an element optional, set  `min_occurs` to 0.

    .. attribute:: max_occurs ([default = 1])

        The maximum number of times the element can appear

    .. attribute:: error ( [XCheckError] )

        Failing to validate raises an exception. Some Exceptions are
        standardized, but custom errors can have their own Exceptions

        The Exception class should be a subclass of XCheckError.

    .. attribute:: children([default = [] ])

        A list of children check object. This list can also be populated with
        the :meth:`addchild` method below.

    .. attribute:: check_children([True])

        If true, the default behavior of the xcheck will be to check all
        children. This can still be overridden when calling an XCheck object.

    .. attribute:: ordered [True]

        If **True**, the child elements must be in order according to
        the order according the `xcheck.children` list.

        If **False**, the order does not matter, but everything else is
        checked.

    .. attribute:: attributes([default = {} ] )

        A dictionary of attributes for the element. This dictionary can
        also be populated with the :meth:`addattribute` method below.

    .. attribute:: required([default = True])

        A boolean value for XML Attribute checkers.
        XChecx objects will fail if a required attribute
        is not found, but let go an attribute that is not required.

        Any attributes that are found will be checked.

    .. attribute:: unique([default = False])

        If true, the attribute value must be unique among all elements
        with the same tag name.

        .. note ::

            This attribute does nothing within the context of XCheck itself.
            This attribute is used by the pyxmldb package.

    .. attribute:: helpstr([default = None])

        A short descriptor of the checker. Can be useful in introspection
        or for GUI applications.

        .. note ::

            There is an interface for XCheck written in wxPython. It will be
            released in 2013.

    XCheck classes have the following methods:

    .. method:: add_child( children )

        add a list of child objects to the expected children
        raises an error if any child object is not an instance of  an XCheck class

        If passing a list, unpack it:

            .. code-block:: python

                >>>x = XCheck('test')
                >>>kids = [XCheck('a'), XCheck('b'), XCheck('c')]
                >>>x.addchildren(*kids)

    .. method:: add_children( children)

        This is an alias for addchild. The same rules apply

    .. method:: add_attribute( attributes )

        Adds expected attributes to the :class:`xcheck` object.

        If passing a list, unpack it.

    XCheck classes have the following methods:

    .. attribute:: name

        returns the name of the checker.

    .. method:: is_att(tag)

        returns **True** if the tag represents an attribute in the checker object

    .. method:: to_dict(node)

        Creates a dictionar representing the node

    .. method from_dict(dict)

        Creates a node from a dictionary, according to the rules of the checker

    .. attribute:: has_children

        Returns true if there are children present in the validator

    .. attribute:: has_attributes

        Returs true if the xcheck object expects attributes

    .. method:: has_attribute(tag)

        Returns **True** if one of the checker's attributes matches 'tag'.

    .. method:: has_child(tag)

        Returns **True** if one of the checker's children attributes matches 'tag'.

    .. method:: get(tag)

        Returns the attribute or child checker object

    .. method:: dict_key(tag)

        Returns an XMLPath dotted with the attribute (if needed).

    .. method:: path_to(tag)

        Returns an (XMLPath, attribute) tuple to the given tag.

    .. method:: xpath_to(tag)

        Returns a formatted xpath string.

    XCheck classes are callable, and rely on two helper methods.

    .. method:: checkContent( item )

        checkContent returns a boolean value, but should raise
        a custom Exception if validation failed.

    .. method:: nomalizeContent( item )

        Unimplemented in version 1.0.0. Future development may use the
        xcheck to change the content it was passed and return
        the item


    The following methods allow an XCheck object to manipulate nodes.

    .. automethod :: insert_node(parent, child)

    .. automethod :: sort_children(parent, child_name, sortkey[, reverse=False])

    .. automethod :: to_definition_node

    see :func:`load_checker` for more information on the definition node.


Calling an `xcheck` object
---------------------------

Calling an :class:`xcheck` object validates whatever is passed to it:

* a simple data type (integer, float)
* a data-equivalent string ()
* an `ElementTree.Element` object
* an XML-formatted string

.. method:: xcheck.__call__(item [, check_children, normalize, verbose, as_string])

    Validates the data

    :param check_children: overrides the instance attribuet for the current call.
    :type check_children: boolean
    :param normalize: returns a normalized value intstead of **True** or **False**
    :type normalize: boolean
    :param verbose: prints a report as the checker processes
    :type verbose: boolean
    :param as_string: return a string representation of the checked value instead of the normalized value.
    :type as_string: boolean

The `normalize` and `as_string` parameters do nothing with XCheck objects. They
are useful for the subclasses.

The `verbose` parameter will be relpaced in future, relying on the :py:mod:`logging` module.





