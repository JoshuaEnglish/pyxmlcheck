#~ -----------------------------------------
#~ UNIT TESTS
#~ -----------------------------------------
import unittest
import test.test_support

from xcheck import *
class XCheckTC(unittest.TestCase):
    def setUp(self):
        self.c = XCheck('test')

    def tearDown(self):
        del self.c

    def testBadXMLTag(self):
        self.assertRaises(self.c.error, self.c, '<text/>')

    def testfailNormalization(self):
        "XCheck() fails if _normalize is True but no normalizedValue is created"
        self.assertRaises(self.c.error, self.c, '<test/>', _normalize=True)

    def testDefaults(self):
        "XCheck creates the proper default attributes"
        self.assertEqual(self.c.minOccurs, 1, "minOccurs is not 1")
        self.assertEqual(self.c.maxOccurs, 1, "maxOccurs is not 1")
        self.assertEqual(self.c.children, [], "children not an empty list")
        self.assertEqual(self.c.unique, False, "unique not False")
        self.assertEqual(self.c.required, True, "required not True")
        self.assertEqual(self.c.attributes, {}, "attributes not an empty dictionary")
        self.assertTrue(issubclass(self.c.error, Exception), "error not derived from Exception")
        self.assertTrue(self.c.checkChildren, "checkChildren not True")
        self.assertTrue(self.c.ordered, "ordered not True")

    def testCustomizationOfAttributes(self):
        "XCheck customizes attributes"
        children = [XCheck('a'), XCheck('b')]
        attributes = {'c': XCheck('c')}
        c = XCheck('test', minOccurs=2, maxOccurs = 3, children= children, \
            unique = True, required=False, attributes = attributes, error=TypeError, \
            checkChildren = False, ordered=False)
        self.assertEqual(c.name, 'test', "name is incorrect")
        self.assertEqual(c.minOccurs, 2, "minOccurs not set correctly")
        self.assertEqual(c.maxOccurs, 3, "maxOccurs not set correctly")
        self.assertEqual(c.children, children, "children not set correctly")
        self.assertTrue(c.unique, "unique not set correctly")
        self.assertFalse(c.required, "required not set correctly")
        self.assertEqual(c.attributes, attributes, "attributes not set correctly")
        self.assertEqual(c.error, TypeError, "error not set correctly")
        self.assertFalse(c.checkChildren, "checkChildren not set correctly")
        self.assertFalse(c.ordered, "ordered not set correctly")


class AttributesTC(unittest.TestCase):
    def setUp(self):
        self.val = IntCheck('val', min=1, max=10, error=TypeError)
        self.t = XCheck('test')
        self.t.addattribute(self.val)

    def tearDown(self):
        del self.t
        del self.val

    def testFailWithBadAttribute(self):
        "XCheck raises AttributeError on adding non-XCheck attribute"
        for item in ['a', 2, 4.5, TypeError]:
            self.assertRaises(AttributeError, self.t.addattribute, item)

    def testFailWithBadAttributeDictionary(self):
        "XCheck raises AttributeError if attribute dictionary is ill-formed"
        self.assertRaises(AttributeError, XCheck, 'name', attributes={'this': XCheck('that')} )

    def testFailWithNonXCheckAttributeDictionary(self):
        "XCheck raises AttributeError if attributes dictionary values are not XCheck objects"
        self.assertRaises(AttributeError, XCheck, 'name', attributes={'this':'that'} )

    def testPassWithGoodAttribute(self):
        "XCheck.addattribute() adds valid attributes"
        self.t.addattribute(XCheck('b') )
        self.failUnless('b' in self.t.attributes, 'did not append attribute properly')

    def testAttributeValidation(self):
        "XCheck() accepts valid attribute values"
        self.failUnless(self.t('<test val="3" />'))

    def testNonRequiredAttribute(self):
        "XCheck() accepts a missing non-required attribute"
        self.t.attributes['val'].required = False
        self.failUnless(self.t('<test />'))

    def testDoubleAttribute(self):
        "XCheck.addattribute() raises AttributeError trying to add a second attribute with duplicate name"
        self.assertRaises(AttributeError, self.t.addattribute, TextCheck('val') )

    def testBadAttribute(self):
        "XCheck() fails if an attribute doesn't check"
        self.assertRaises(self.val.error, self.t, '<test val="0" />')

    def testExtraAttribute(self):
        "XCheck() raises UnknownAttributeError if element attribute is unknown"
        self.assertRaises(UnknownAttributeError, self.t, '<test val="4" ex="true"/>')

    def testUnchecked(self):
        "XCheck() raises UncheckedAttributeError if a required attribute was not checked"
        self.assertRaises(UncheckedAttributeError, self.t, '<test />')

    def testEmptyAttribute(self):
        "XCheck() raises ValueError if value for required attribute is empty"
        self.assertRaises(ValueError, self.t, '<test val=""/>')

