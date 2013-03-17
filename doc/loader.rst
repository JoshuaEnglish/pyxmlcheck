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

    address = XCheck('address', children = [street, city, email], max_occurs = 4)

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





