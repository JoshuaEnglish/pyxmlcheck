`xcheck` --- XML validation tools
=======================================

.. module:: xcheck
    :synopsis: XML validation tools
    :platform: All
.. moduleauthor:: Josh English <Joshua.R.English@gmail.com>

The :mod:`xcheck` module contains classes for validating XML elements. It uses
the :py:mod:`ElementTree` interface.


The Master Class
------------------

:class:`xcheck` defines the structure of an |xml|-Data node, and validates
|xml|-Data nodes.

.. class:: XCheck(name, [**kwargs])

    This is the default XCheck object that can handle attributes and children.
    All other checkers are subclasses of XCheck.

    :keyword string name: This is the name of the |xml| element tag.

    :keyword int min_occurs: Minimum number of times this element can occur. To
                             make an element optional set this to 0.
                             If the checker represents an |xml| attribute, use
                             :attr:`required` instead.
                             (default = 1)

    :keyword int max_occurs: Maximum number of times this element can occur.
                             (default = 1)

    :keyword Exception error: The default error for this checker, assuming some
                              other, more logical, error is thrown.
                              (defaut = :exc:`XCheckError`)

    :keyword list children: A list of check objects. This list can be populated
                            with the :meth:'add_child` method.
                            (default = [] )

    :keyword bool check_children: Default behavior for checking children of an
                                  |xml| node.

    :keyword bool ordered: If true, the children listed in the checker should
                           match the order of the |xml| node being checked. If
                           false, then the order will not matter.

    :keyword dict attributes: A dictionary of attributes for the checker. This
                              dictionary can be populated with the
                              :meth:`add_attribute` method.

    :keyword bool required: Only applies to checkers for |xml| attributes.
                            (default=True)

    :keyword bool unique: Only applies to attributes.

    :keyword str helpstr: A short descriptor of the checker. This is useful
                          for introspection or GUI applications.

    .. note ::
        There is an interface for XCheck written in wxPython. It will be
        released in 2013. This will use the required and helpstr attributes

    .. deprecated::
        The check_children paramater will most likely be removed in future
        versions.

    XCheck objects have the following properties:

    .. attribute:: name (read-only)

        Returns the name of the checker.


    .. attribute:: has_children

        Returns true if there are children present in the validator

    .. attribute:: has_attributes

        Returs true if the xcheck object expects attributes

    .. attribute:: logger

        Returns a :class:`logging.Logger` instance named after this checker.
        The name is the checker name with "Check" appended.



Creation Methods
^^^^^^^^^^^^^^^^

    XCheck objects have the following methods useful in creation:

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

    .. method:: is_att(tag)

        returns **True** if the tag represents an attribute in the checker object


Usage Methods
^^^^^^^^^^^^^

    The following methods are useful when using the :class:`xcheck`-derived
    objects.

    .. method:: to_dict(node)

        Creates a dictionar representing the node

    .. method from_dict(dict)

        Creates a node from a dictionary, according to the rules of the checker

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



Node Manipulation Methods
^^^^^^^^^^^^^^^^^^^^^^^^^

    The following methods allow an XCheck object to manipulate nodes.

    .. method :: insert_node(parent, child)

        Takes a node and inserts a child node, based on the organiziational
        rules of the checker.

        :param parent, child: ElementTree.Elements to manipulate

        .. warning::

            Only works on first-generation children of the checker!

    .. method :: sort_children(parent, child_name, sortkey[, reverse=False])

        Sorts children of a node according to sortkey.

        :param parent: ElementTree.Element
        :param child_name: string
        :param sortkey: passed to a call to :py:func:`sorted`
        :param reverse: passet to a call to :py:func:`sorted`

    .. method :: to_definition_node()

        Creates an ElementTree.Element that represents the checker tree,
        not data that can be checked by the checker.

        see :func:`load_checker` for more information on the definition node.


Calling a Checker
---------------------------

Calling an :class:`xcheck` object validates whatever is passed to it:

* a simple data type (integer, float)
* a data-equivalent string ()
* an `ElementTree.Element` object
* an XML-formatted string

.. method:: xcheck.__call__(item [, check_children, normalize, as_string])

    Validates the data

    :param bool check_children: overrides the instance attribuet for the
                                current call.
    :param bool normalize: returns a normalized value intstead of
                           **True** or **False**
    :param boolean as_string: return a string representation of the
                              checked value instead of the normalized value.

    .. note::
        The `normalize` and `as_string` parameters do nothing with XCheck
        objects. They are useful for the subclasses.

    .. deprecated:: 0.7.1
        The `verbose` parameter was removed in version 0.7.1. The
        :py:mod:`logging` module is now in place.

__call__ helper methods
^^^^^^^^^^^^^^^^^^^^^^^

    XCheck classes are callable, and rely on two helper methods. For more
    information and examples, see :doc:`rolling`.

    .. method:: check_content( item )

        Checks the item against the checker's rules (either an attribute value
        or node text) and returns a boolean value.

        This method can also raise an error. Errors should be consistent with
        Python. See :doc:`errors` for more information.

    .. method:: nomalize_content( item )

       Uses the checker's normalization rules without checking the validity
       of the item being normalized.


Logging with Checkers
^^^^^^^^^^^^^^^^^^^^^

The logging module has been integrated into XCheck. Each checker has a default
logger accessible through the :attr:`XCheck.logger` attribute.

The :mod:`XCheck` module also creates a new logging level named ``INIT``. It
has a logging level of 2. The INIT messages are created during the creation of
the checker objects.
