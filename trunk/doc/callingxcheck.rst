.. _calling_xcheck:

Calling an Checker -- Under the Hood
====================================


Calling a checker has been simplified starting with 0.7.1 (rev 34 and up).
These functions return a list of :class:`Exception` instances.

.. function:: check_node(checker, node)

   Runs the other check_xxx functions recursively through a node.
   Returns a list of errors.

.. function:: check_attributes(checker, node)

   Checks the attributes of the node.

   Returns a list of errors.

.. function:: check_node_contents(checker, node)

    Checks the contents of the node by calling the checkeres
    :meth:`check_content` method.. This function will ignore any errors that
    may exist in the attributes of the node.

    Returns a list of errors

.. function:: check_node_ordered_children(checker, node)

   Checks the structure of the children of the node. This function does not
   check the contents or atributes of the node.

   Returns a list of errors.

.. function:: check_node_unordered_chilrden(checker, node)

   Checks the structure of the children of an unordered node. This function
   does not check the contes or attributes of the node.

   Returns a list of errors.

Helpful Decorators
------------------

.. decorator:: validate_input

   Checks that the check_xxx functions are passed an :class:`XCheck` object and
   an :class:`elementtree.Element`

.. decorator:: match_checker_to_node

   Checks that the check_xxx function is passed an appropriate :class:`XCheck`
   object for the given :class:`elementtree.Element` object

This diagram illustrates the basic procedure checker objects follow when
validating data.


.. image:: _static/calling_xcheck.*

