import xcheck


class ComplexError(xcheck.XCheckError): pass

class ComplexCheck(xcheck.XCheck):
    def __init__(self, name, **kwargs):
        self.allow_none = kwargs.pop('allow_none', True)
        if 'error' not in kwargs:
            kwargs['error'] = ComplexError
        xcheck.XCheck.__init__(self, name, **kwargs)

        # extend _object_atts for to_node() to work
        self._object_atts.extend(['allow_none'])

    def __call__(self, item, **kwargs):
        self._as_string = kwargs.pop('as_string', False)
        self._as_complex = kwargs.pop('as_complex', False)
        self._as_tuple = kwargs.pop('as_tuple', False)

        if any((self._as_string, self._as_complex, self._as_tuple)):
            kwargs['normalize'] = True
        else:
            kwargs['normalize'] = False

        return xcheck.XCheck.__call__(self, item, **kwargs)

    def check_content(self, item):
        ok = None
        complex_number = None
        is_none = False

        # handle any acceptable None items
        if item is None or str(item).lower().strip() == 'none':
            if self.allow_none:
                ok = True
                self._normalized_value = "None"
                is_none = True

            else:
                ok = False
                raise self.error("ComplexCheck cannot accept None")

        # handle everything else
        if ok is None:
            try:
                self._value = complex(item)
                self._normalized_value = self.normalize_content()
                ok = True
            except Exception as E:
                ok = False
                raise E

        return ok

    def normalize_content(self):
        if self._as_string:
            return str(self._value)
        elif self._as_complex:
            return self._value
        elif self._as_tuple:
            return (self._value.real, self._value.imag)
        else:
            return self._value # always returns the complex number

ET = xcheck.ET
import unittest

class ComplexCheckTC(unittest.TestCase):
    def setUp(self):
        self.c = ComplexCheck('origin')

    def tearDown(self):
        del self.c

    def test_default(self):
        self.assertTrue(self.c.allow_none)
        self.assertTrue(issubclass(self.c.error, ComplexError))

    def test_acceptable_values(self):
        self.assertTrue(self.c(None))
        self.assertTrue(self.c('none'))
        self.assertTrue(self.c(1))
        self.assertTrue(self.c((1+0j)))
        self.assertTrue(self.c(3j))
        text = '1+2j'
        node_text = '<origin>1+2j</origin>'
        node = ET.fromstring(node_text)
        self.assertTrue(self.c(text))
        self.assertTrue(self.c(node_text))
        self.assertTrue(self.c(node))

    def test_failures(self):
        self.assertRaises(ValueError, self.c, 'not a number')
        self.assertRaises(xcheck.MismatchedTagError, self.c, '<o>1+4j</o>')

        bad_text = '<origin>not a number</origin>'
        bad_node = ET.fromstring(bad_text)

        self.assertRaises(ValueError, self.c, bad_text)
        self.assertRaises(ValueError, self.c, bad_node)


    def test_normalizations(self):
        self.assertIsInstance(self.c(1+2j, as_string=True), basestring)
        self.assertIsInstance(self.c(1+2j, as_complex=True), complex)
        self.assertIsInstance(self.c(1+2j, as_tuple=True), tuple)
        self.assertIsInstance(self.c(1+2j, normalize=True), bool)




if __name__=='__main__':
    unittest.main(verbosity=1)