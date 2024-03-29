import operator

from core import XCheckError, XCheck
from boolcheck import BoolCheck
from infinity import INF, NINF

class NoSelectionError(XCheckError):
    """SelectionCheck was not given a value to check"""
class BadSelectionsError(XCheckError):
    """SelectionCheck was passed non-iterable as whitelist"""


    """IntCheck(name[, min, max])

    IntCheck checks attributes and elements containing integer data.

    :param name: name of the xml tag
    :type name: string
    :param min: minimum value for the checker
    :type min: integer or NINF
    :param max: maximum value for the checker
    :type max: integer or INF

    The max and min attributes are inclusive, they default to NINF and INF,
    respectively.
    """

class SelectionCheck(XCheck):
    """SelectionCheck(name, **kwargs)

    SelectionCheck checks against a set number of string values

    :param iterable values: list of string objects
    :param func callback: function to call to get values
    :param bool ignore_case: allows value to match upper or lower case
    :param bool allow_none: allows no selection value

    If a callback is specified, it will always be used over a static values
    list.
    """
    _boolCheck = BoolCheck('caseSensitive')
    def __init__(self, name, **kwargs):
        if 'values' not in kwargs and 'callback' not in kwargs:
            raise NoSelectionError("Selection check must have iterable values or a callback function")

        self.callback = kwargs.pop('callback', None)
        self.use_callback = True if self.callback is not None else False

        self.allow_none = kwargs.pop('allow_none', False)
        self.required = kwargs.get('required', True)
        if not self.required:
            self.allow_none = True

        try:
            self._values = list(kwargs.pop('values', []))
        except:
            raise BadSelectionsError("Selection must be iterable")

        self._values = [val for val in self._values if val]

        self.ignore_case = self._boolCheck(kwargs.pop('ignore_case', True),
            normalize=True)

        XCheck.__init__(self, name, **kwargs)
        self._object_atts.extend(['ignore_case', 'values',
            'use_callback', 'allow_none'])

        if not self.use_callback and not self.values:
            raise NoSelectionError("must have values for selection test")

        for v in self._values:
            if not isinstance(v, basestring):
                raise BadSelectionsError("value %s is not string type" % v)

    @property
    def values(self):
        if self.callback:
            return self.callback()
        else:
            return self._values

    @values.setter
    def values(self, value_list):
        self.logger.debug('setting values list for SelectionCheck')
        self._values = list(value_list)


    def __call__(self, item, **kwargs):
        self.logger.debug('__call__ %s with %s (allow_none is %s)',
             self.name, item, self.allow_none)
        if item is None and self.allow_none:
            return True

        return XCheck.__call__(self, item, **kwargs)

    def check_content(self, item):
        ok = None
        self.logger.debug('%s: item is %s', self.name, item)
        if item is None and self.allow_none:
            return True

        item = str(item)
        if self.callback:
            vals = self.callback()
        else:
            vals = list(self.values)


        self.normalize_content(item)
        if self.ignore_case:
            item = item.lower()
            vals = map(str.lower, vals)
        if item not in vals:
            ok = False
            raise self.error(
                "Selection %s not in list of available values" % item)
        else:
            ok = True
        return ok

    def dummy_value(self):
        return self.values[0]

strip = operator.methodcaller('strip')
lower = operator.methodcaller('lower')
upper = operator.methodcaller('upper')
title = operator.methodcaller('title')

