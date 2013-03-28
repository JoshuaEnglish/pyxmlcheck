Enumeration Validators
======================

SelectionCheck --- Enumerated values
-------------------------------------

`SelectionCheck` limits the values that will validate.

:class:`SelectionCheck` raises two exceptions:

.. exception:: NoSelectionError

    *NoSelectionError* is raised if *values* is an empty list.

.. exception:: BadSelectionsError

    *BadSelectionsError* is raised if the values are not `string` or 
    `unicode` objects.

.. class:: SelectionCheck( *args, values=[ items ], ignoreCase = True)

    .. attribute:: values
    
        *values* must be a list of strings.
    
    .. attribute:: ignoreCase
    
        If **True**, will validate despite the case of the item being
        validated.
    
Examples
^^^^^^^^^

.. code-block:: python

    ch = SelectionCheck('type', values=['fws', 'aide', 'volunteer'])
    ch('FWS') # passes
    ch('fws') # passes
    ch('help') # fails
 
ListCheck --- Multiple Enumerated Values
----------------------------------------

.. class:: ListCheck( *args, [delimiter, values, allowDuplicates, minItems, maxItems, ignoreCase)
    
    :param delimiter: string to separate list items
    :type delimiter: string
    :param values: acceptable values for the list items
    :type values: list
    :param allow_duplicates: determines if list items must be unique
    :type allow_dupliates: boolean
    :param min_items: minimum number of items that should be in the list
    :type min_items: integer
    :param max_items: maximum number of items that should be allowed in the list
    :type max_items: integer
    :param ignore_case: determines if case should matter when validating items
    :type ignore_case: boolean

    .. attribute:: values
    
        If *values* is an empty list, any text values will pass as long
        as the other attribute checks pass.
    
There isn't much difference between :class:`SelectionCheck` and 
:class:`ListCheck`. Future versions may combine them into one class. A :class:`ListCheck`
object is not much more than a :class:`SelectionCheck` object that can read more than 
one item.
