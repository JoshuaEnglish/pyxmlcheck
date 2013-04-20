Definition Nodes
=================

Using the checker classes themselves, defining complex checkers can lead to
complicated code that is harder to parse, as in this simple rolodex entry:

.. code-block:: python

    nick = BoolCheck('nick', required=False)
    fname = TextCheck('first', min_length = 1)
    fname.addattribute(nick)

    lname = TextCheck('last', min_length = 1)
    code = IntCheck('code', min_occurs = 1, max_occurs = 5)
    code.addattribute(TextCheck('word', required=False) )
    name = XCheck('name', children=[fname, lname, code])

    emailtype = SelectionCheck('type', values = ['home','work', 'personal'])
    email = EmailCheck('email', max_occurs=2)
    email.addattribute(emailtype)
    street = TextCheck('street')
    city = TextCheck('city')

    address = XCheck('address', children=[street, city, email], max_occurs=4)

    dude = XCheck('dude', children=[name, address],
        help="A simple contact list item")
    idch = IntCheck('id', required=True)
    dude.addattribute(idch)

This style creates the children checkers, then creates the main object.
Alternately, this could be created in a top-down manner:

.. code-block:: python

    dude = XCheck('dude', help="A simple contact list item")

    # can add some attributes without creating them seprately first
    dude.addattribute(IntCheck('id', required=True))

    # complex children can be defined and added

    name = XCheck('name')
    fname = TextCheck('first', min_length = 1)
    fname.addattribute(BoolCheck('nick', required=False))
    lname = TextCheck('last', min_length = 1)
    code = IntCheck('code', min_occurs = 1, max_occurs = 5)
    code.addattribute(TextCheck('word', required=False) )

    name.add_children(fname, lname, code)

    # ... etc

The :func:`load_checker` function allows users to write definition nodes that
can be translated into an XML definition node:

.. code-block:: python

    dude_defition = """<xcheck name="dude">
    <attributes>
        <int name="id" required="true" />
    </attributes>
    <children>
        <xcheck name="name">
            <text name="first" min_length="1">
                <attributes>
                    <text name="nick" required="false"/>
                </attributes>
            </text>
            <text name="last" min_length="1" />
            <int name="code" min_occurs="1" max_accurs="5">
                <attributes>
                    <text name="word" required="false" />
                </attributes>
            </int>
        </xcheck>
        <xcheck name="address" max_occurs="4">
            <children>
                <text name="street" />
                <text name="city" />
                <email name="email" max_occurs="2">
                    <attributes>
                        <selection name="type" values="home, work, personal" />
                    </attrubutes>
                </email>
            </children>
        </xcheck>
    </children>
    </xcheck>
    """

.. note ::

    Future plans include removing the `children` tag, assuming every child under
    the `xchecx` definition node is a child unless they are under the `attributes`
    child or has a special `is_attribute` xml attribute.

    Other future plans include an RNG to XCheck converter.


Definition nodes use tags defining the checker:

=========   ===============
tag         Checker Created
=========   ===============
xcheck      XCheck
text        TextCheck
email       EmailCheck
url         URLCheck
int         IntCheck
decimal     DecimalCheck
datetime    DatetimeCheck
bool        BoolCheck
selection   SelectionCheck
list        ListCheck
=========   ===============

Each XML element must have a `name` attribute, which is the tag the checker will
look for. Other attributes are mapped to the keyword arguments that are called
when :func:`load_checker` creates the XCheck object.

If you define your own checker class (see :doc:`rolling`), you can get
:func:`load_checker`  to accept your class by calling::

    xcheck.loader.LOAD_RULES[name] = YourClass

before you call :func:`load_checker`.

The :func:`load_checker` function recognizes several custom attributes. If your
custome checker class uses these attributes, :func:`load_cheker` will work.

==============  ================
attribute       Treated as
==============  ================
min             int or decimal
max             int or decimal
min_value       int or decimal
max_value       int or decimal

min_length      int
max_length      int
min_occurs      int
max_occurs      int

required        bool
unique          bool
check_children  bool

ordered         bool
allow_none      bool
allow_blank     bool
none_is_false   bool

pattern         string
delimiter       string [#f1]_

error           exception [#f2]_
==============  ================



If you have a custom attribute not listed here, :func:`load_checker` will fail.

.. rubric:: Footnotes

.. [#f1] The :class:`SelectionCheck` class does not have a delimiter, but the
         definition node does.
.. [#f2] If the exception class is not in :py:func:`globals()` then
         :func:`load_checker` will raise an :exc:`UnmatchedError`