class UnorderedChildrenTC(unittest.TestCase):
    def setUp(self):
        self.c = XCheck('test', ordered=False)
        self.c.addchild(XCheck('a') )
        self.c.addchild(XCheck('b', minOccurs = 0, maxOccurs = 2) )
        self.c.addchild(XCheck('c') )
    
    def tearDown(self):
        del self.c
    
    def testAcceptableVariations(self):
        "Unordered check accepts children in order"
        self.failUnless(self.c('<test><a/><b/><c/></test>'), "Unordered check didn't like ABC")
        self.failUnless(self.c('<test><a/><c/><b/></test>'), "Unordered check didn't like ACB")
        self.failUnless(self.c('<test><b/><a/><c/></test>'), "Unordered check didn't like BAC")
        self.failUnless(self.c('<test><b/><c/><a/></test>'), "Unordered check didn't like BCA")
        self.failUnless(self.c('<test><c/><a/><b/></test>'), "Unordered check didn't like CAB")
        self.failUnless(self.c('<test><c/><b/><a/></test>'), "Unordered check didn't like CBA")
        self.failUnless(self.c('<test><a/><c/></test>'), "Unordered check didn't like AC")
        self.failUnless(self.c('<test><c/><a/></test>'), "Unordered check didn't like CA")
        self.failUnless(self.c('<test><a/><b/><b/><c/></test>'), "Unordered check didn't like ABBC")
        self.failUnless(self.c('<test><b/><a/><b/><c/></test>'), "Unordered check didn't like BABC")
        self.failUnless(self.c('<test><b/><b/><a/><c/></test>'), "Unordered check didn't like BBAC")
    
    def testUnexpectedChild(self):
        "Unordered check fails if it finds an unexpected child"
        self.assertRaises(UnexpectedChildError, self.c, '<test><unwanted/></test>')
    
    def testNotEnoughChidren(self):
        "Unordered check fails if it doesn't find enough children"
        self.assertRaises(MissingChildError, self.c, '<test><b/><b/><c/></test>')
        self.assertRaises(MissingChildError, self.c, '<test><a/></test>')
    
    def testTooManyChildren(self):
        "Unordered check fails if it finds too many children"
        self.assertRaises(UnexpectedChildError, self.c, '<test><a/><a/><c/></test>')
        self.assertRaises(UnexpectedChildError, self.c, '<test><a/><b/><b/><b/><c/></test>')
        self.assertRaises(UnexpectedChildError, self.c, '<test><a/><b/><c/><c/></test>')
        
        