class ListCheck(XCheck):
    """ListCheck(name, **kwargs)
    List Check accepts a string that is formatted as a list

    :param str delimiter: The separator between items
    :param list values: A list of acceptable values. If None or an empty list,
                        any value is acceptable
    :param func callback: A function that can be called dynamically to get
                          acceptable members of the list.
    :param bool allow_duplicates: If True, items can appear more than once
                                  in the list. If false, items can only appear
                                  once.
    :param int min_items: The minimum number of items allowed in the list.
                          Default 0.
    :param int max_items: The maximum number if items allowed in the list.
                          Default INF.
    :param bool ignore_case: If True, check is not case-sensitive.
                             Default False.

    In the call:
    _normalize = True returns a python list [default]
    as_string -- returns a string representation

    """
    _boolCheck = BoolCheck('ignore_case')
    def __init__(self, name, **kwargs):

        self.delimiter = kwargs.pop('delimiter', ',')
        try:
            self._values = list(kwargs.pop('values', []))
        except:
            raise BadSelectionsError('List values must be iterable')

        self.callback = kwargs.pop('callback', None)

        self.allow_duplicates = kwargs.pop('allow_duplicates', False)
        self.min_items = int(kwargs.pop('min_items', 0) )
        self.max_items = int(kwargs.pop('max_items', -1) )
        self.ignore_case = self._boolCheck(
            kwargs.pop('ignore_case', False),
            normalize=True)

        if self.max_items in [ -1, INF]:
            self.max_items = INF

        self.as_string = self._boolCheck(
            kwargs.pop('as_string', False),
            normalize=True)

        XCheck.__init__(self, name, **kwargs)
        self._object_atts.extend(['delimiter', 'values', 'allow_duplicates',
            'min_items', 'max_items', 'ignore_case', 'as_string'])

    @property
    def values(self):
        if self.callback:
            return self.callback()
        else:
            return self._values

    @values.setter
    def values(self, values_list):
        self.logger.debug('changing ListCheck values')
        self._values = list(values_list)

    def normalize_content(self, items):
        "normalizes the content of the list"
        self._normalized_value = map(strip, items)
        if self.as_string:
            delim = "%s " % self.delimiter
            self._normalized_value = delim.join(self._normalized_value)



    def check_content(self, item):
        "determines if items in list are valid"
        ok = True
        if item is None:
            item = ''
        if isinstance(item, (list, tuple)):
            item = self.delimiter.join(item)
        items = item.split(self.delimiter)
        items = map(strip, items)
        items = filter(bool, items)
        if self.min_items > len(items):
            ok = False
            raise self.error, "not enough items in the list"
        if self.max_items < len(items):
            ok = False
            raise self.error, "too many items in the list"
        if self.ignore_case:
            vals = map(str.lower, self.values)
            items = map(str.lower, items)
        else:
            if self.callback:
                vals = self.callback()
            else:
                vals = list(self.values)

        if vals != []:
            for item in items:
                ok &= item in vals
                if item not in vals:
                    raise self.error, "Item %s not in values list(%s)" % \
                        (item, self.name)
                if not self.allow_duplicates:
                    try:
                        vals.remove(item)
                    except ValueError:
                        raise self.error, "Item %s not in values list" % item

        if not ok:
            raise self.error, "sommat got borked"
        self.normalize_content(items)
        return ok

    def __call__(self, item, **kwargs):
        self.as_string = kwargs.pop('as_string', False)
        if self.as_string:
            kwargs['normalize'] = True
        return XCheck.__call__(self, item, **kwargs)

    def dummy_value(self):
        if self.values:
            return self.delimiter.join(self.values[:self.min_items])
        else:
            from string import lowercase
            return self.delimiter.join(lowercase[:self.min_items])

import unittest
from core import ET

class SelectionCheckTC(unittest.TestCase):
    def setUp(self):
        self.s = SelectionCheck('choice', values=['alpha','beta','gamma'])

    def tearDown(self):
        del self.s

    def testDefaultAttributes(self):
        "SelectionCheck creates appropriate default attrubutes"
        self.assertTrue(self.s.ignore_case, "ignore_case not True")

    def testCustomAttributes(self):
        "SelectionCheck customizes attributes"
        s = SelectionCheck('choice', values=['a', 'b'], ignore_case = False)
        self.assertFalse(s.ignore_case, "ignore_case not customized")

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
        "SelectionCheck() fails if case doesn't match and ignore_case is False"
        self.s.ignore_case = False
        self.assertRaises(self.s.error, self.s, 'Alpha')

    def testPassWithNonCaseSensitiveChoice(self):
        "SelectionCheck() accepts value in list without case match and caseSensitive is False"
        self.s.ignore_case = True
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

class SelectionCallbackTC(unittest.TestCase):
    delta_ok = False

    def getValues(self):
        if self.delta_ok:
            return['alpha', 'beta', 'gamma', 'delta']
        else:
            return ['alpha', 'beta', 'gamma']

    def setUp(self):

        self.s = SelectionCheck('choice', callback=self.getValues)

    def tearDown(self):
        del self.s

    def testPassWithCallback(self):
        self.failUnless(self.s('alpha'))

    def testFailWithCallback(self):
        self.assertRaises(self.s.error, self.s, 'delta')

    def testDynamic(self):
        self.delta_ok = False
        self.assertRaises(self.s.error, self.s, 'delta')
        self.delta_ok = True
        self.failUnless(self.s, 'delta')
        self.delta_ok = False

