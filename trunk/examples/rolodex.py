import xcheck

item_definition="""<xcheck name="item">
<children>
    <text name="name" min_length="1" />
    <email name="email" max_occurs="4">
        <attributes>
            <selection name="type" values="home, work, personal"/>
        </attributes>
    </email>
</children>
</xcheck>
"""

item = xcheck.load_checker(item_definition)

class Item(xcheck.Wrap):
    def __init__(self, node=None):
        xcheck.Wrap.__init__(self, item, node)

    @property
    def name(self):
        return self._get_elem_value('name')

    @name.setter
    def name(self, value):
        return self._set_elem_value('name', value)


some_person = """<item>
<name>John Doe</name>
<email type="work">lost@fox.com</email>
<email type="personal">knowitall@seattle.net</email>
</item>"""

John = Item(some_person)

print John.name # prints "John Doe"
John.name = 'Jane Doe'
print John.name # prints "Jane Doe"