class ChildrenTC(unittest.TestCase):
    def setUp(self):
        self.p = XCheck('parent')
        c = XCheck('child')
        self.p.addchild(c)
        self.m = XCheck('kid', minOccurs=2, maxOccurs= 3)

    def tearDown(self):
        del self.p
        del self.m

    def testPassChildren(self):
        "XCheck() accepts known children elements"
        self.failUnless(self.p("<parent><child/></parent>"))

    def testPassWithMultipleChildren(self):
        "XCheck() accepts multiple copies of one child if child.maxOccurs allows"
        self.p.children[0].maxOccurs= 2
        self.failUnless(self.p("<parent><child/><child/></parent>"))

    def testPassWithSequentialChildren(self):
        "XCheck() accepts a sequence of children"
        self.p.addchild(self.m)
        self.failUnless(self.p("<parent><child/><kid/><kid/></parent"))

    def testPassWithGrandChildren(self):
        "XCheck() accepts multiple levels of children"
        self.p.children[0].addchild(self.m)
        self.failUnless(self.p("<parent><child><kid/><kid/></child></parent>"))

    def testFailWithUnexpectedChildren(self):
        "XCheck() raises UnexpectedChildError if element has children and checker expects none"
        t = XCheck('check', checkChildren = True)
        self.assertRaises(UnexpectedChildError, t, "<check><unwanted/></check>")

    def testIgnoreChildren(self):
        "XCheck() should ignore children if told"
        t = XCheck('check', checkChildren = False)
        self.failUnless(t("<check><unexpected/></check>"), "XCheck checked children even when told not to")
        self.failUnless(self.p("<parent><unexected/></parent>", checkChildren = False), "XCheck checked children at call when told not to")
        
    def testFailUnknownChild(self):
        "XCheck() fails with unknown child"
        self.assertRaises(self.p.error, self.p, "<parent><mystery/></parent>")

    def testFailWithExtraChild(self):
        "XCheck() fails with more children elements than checker.maxOccurs allows"
        self.assertRaises(UnexpectedChildError, self.p, "<parent><child/><child/></parent>")

    def testFailWithMissingChild(self):
        "XCheck() fails if a required child is missing"
        self.assertRaises(MissingChildError, self.p, "<parent/>")
    
    def testAcceptOptionalChild(self):
        "XCheck() accepts an optional child"
        self.p.children[0].minOccurs= 0
        self.failUnless(self.p('<parent/>'), "XCheck cannot handle optional child")
        self.failUnless(self.p('<parent><child/></parent>'), "XCheck cannot handle an optional child that exists")
    
    def testAcceptOptionalChild2(self):
        "XCheck() accepts an optional child that is not the first child"
        self.m.minOccurs = 0
        self.p.addchild(self.m)
        self.failUnless(self.p('<parent><child/></parent'), "XCheck cannot handle an optional child that is not the first")
        self.failUnless(self.p('<parent><child/><kid/></parent>'), "Oops")

class TextCheckTC(unittest.TestCase):
    def setUp(self):
        self.t = TextCheck('text', minLength = 4, maxLength = 8)

    def tearDown(self):
        del self.t

    def testDefaults(self):
        "TextCheck creates the proper default attributes"
        t = TextCheck('text')
        self.assertEqual(t.minLength, 0, "minLength not 1")
        self.assertEqual(t.maxLength, Inf, "maxLength not 1")
        self.assertEqual(t.pattern, None, "pattern not None")

    def testCustomizedAttributes(self):
        "TextCheck customizes attributes"
        t = TextCheck('text', minLength=4, maxLength=8, pattern=r'blah')
        self.assertEqual(t.minLength, 4, "minLength not set correctly")
        self.assertEqual(t.maxLength, 8, "maxLength not set correctly")
        self.assertEqual(t.pattern, r'blah', "pattern not set correctly")

    def testPassWithMinString(self):
        "TextCheck() accepts strings of the minimum length"
        self.failUnless(self.t('abcd') )

    def testPassWithMaxString(self):
        "TextCheck() accepts strings of the maximum length"
        self.failUnless(self.t('abcdefgh') , "TextCheck() accepted a string longer than the maximum length")

    def testPassWithElement(self):
        "TextCheck() accepts an elementtree.Element"
        self.failUnless(self.t(ET.fromstring('<text>abcde</text>') ) )

    def testPassWithElementString(self):
        "TextCheck() accepts an xml-formatted string"
        self.failUnless(self.t('<text>abcdef</text>'))

    def testFailWithTooShortString(self):
        "TextCheck() fails if the string is too short"
        self.assertRaises(self.t.error, self.t, "abc")

    def testFailWithTooLongString(self):
        "TextCheck() fails if the string is too long"
        self.assertRaises(self.t.error, self.t, "123456789")

    def testFailWithTooShortElement(self):
        "TextCheck() fails if the element.text is too short"
        self.assertRaises(self.t.error, self.t, ET.fromstring('<text>abc</text>') )

    def testFailWithTooShortXMLString(self):
        "TextCheck() fails if the xml string text is too short"
        self.assertRaises(self.t.error, self.t, '<text>a</text>')
    
    #~ def testFailWithEmptyElement(self):
        #~ "TextCheck() fails if the xml element has no text but checker expects some"
        #~ self.assertRaises(self.t.error, self.t, '<text/>')

    def testPassWithPattern(self):
        "TextCheck() accepts strings that match the given pattern"
        t = TextCheck('test', pattern=r'\S+@\S+\.\S+')
        self.failUnless(t('english@spiritone.com') )

    def testFailWithPattern(self):
        "TextCheck() fails if the string doesn't match the given pattern"
        t = TextCheck('test', pattern=r'\S+@\S+\.\S+')
        self.assertRaises(t.error, t, 'english @ spiritone.com')

