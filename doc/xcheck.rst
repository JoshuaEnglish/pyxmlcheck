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
    
    .. attribute:: minOccurs ([default = 1])
    
        The minimum number of times the element must appear.
        To make an element optional, set  `minOccurs` to 0.
    
    .. attribute:: maxOccurs ([default = 1])
     
        The maximum number of times the element can appear
    
    .. attribute:: error ( [XCheckError] )
    
        Failing to validate raises an exception. Some Exceptions are 
        standardized, but custom errors can have their own Exceptions
        
        The Exception class should be a subclass of XCheckError.
    
    .. attribute:: children([default = [] ])
    
        A list of children check object. This list can also be populated with the 
        :meth:`addchild` method below.
    
    .. attribute:: checkChildren([True])
    
        If true, the default behavior of the xcheck will be to check all
        children. This can still be overridden when calling an XCheck object.
    
    .. attribute:: ordered [True]
    
        If **True**, the child elements must be in order according to
        the order according the `xcheck.children` list.
        
        If **False**, the order does not matter, but everything else is 
        checked.
        
    .. attribute:: attributes([default = {} ] )
    
        A dictionary of attributes for the element. This dictionary can also be populated with the `addattribute` method below.

    .. attribute:: required([default = True])
    
        A boolean value. XChecx objects will fail if a required attribute
        is not found, but let go an attribute that is not required.
        
        Any attributes that are found will be checked.
    
    .. attribute:: unique([default = False])
        
        If true, the attribute value must be unique among all elements
        with the same tag name.
    
    XCheck classes have the following methods:
    
    .. method:: addchild( children )
    
        add a list of child objects to the expected children
        raises an error if any child object is not an instance of  an XCheck class
        
        If passing a list, unpack it:
            
            .. code-block:: python
            
                >>>x = XCheck('test')
                >>>kids = [XCheck('a'), XCheck('b'), XCheck('c')]
                >>>x.addchildren(*kids)
            
    .. method:: addchildren( children)
    
        This is an alias for addchild. The same rules apply
    
    .. method:: addattribute( attributes )
    
        Adds expected attributes to the :class:`xcheck` object. 
        
        If passing a list, unpack it.
    
    XCheck classes have the following methods wrapped as properties:
    
    .. method:: name
    
        returns the name of the checker.
    
    .. method:: haschildren
    
        Returns true if there are children present in the validator
    
    .. method:: hasattirbutes
    
        Returs true if the xcheck object expects attributes
    
    XCheck classes are callable, and rely on two helper methods.
    
    .. method:: checkContent( item )
    
        checkContent returns a boolean value, but should raise 
        a custom Exception if validation failed.
    
    .. method:: nomalizeContent( item )
    
        Unimplemented in version 1.0.0. Future development may use the
        xcheck to change the content it was passed and return
        the item
    
    XCheck classes have some 'advanced' methods as well. These methods 
    are purely optional.
    
    
    .. method:: toElem()
    
        Returns an ElementTree.Element object that stores data about the checker.
        A future implementation will read these objects and restore the XCheck object
    
    .. method:: toClass( [verbose=False])
    
        Returns a class representing the XCheck object. This method has two attributes that
        are used internally to aid in the creation of the class.
        
        If *verbose* is True, the text of the class will be printed.
        
        If the :class:`xcheck` object has no children or attributes, a SyntaxError will be generated

    .. versionadded:: 0.2
    
        The :meth:`toElem` and :meth:`toClass` methods.
    
    
Calling an `xcheck` object
---------------------------
    
Calling an :class:`xcheck` object validates whatever is passed to it:
    
* a simple data type (integer, float) 
* a data-equivalent string ()
* an `ElementTree.Element` object
* an XML-formatted string

.. method:: xcheck.__call__(item [, checkChildren, _normalize])
    
    Validates the data
    :param checkChildren: overrides the instance attribuet for the current call.
    :type checkChildren: boolean
    :param _normalize: returns a normalized value intstead of **True** or **False**
    :type _normalize: boolean