class ListCallbackTC(unittest.TestCase):
    delta_ok = False

    def getValues(self):
        if self.delta_ok:
            return ['alpha', 'beta', 'gamma', 'delta']
        else:
            return ['alpha', 'beta', 'gamma']

    def setUp(self):
        self.l = ListCheck('letter', callback=self.getValues)
    def tearDown(self):
        del self.l

    def testPassWithCallback(self):
        self.failUnless(self.l('alpha'))

    def testFailWithCallback(self):
        self.assertRaises(self.l.error, self.l, 'delta')

    def testDynamic(self):
        self.delta_ok = False
        self.assertRaises(self.l.error, self.l, 'delta')
        self.delta_ok = True
        self.failUnless(self.l, 'delta')
        self.delta_ok = False

class ListCheckTC(unittest.TestCase):
    "random doc string"
    def setUp(self):
        self.l = ListCheck('letter', values=['alpha','gamma','delta'])

    def tearDown(self):
        self.l.logger.setLevel(logging.WARNING)
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
        self.l.allow_duplicates = True
        self.failUnless(self.l('alpha, alpha'))

    def testFailIfTooManyItems(self):
        "ListCheck fails if list has too many items"
        self.l.max_items = 2
        self.assertRaises(self.l.error, self.l, 'alpha, delta, gamma')

    def testFailIfTooFewItems(self):
        "ListCheck fails if list has too few items"
        self.l.min_items = 2
        self.assertRaises(self.l.error, self.l, 'delta')

    def testFailIfWrongCase(self):
        "ListCheck fails if wrong case and ignore_case is False"
        self.l.ignore_case = False
        item ='alpha, gamma, delta'
        self.assertRaises(self.l.error, self.l, item.upper()  )
        self.assertRaises(self.l.error, self.l, item.title() )

    def testPassEvenWithWrongCase(self):
        "ListCheck accpets items if wrong case and ignore_case is True"
        self.l.ignore_case = True
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

    def testAcceptEmptyList(self):
        "ListCheck() accepts an empty list if minitems is 0"
        self.failUnless(self.l('<letter/>'), "ListCheck cannot handle empty list")

    def testNormalizedValue(self):
        self.assertEqual(['alpha', 'gamma'] , self.l("alpha, gamma", normalize=True))

    def testNormalizedList(self):
        self.assertEqual('alpha, gamma', self.l("alpha, gamma", as_string=True) )
        self.assertEqual('alpha, gamma', self.l("<letter>alpha, gamma</letter>", as_string=True))

    def testAcceptsPythonList(self):
        self.assertEqual('alpha, gamma', self.l(['alpha', 'gamma'], as_string=True) )

    def testDummyValue(self):
        self.assertEqual(self.l.dummy_value(), "")
        self.l.min_items = 1
        self.assertEqual(self.l.dummy_value(), "alpha")
        self.l.min_items = 2
        self.assertEqual(self.l.dummy_value(), "alpha,gamma")

    def testDummyValue2(self):
        self.l.values=[]
        self.assertEqual(self.l.dummy_value(), "")
        self.l.min_items = 1
        self.assertEqual(self.l.dummy_value(), "a")
        self.l.min_items = 2
        self.assertEqual(self.l.dummy_value(), "a,b")


class Issue10Test(unittest.TestCase):
    def setUp(self):
        self.ch = XCheck('test')
        self.ch.addattribute(SelectionCheck('value', values=['a', 'b'], required=False))

    def tearDown(self):
        del self.ch

    def testGoodValues(self):
        self.assertTrue(self.ch('<test value="a" />'))
        self.assertTrue(self.ch('<test value="b" />'))

    def testBadValues(self):
        self.assertRaises(self.ch.error, self.ch, "<test value='c' />")

    def testMissing(self):
        self.assertTrue(self.ch('<test />'))

    def testPassingNone(self):

        v = self.ch.get('value')
##        v.logger.setLevel(logging.DEBUG)
        self.assertTrue(v(None))
##        v.logger.setLevel(logging.CRITICAL)

if __name__=='__main__':
    import logging
    logger = logging.getLogger()
    hndl = logging.StreamHandler()
    fmtr = logging.Formatter("%(name)s - %(levelname)s - %(message)s [%(module)s:%(lineno)s]")
    hndl.setFormatter(fmtr)
    logger.addHandler(hndl)
##    logger.setLevel(logging.DEBUG)

    unittest.main(verbosity=1)