class EmailCheckTC(unittest.TestCase):
    def setUp(self):
        self.t = EmailCheck('email')
        self.n = EmailCheck('email', allowNone = False)
        self.b = EmailCheck('email', allowBlank = True)
    
    def tearDown(self):
        del self.t
        del self.n
        del self.b

    def testDefaultEmail(self):
        "EmailCheck() accepts valid simple email addresses"
        self.failUnless(self.t('english@spiritone.com'))

    def testDefaults(self):
        "EmailCheck creates the proper default attributes"
        self.assertTrue(self.t.allowNone, "allowNone not True")
        self.assertFalse(self.t.allowBlank, "allowBlank not False")

    def testDefaultEmailasNoneString(self):
        "EmailCheck() defaults to allow 'None'"
        self.failUnless(self.t('None'))

    def testDefaultEmailAsNone(self):
        "EmailCheck() defaults to allow None object"
        self.failUnless(self.t(None))

    def testDefaultEmailAsBlank(self):
        "EmailCheck() fails if email is blank and allowBlank is False"
        self.assertRaises(self.t.error, self.t, '')

    def testCustomAllowNone(self):
        "EmailCheck handles allowNone=False"
        self.failIf(self.n.allowNone)

    def testFailCustomAllowNone(self):
        "EmailCheck() fails if allowNone is false and given None"
        self.assertRaises(self.n.error, self.n, 'None')

    def testFailCustomAllowBlank(self):
        "EmailCheck() allows a blank string if allowBlank is true"
        self.failUnless(self.b(''))

    def testFailCustomAllowBlankEmpty(self):
        "EmailCheck() allows an empty string if allowBlank is true"
        self.failUnless(self.b(' '))

class IntCheckTC(unittest.TestCase):
    "These test if the defaults are created properly"
    def setUp(self):
        self.t = IntCheck('test', min=1, max = 10)
    def tearDown(self):
        del self.t

    #~ valid input tests
    def testPassWithInt(self):
        "IntCheck() accepts in-bounds integer"
        self.failUnless(self.t( 9))

    def testPassWithValidString(self):
        "IntCheck() accepts integer-equivalent string"
        self.failUnless(self.t( '6'))

    def testPassWithValidFloat(self):
        "IntCheck() accepts with integer-equivalent float"
        self.failUnless(self.t( 6.0 ) )

    def testPassWithElement(self):
        "IntCheck() accepts valid element.text"
        self.failUnless(self.t(ET.fromstring('<test>4</test>')))

    def testPassWithXML(self):
        "IntCheck() accepts valid xml strings"
        self.failUnless(self.t('<test>4</test>'))

    #~ bad input tests
    def testFailWithEmptyString(self):
        "IntCheck() raises ValueError when passed an empty string when required"
        self.assertRaises(ValueError, self.t, '')

    def testFailWithOOBInt(self):
        "IntCheck() fails with out-of-bounds integer"
        self.assertRaises(self.t.error, self.t, -4)

    def testFailWithFloat(self):
        "IntCheck() raises TypeError when passed with non-integral float"
        self.assertRaises(TypeError, self.t, 5.6)

    def testFailWithOOBString(self):
        "IntCheck() fails with out-of-bounds integral string"
        self.assertRaises(self.t.error, self.t, '45')

    def testFailWithFloatString(self):
        "IntCheck() fails wehn passed float-equivalent string"
        self.assertRaises(ValueError, self.t, '5.6')

    def testFailWithFloatElem(self):
        "IntCheck() raises ValueError with element.text as non-integral float"
        self.assertRaises(ValueError, self.t, ET.fromstring('<test>5.5</test>') )

    def testFailWithFloatElemString(self):
        "IntCheck() fails with xml-formatting string as non integral float"
        self.assertRaises(ValueError, self.t, '<test>5.4</test>')

    def testFailWithOOBElement(self):
        "IntCheck() fails with element.text as out-of-bounds integer"
        self.assertRaises(self.t.error, self.t, ET.fromstring('<test>99</test>'))

    def testFailWithOOBElementString(self):
        "IntCheck() fails with xml-formattet sting with out of bounds integer"
        self.assertRaises(self.t.error, self.t, '<test>99</test>')

    def testFailWithNonInteger(self):
        "IntCheck() fails with a non-integer"
        self.assertRaises(ValueError, self.t, 'a')

class SelectionCheckTC(unittest.TestCase):
    def setUp(self):
        self.s = SelectionCheck('choice', values=['alpha','beta','gamma'])

    def tearDown(self):
        del self.s

    def testDefaultAttributes(self):
        "SelectionCheck creates appropriate default attrubutes"
        self.assertTrue(self.s.ignoreCase, "ignoreCase not True")
    
    def testCustomAttributes(self):
        "SelectionCheck customizes attributes"
        s = SelectionCheck('choice', values=['a', 'b'], ignoreCase = False)
        self.assertFalse(s.ignoreCase, "ignoreCase not customized")
        
    def testFailWithoutValues(self):
        "SelectionCheck raises NoSelectionError if not given any values"
        self.assertRaises(NoSelectionError, SelectionCheck, 'choices')

    def testFailWithEmptyListForValues(self):
        "SelectionCheck raises NoSelectionError if values is an empty list"
        self.assertRaises(NoSelectionError, SelectionCheck, 'choices', values = [])

    def testFailWithNonListForValues(self):
        "SelectionCheck() raises BadSelectionsError if values is not iterable"
        self.assertRaises(BadSelectionsError, SelectionCheck, 'choices', values=None)

    def testFailWithNonCaseSensitiveChoice(self):
        "SelectionCheck() fails if case doesn't match and ignoreCase is False"
        self.s.ignoreCase = False
        self.assertRaises(self.s.error, self.s, 'Alpha')

    def testPassWithNonCaseSensitiveChoice(self):
        "SelectionCheck() accepts value in list without case match and caseSensitive is False"
        self.s.ignoreCase = True
        self.failUnless(self.s('Alpha'))

    def testPassWithElementText(self):
        "SelectionCheck() accepts appropriate xml-formmated text"
        self.failUnless(self.s('<choice>alpha</choice>'))

    def testPassWithElement(self):
        "SelectionCheck() accepts appropriate element.text"
        self.failUnless(self.s(ET.fromstring('<choice>alpha</choice>')))

    def testFailWithOutOfListValue(self):
        "SelectionCheck() fails if value not in list of acceptable values"
        self.assertRaises(self.s.error, self.s, 'delta')

class BoolCheckTC(unittest.TestCase):
    def setUp(self):
        self.b = BoolCheck('flag')

    def tearDown(self):
        del self.b

    def testPassWithBoolean(self):
        "BoolCheck() accepts True or False types"
        self.failUnless(self.b(True))
        self.failUnless(self.b(False))

    def testPassWithBooleanString(self):
        "BoolCheck() accepts boolean-equivalent strings"
        self.failUnless(self.b('True'))
        self.failUnless(self.b('False'))

    def testPassWithLowerCaseBoolanString(self):
        "BoolCheck() accepts boolean-equivalent strings despite capitalization"
        for x in ['true', 'TRUE', 'false', 'FALSE']:
            self.failUnless(self.b( x))

    def testPassWithYesNoAnyCase(self):
        "BoolCheck() accepts yes and no variants"
        for x in ['yes', 'YES', 'y', 'Y', 'no', 'NO', 'n', 'N']:
            self.failUnless(self.b(x))

    def testPassWithNoneAsFalse(self):
        "BoolCheck() accepts NoneType if noneIsFalse is True"
        self.b.noneIsFalse=True
        self.failUnless(self.b(None))

    def testFailWithoutNoneAnFalse(self):
        "BoolCheck() fails if NoneType and noneIsFalse is False"
        self.b.noneIsFalse = False
        self.assertRaises(self.b.error, self.b, None)

    def testPassWithNoneAsFalseAndNoneString(self):
        "BoolCheck() accepts 'None' if noneIsFalse is True"
        self.b.noneIsFalse = True
        self.failUnless(self.b('None'))

    def testFailWithoutNoneAsFalseandNoneString(self):
        "BoolCheck() fails with 'none' if noneIsFalse is False"
        self.b.noneIsFalse = False
        self.assertRaises(self.b.error, self.b, 'none')

    def testPassWithValidString(self):
        "BoolCheck() accepts a variety of positive and negative strings"
        for x in ['true','yes','1','t','y','false','no','0','f','n']:
            self.failUnless(self.b(x))
            self.failUnless(self.b(x.upper()))
            self.failUnless(self.b(x.title()))

    def testPassWithXMLText(self):
        "BoolCheck() accepts xml-formatting string"
        for x in ['true','yes','1','t','y','false','no','0','f','n']:
            self.failUnless(self.b('<flag>%s</flag>' % x))

    def testPassWithElement(self):
        "BoolCheck() accepts xml-formatting string"
        for x in ['true','yes','1','t','y','false','no','0','f','n']:
            self.failUnless(self.b(ET.fromstring('<flag>%s</flag>' % x) ) )

    def testNormalizedValues(self):
        "Boolcheck() returns the correct normalized value"
        for x in ['true','yes','1','t','y']:
            self.assertTrue(self.b(x, _normalize=True))
        for x in ['false','no','0','f','n']:
            self.assertFalse(self.b(x, _normalize=True))

class ListCheckTC(unittest.TestCase):
    "random doc string"
    def setUp(self):
        self.l = ListCheck('letter', values=['alpha','gamma','delta'])

    def tearDown(self):
        del self.l

    def testSingleValidString(self):
        "ListCheck accepts a valid list of length 1"
        self.failUnless(self.l("alpha"))

    def testFailWithOutOfValueItem(self):
        'ListCheck fails if an item in the list is not in value list'
        self.assertRaises(self.l.error, self.l, "alpha, beta")

    def testFailWithDuplicateItems(self):
        "ListCheck fails with duplicated values and allowDuplicates is False"
        self.l.allowDuplicates = False
        self.assertRaises(self.l.error, self.l, "alpha, alpha")

    def testPassWithDuplicateItems(self):
        "ListCheck accepts duplicates if allowDuplicates is True"
        self.l.allowDuplicates = True
        self.failUnless(self.l('alpha, alpha'))

    def testFailIfTooManyItems(self):
        "ListCheck fails if list has too many items"
        self.l.maxItems = 2
        self.assertRaises(self.l.error, self.l, 'alpha, delta, gamma')

    def testFailIfTooFewItems(self):
        "ListCheck fails if list has too few items"
        self.l.minItems = 2
        self.assertRaises(self.l.error, self.l, 'delta')

    def testFailIfWrongCase(self):
        "ListCheck fails if wrong case and ignoreCase is False"
        self.l.ignoreCase = False
        item ='alpha, gamma, delta'
        self.assertRaises(self.l.error, self.l, item.upper()  )
        self.assertRaises(self.l.error, self.l, item.title() )

    def testPassEvenWithWrongCase(self):
        "ListCheck accpets items if wrong case and ignoreCase is True"
        self.l.ignoreCase = True
        item ='alpha, gamma, delta'
        self.failUnless( self.l(item.upper()) )
        self.failUnless( self.l(item.title()) )

    def testPassWithAlternateDelimiter(self):
        "ListCheck accepts alternate deliminator"
        self.l.delimiter="::"
        self.failUnless(self.l("alpha::gamma:: delta") )
    
    def testPassWithEmptyValues(self):
        "ListCheck() accepts anything if the value list is empty"
        l = ListCheck('anythinggoes', values = [])
        self.failUnless(l("alpha, beta, gamma"), "ListCheck demands values")


class DateTimeCheckTC(unittest.TestCase):
    def setUp(self):
        self.d = DateTimeCheck('date')
    
    def tearDown(self):
        del self.d
    
    def testDefaults(self):
        "DateTimeCheck creates appropriate default values"
        self.assertFalse(self.d.allowNone, "allowNone not False")
        self.assertEqual(self.d.format, "%a %b %d %H:%M:%S %Y", "format not the default")
        self.assertEqual(self.d.formats, [], "formats not an empty list")
    
    def testCustomizedAttributes(self):
        "DateTimeCheck customizes attrbutes"
        d = DateTimeCheck('date', allowNone=True, format="%b-%d-%Y", 
            formats = ['%d-%m-%Y',])
        self.assertTrue(d.allowNone, "allowNone not customized")
        self.assertEqual(d.format, '%b-%d-%Y', 'format not customised')
        self.assertEqual(d.formats, [ '%d-%m-%Y'])
    
    def testDefaultFormat(self):
        "DateTimeCheck() accepts the default datetime"
        self.failUnless(self.d('Mon Oct 26 22:20:43 2009'), "cannot parse default date")
    
    def testCustomFormat(self):
        "DateTimeCheck() accepts a custom format"
        d = DateTimeCheck('test', format="%Y%m%d%H%M%S")
        self.failUnless(d('20090101122042'), 'cannot parse custom date')
    
    def testDateTimeObject(self):
        "DateTimeCheck() returns a datetime.datetime object when requested"
        dt = self.d("Mon Oct 26 14:52:42 2009", _asDateTime=True)
        self.assertTrue(isinstance(dt, datetime.datetime), "Did not return a datetime.datetime object")
    
    def testTimeStructObject(self):
        "DateTimeCheck() returns a time.struct_time object when requested"
        dt = self.d("Mon Oct 26 09:00:00 2009", _asStruct=True)
        self.assertTrue(isinstance(dt, time.struct_time), "Did not return a time.struct_time object")
    
    def testDateOutOfBounds(self):
        "DateTimeCheck() fails if date is out of range"
        d = DateTimeCheck('test', format="%m/%d/%Y", minDateTime = "10/1/2009", maxDateTime = "10/31/2009")
        self.assertRaises(self.d.error, d, "9/30/2009")
    
    def testMonthAndDayOnly(self):
        "DateTimeCheck() accepts month and day only"
        d = DateTimeCheck('mday', format="%b %d", minDateTime="Oct 10", maxDateTime="Oct 20")
        self.failUnless(d('Oct 12'), "Cannot accept month and day only")
        self.assertRaises(d.error, d, 'Oct 9')
        self.assertRaises(d.error, d, 'Nov 1')
    
    def testFormatLists(self):
        "DateTimeCheck() handles a list of formats"
        d = DateTimeCheck('formatlist', formats=['%b %d', '%b %d %Y'])
        self.failUnless(d('Oct 1'), "DateTimeCheck cannot handle the first format")
        self.failUnless(d('Jan 1 2000'), "DateTimeCheck() cannot handle the second format")
        

test.test_support.verbose = True
test.test_support.run_unittest( XCheckTC,
    AttributesTC,
    ChildrenTC,
    TextCheckTC,
    IntCheckTC,
    EmailCheckTC,
    BoolCheckTC,
    SelectionCheckTC,
    ListCheckTC,
    DateTimeCheckTC,
    UnorderedChildrenTC
    )