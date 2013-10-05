"""
XCheck Core

The main XCheck object, and custome exceptions.

XCheck objects can check xml nodes or xml-text. XCheck objects are designed
to process children nodes, as well, and thus ignore any text.

XCheck is the parent class for all other XCheck objects.


"""

__history__ = """
2013-10-05 - Rev 29 - Integrated logging correctly
"""
import logging
import collections

if hasattr(collections, "OrderedDict"):
    DICT_CLASS = collections.OrderedDict
else:
    DICT_CLASS = dict

try:
    from elementtree import ElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


class XCheckError(Exception):
    "Base module error"

class MismatchedTagError(XCheckError):
    "Tags do not match in checking process"

class UnknownXMLAttributeError(XCheckError):
    "Node has an attribute the checker does not accept"

class XMLAttributeError(XCheckError):
    "Miscellaneous XML attribute error"

class UncheckedXMLAttributeError(XCheckError):
    "a node has a spare attribute"

class MissingChildError(XCheckError):
    "an xml child was expected and not found"

class UnexpectedChildError(XCheckError):
    "A child was found that was not expected"

INIT = 2
logging.addLevelName(INIT, "INIT")


class XCheck(object):
    """XCheck
    Generic validator tool for XML nodes and XML formatted text.
    General Attributes:
        name -- the name used for the XML tag
        min_occurs [default 1] -- the minimum number of times the element
            must appear
        max_occurs [default 1] -- the maximum number of times the element
            can appear
        children -- a list of XCheck objects in expected order
            (XCheck doesn't accept unordered children)
            see add_child for more information

    XML-attribute related attributes:
        unique [default False] -- if the attribute has to be unique (see docs)
        required [default True] -- if the attribute must appear in the element
        attributes -- a dictionary.
            see addattribute for more information

    Miscellaneous Attributes:
        error -- The basic error generated by the checker (see docs)
        check_children [default True] -- the flag that checks children of
            the element
        ordered [default True] -- the flag that determines if the children
            are ordered or not
        helpstr -- a string to describe the purpose of the checker

    Methods (see individual methods for more information):
        add_child -- adds one or more children to the checker
        add_children -- synonym for add_child
        addattribute -- adds one or more attributes to the checker
        addattributes -- synonym for addattribute
        check_content -- method that checks the content of the xml element or
            data. See docs.

    Calling an XCheck object performs the check.
    XCheck objects will accept an element.tree based element, a string of text,
        or a value in the __call__ method.

    Other Methods:
        These methods are not used at runtime, but allow checker objects to
        change ET Elements.

        insert_node(parent, child) -- inserts child into parent in place
        sortDone(parent, childName, sortkey, reverse=False)
            -- sorts children of a node
    """
    def __init__(self, name, **kwargs):

        self.name_ = name    # required (cannot be changed)
        self.logger = logging.getLogger("%sCheck" % name)
        self.logger.log(INIT, "Creating %sCheck", name)
        self.min_occurs = int(kwargs.pop('min_occurs',1))  # number of times the element
        self.max_occurs = int(kwargs.pop('max_occurs',1)) # can appear in the parent (if any)
        self.logger.log(INIT, "Set min and max occur values %d and %d",
                        self.min_occurs, self.max_occurs)
        self.children = []

        #XML attribute related
        self.unique = False
        self.required = True
        self.attributes = DICT_CLASS()

        #Miscellaneous attributes
        self.error = XCheckError
##        if self.__class__._name___=="XCheck":
        self.check_children = True
        self.ordered = True
        self.helpstr = kwargs.pop('help', '')

        # Safely populate the attributes
        self.logger.log(INIT, "Creating attributes")
        for key, val in kwargs.pop('attributes', {}).items():
            if not isinstance(val, XCheck):
                raise XMLAttributeError('Invalid attribute checker %s' % val)
            if key != val.name:
                raise XMLAttributeError('att key and check name different')
            self._addattribute(val)

        # Safely populate children
        self.logger.log(INIT, "Creating Children...")
        for child in kwargs.pop('children', []):
            self._add_child(child)
        self.__dict__.update(**kwargs)
        #~ if  self.required is False:
            #~ self.min_occurs = 0

        # _object_atts is a list of all attributes to be copied
        # during a call to self._rename (0.4.1)
        self._object_atts = ['min_occurs', 'max_occurs', 'children', 'unique',
            'required', 'attributes', 'error', 'helpstr']
        if self.__class__.__name__ == "XCheck":
            self._object_atts.extend(['check_children', 'ordered'])


    # DEV
    def is_att(self, tag):
        """returns true if the given tag is an attribute"""
        return tag in self.tokens() and tag not in self.tagnames()

    #0.6.5 cut to_dict and from_dict to avoid recursive imports
    # new 0.5.0
    def to_dict(self, node):
        """creates a dictionary representing the node"""
        self.logger.debug("Converting to dictionary")
        return node_to_dict(node, self)

    def from_dict(self, dict_):
        """creates a node from a dictionary"""
        self.logger.debug("Converting from dictionary")
        return dict_to_node(dict_, self)

    # new 0.4.8
    def set_help_string(self, text):
        """sets the help string for the checker"""
        self.helpstr = str(text)

    # new 0.4.8
    def get_help_string(self):
        """returns the help string for the checker"""
        return self.helpstr

    @property
    def help(self):
        """returns the checker's help string"""
        return self.helpstr

    # new 0.4.2
    def tokens(self, children_only = False):
        """XCheck.tokens([children_only = False]):
        Returns a list of the names of the checker and all children and
        attributes.
        If children_only is true, no attributes are included.
        """
        res = [self.name]
        if not children_only:
            res.extend(self.attributes.keys() )
        for child in self.children:
            res.extend(child.tokens(children_only) )
        return res

    def tagnames(self):
        """XCheck.tagnames()
        Shortcut method for XCheck.tokens(True)
        """
        return self.tokens(children_only = True)

    # new 0.4.2
    def _rename(self, newname):
        """returns a copy of the checker with a new name"""
        att_dict = DICT_CLASS()
        for key in self._object_atts:
            att_dict[key] = getattr(self, key)

        return self.__class__(newname,  **att_dict)

    @property
    def name(self):
        """returns the name of the checker, the expected XML tag"""
        return self.name_

    @property
    def has_children(self):
        """returns True if the checker expects child nodes, otherwise False"""
        return not self.children == []

    @property
    def has_attributes(self):
        """returns True if the checker expects attributes, otherwise False"""
        return not self.attributes == {}

    # 3/3/2012
    def has_attribute(self, name):
        """returns True if the checker has a specific attribute"""
        return name in self.attributes

    # 3/3/2012
    def has_child(self, name):
        """returns True if the checker expects a specific child node"""
        return name in [ch.name for ch in self.children]

    def __repr__(self):
        return "<%sCheck object at 0x%x>" % (self.name, id(self))

#todo: change get to allow for a . notation
#so attribute checkers could have the same name
    def get(self, name):
        """get(name)
        Returns an attribute or child checker object.
        """
        res = None
        if name in self.attributes:
            return self.attributes[name]
        else:
            if name == self.name:
                return self
            else:
                for child in self.children:
                    res = child.get(name)
                    if res is not None:
                        break
        return res

    def dict_key(self, name):
        """dict_key(name)

        Returns a key for the tag, either as a child or attribute.

        """
        pth, att = self.path_to(name)
        if pth == '.':
            pth = self.name
        if att:
            return "%s.%s" % (pth, att)
        else:
            return pth

    def path_to(self, name, level = 0):
        """path_to(name, [level=0])

        Returns an XMLPath and attribute to the tag
        This is a pair, not an actual string. (use xpath_to for the string)
        The level attribute is used internally.

        """
        res = None
        if name in self.attributes:
            return ("." if level==0 else self.name, name)
        else:
            if name == self.name:
                return ('.' if level==0 else self.name, None)
            else:
                for child in self.children:
                    res = child.path_to(name, level = level+1)
                    if res is not None:
                        a, b = res
                        if level > 0:
                            a = ".//%s" % ( a)
                        res = (a, b)
                        break


        return res

    def xpath_to(self, name):
        """Returns a formatted xpath string"""
        nm, at = self.path_to(name)
        if at is None:
            return nm
        else:
            return "%s[@%s]" % (nm, at)

    def _add_child(self, child):
        """adds a child checker to the expected children list"""
        if not isinstance(child, XCheck):
            raise self.error, "Cannot use %s as child checker" % child
        self.children.append(child)
        self.logger.log(INIT, "Adding child %s", child.name)

    def add_child(self, *children):
        """add_child(*children) [also add_children]
        add a list of child objects to the expected children
        raises an error if any child object is not an instance of
          an XCheck class
        If passing a list, unpack it:
        >>>x = XCheck('test')
        >>>kids = [XCheck('a'), XCheck('b'), XCheck('c')]
        >>>x.add_children(*kids)
        """
        for child in children:
            self._add_child(child)

    add_children = add_child

    def _addattribute(self, att):
        """adds an attribute to the checker"""
        if not isinstance(att, XCheck):
            raise XMLAttributeError("Cannot use %s as attribute checker" % att)
        if att.name in self.attributes:
            raise XMLAttributeError("Cannot replace known attribute")
        self.attributes[att.name] = att
        self.logger.log(INIT,"Setting attribute %s", att.name)

    def addattribute(self, *atts):
        """addattribute(*atts) [also addattributes]
        add an attribute checker to the element
        Raises an error if any attribute is not an instance of
            an XCheck class
        If passing a list, unpack it:
        >>>x = XCheck('test')
        >>>atts = [XCheck('a'), XCheck('b')]
        >>>x.addattributes(*atts)
        """
        for att in atts:
            self._addattribute(att)

    addattributes = addattribute
    add_addtribute = addattribute
    add_addtributes = addattribute

    def check_content(self, item):
        """check_content(item) -> Bool
        This is the method to customize for your own checker.
        Return True if all is good, raise an error otherwise
        """
        #
##        raise XCheckError("Do not check simple content with XCheck")
        self.logger.debug('checking content %s', item)
        self.normalize_content(item)
        return True

    def normalize_content(self, item):
        """normalize_content(item)
        This is the method used to normalize the return value.
        normalization is optional
        """
        self.logger.debug('setting normalized_value')
        self._normalized_value = item


    # 5-17-2012 -- way to normalize without checking
    def normalize(self, item, as_string=False):
        """normalize(item, as_string)
        Normalize the item according to the checker's rules, but
        does not check the item.

        :param: as_string -- returns a string representation
        """
        self.normalize_content(item)
        if as_string:
            self.logger.debug('... converting normalized value to string')
            return str(self._normalized_value)

        return self._normalized_value


    def __call__(self, arg, check_children=None,
                 normalize=False, verbose=False,
                 as_string = False):
        # Temporarily override the check_children attribute
        self.logger.debug("checking %s", arg)
        self.logger.debug("  normalize: %d", normalize)
        self.logger.debug("  as_string: %d", as_string)
        _cc = None
        #self._normalizedResult = None
        if check_children is not None:
            _cc = self.check_children
            self.check_children = check_children

        # Create an element if possible
        elem = None
        if ET.iselement(arg):
            self.logger.debug("checking an Element")
            elem = arg

        if elem is None:
            try:
                self.logger.debug('converting to Element')
                elem = ET.fromstring(arg)
                arg = elem.text
                self.logger.debug("element: %s" % ET.fromstring(elem))
            except:
                self.logger.debug("could not convert %s", elem)
                pass

        # validate element if appropriate
        if elem is not None:
            self.logger.debug(' validating element')
            ok = elem.tag == self.name
            if not ok:
                text = "Element tag does not match check name"
                raise MismatchedTagError(text)
            content = elem.text
            if content:
                ok &= self.check_content(content.strip())
            #~ Check the attributes
            atts = dict(self.attributes) # create a copy to play with
            self.logger.debug('checking attributes: %s', atts)

            for key, val in elem.items():
                ch = atts.pop(key, None)
                #! element has attribute that the checker doesn't know about
                if ch is None:
                    self.logger.error("Unknown Attrbute: %s", key)
                    raise UnknownXMLAttributeError(key)
                #~ check the attribute with the checker
                self.logger.debug('checking attribute %s with %s', ch.name, val)


                # Work around the strangeness of DateTimeCheck (0.4.1)
                if isinstance(ch, DatetimeCheck):
                    ok &= ch(val, as_string=False)
                else:
                    ok &= ch(val)

            #~ check for leftover required attributes
            for att in atts.values():
                self.logger.error('Leftover attribute %s', att.name)
                if att.required:

                    text = "missing required attribute (%s)" % att.name
                    self.logger.error(text)
                    raise UncheckedXMLAttributeError(text)


            if self.check_children:
                if self.ordered:
                    self.logger.debug('Checking children in order')
                    if elem.tag == self.name:
                        self.logger.debug('checking %s with %s', elem.text, self.name)
                        self.check_content(elem.text)

                        if self.has_children:
                            self.logger.debug('checking children of %s', self.name)
                            children = iter(self.children)
                            child = children.next()
                            self.logger.debug('setting childe as %s', child.name)
                            count = 0
                            for e in elem:
                                self.logger.debug('current element %s', e.tag)
                                if child.name ==  e.tag:
                                    self.logger.debug('%s matches %s', child.name, e.tag)
                                    child(e, verbose = verbose)
                                    count += 1
                                else:
                                    self.logger.debug("%s doesn't match %s", child.name, e.tag)

                                    while child.name != e.tag:
                                        self.logger.debug("counting number of %s elements", e.tag)
                                        if count < child.min_occurs :
                                            self.logger.error("Not enough %s children (found %d)", child.name, count)
                                            raise MissingChildError(
                                                "Not enough %s children (found %d)" % (child.name, count))
                                        if count > child.max_occurs:
                                            self.logger.error('Too many %s children', child.name)
                                            raise UnexpectedChildError(
                                                "Too many %s children" % child.name)
                                        try:
                                            child = children.next()
                                            self.logger.log(INIT, "setting next child", child.name)
                                            count = 0
                                        except StopIteration:
                                            text = "what is %s and what is it doing here?" % child.name
                                            self.logger.error(text)
                                            raise UnexpectedChildError(text)
                                    child(e, verbose=verbose)
                                    count += 1
                            self.logger.debug('Checking count of %s elements', child.name)

                            if count < child.min_occurs:
                                text ="Not enough %s children" % child.name
                                self.logger.error(text)
                                raise MissingChildError(text)
                            if count > child.max_occurs:
                                text ="Too many %s children" % child.name
                                self.logger.error(text)
                                raise UnexpectedChildError(text)

                            # AFTER CHECKING ALL ELEMENTS
                            while True:
                                self.logger.debug('looking for leftover required children')
                                try:
                                    child = children.next()
                                    if child.min_occurs > 0:
                                        self.logger.error('Missing %s child', child.name)
                                        raise MissingChildError(
                                            "Missing %s child" % child.name)
                                except StopIteration:
                                    break

                            return True
                        # checker has no children
                        else:
                            if len(elem) > 0:
                                self.logger.error("Found child where non expected")
                                raise UnexpectedChildError(
                                    "Found child where none expected")
                    else:
                        raise MismatchedTagError(
                            "checker and element don't match")
                #~  UNORDERED SEARCHING
                else:
                    #~ print "unordered search"
                    #~ check that all the elements are expected
                    names = [x.name for x in self.children]
                    #~ print names
                    for e in list(elem):
                        #~ print "%s in names" % e.tag, e.tag in names
                        if e.tag not in names:
                            raise UnexpectedChildError(
                                "Unexpected %s element" % e.tag)

                    # assuming that's good, do the checks and counting
                    for child in self.children:
                        count = 0
                        #~ print "checking child", child.name
                        for e in elem.findall(child.name):
                            if verbose:
                                print "checking {0}".format(child.name)
                            child(e, verbose=verbose)
                            count += 1
                        if verbose:
                            print "found {0} {1}".format(count, child.name)
                        if count < child.min_occurs:
                            raise MissingChildError(
                                "Not enough %s children" % child.name)
                        if count > child.max_occurs:
                            raise UnexpectedChildError(
                                "Too many %s children" % child.name)
        else:
            logging.debug(' validating non-element atom')
            ok = self.check_content(arg)

        #~ restore saved check_children value
        if _cc is not None:
            self.check_children = _cc

        if normalize:
            if not hasattr(self, '_normalized_value'):
                raise self.error("%s has no normalized value" % self.name)
            else:
                return self._normalized_value
        else:
            return ok

    def insert_node(self, parent, child):
        """insert_node(parent, child)

        Takes a node and inserts a child node, based on the organiziational
        rules of the checker.

        :param parent, child: ElementTree.Elements to manipulate

        .. warning::

            Only works on first-generation children of the checker!
        """
        if parent.tag != self.name:
            raise self.error(
                "%sCheck cannot insert into node tag %s" % (
                    self.name, parent.tag) )

        known_children = [ch.name for ch in self.children]
        if child.tag not in known_children:
            raise self.error(
                "%sCheck cannot insert %s into node" % (self.name, child.tag))


        parent_children = [ch.tag for ch in parent]
        parent_children.reverse()

        if child.tag in parent_children:
            idx = parent_children.index(child.tag)
            ins = len(parent_children)-idx
            parent.insert(ins, child)
        else:
            idx = known_children.index(child.tag)
            found_tag = None # tag in parent children to anchor the insertion
            while found_tag is None:
                idx += 1
                if idx < len(known_children):
                    tag_to_look_for = known_children[idx]
                    if tag_to_look_for in parent_children:
                        found_tag = tag_to_look_for
                else:
                    found_tag = known_children[-1]
            parent_children.reverse()
            if found_tag in parent_children:
                idx = parent_children.index(found_tag)
            else:
                idx = len(parent_children)

            parent.insert(idx, child)

    def sort_children(self, parent, child_name, sortkey, reverse=False):
        """sort_children(parent, child_name, sortkey, reverse=False)

        Sorts children of a node according to sortkey.

        :param parent: ElementTree.Element
        :param child_name: string
        :param sortkey: passed to a call to sorted
        :param reverse: passet to a call to sorted
        """
        if sortkey is None:
            return None

        children = list(parent.findall(child_name))
        if len(children) == 1:
            return None

        for child in children:
            parent.remove(child)

        for child in sorted(children, key=sortkey, reverse=reverse):
            self.insert_node( parent, child)

    def to_definition_node(self, n=0):
        """to_definition_node([n=0])

        Creates an ElementTree.Element that represents the checker tree,
        not data that can be checked by the checker.

        This is a recursive fuction.
        """
        name_ = self.__class__.__name__.lower().replace('check', '')
        if name_ == 'x':
            name_ = 'xcheck'
        elem = ET.Element(name_)
        elem.set('name', self.name)

        for att in self._object_atts:
            if att in ['children', 'attributes']:
                continue
            if att == 'error':
                elem.set('error', self.error.__name__)
                continue
            val = getattr(self, att)
            if isinstance(val, (list, tuple)):
                if self.has_attribute('delimiter'):
                    delimiter = self.delimiter
                else:
                    delimiter = ', '
                val = delimiter.join(val)

            elem.set(att, str(val ) )

        if self.attributes:
            if not elem.text:
                elem.text = '\n'#+'\t'*(n + 1)

            atts = ET.SubElement(elem, "attributes")
            atts.text = '\n'#+'\t'*(n+2)
            for att in self.attributes:
                # may have to do somethingdifferent with lists like SelectionCheck Values
                atts.append(self.attributes[att].to_definition_node(n+1) )
            atts.tail = '\n' #+ '\t'* (n+1)

            last_child = list(atts)[-1]
            #lastChild.tail = lastChild.tail[:-1]

        if self.children:
            if not elem.text: elem.text = '\n'# + '\t'*(n+1)

            kids = ET.SubElement(elem, "children")
            kids.text = '\n'# + '\t'*(n + 2)
            for kid in self.children:
                kids.append(kid.to_definition_node(n+1) )
            kids.tail = '\n'# + '\t' * n

            last_child = list(kids)[-1]
            #lastChild.tail = lastChild.tail[:-1]

        elem.tail = '\n'# + '\t' * (n + 1)
        return elem


    def dummy_element(self):
        """dummy_element()

        Creates a Element node that should pass the checker itself.

        """
        if self.__class__ != XCheck:
            cls_name = self.__class__.__name__
            text = "cannot create dummy element for %s" % cls_name
            self.logger.error(text)
            raise TypeError(text)

        self.logger.debug('Creating dummy element')
        elem = ET.Element(self.name)
        for key in self.attributes:
            ch = self.attributes[key]
            if ch.required:
                elem.set(key, ch.dummy_value() )

        for child in self.children:
            self.logger.debug("Creating %d %s children", child.min_occurs, child.name)
            for x in range(child.min_occurs):
                if child.__class__.__name__== 'XCheck':
                    kid = child.dummy_element()
                    elem.append(kid)
                else:
                    kid = ET.SubElement(elem, child.name)
                    for key in child.attributes:
                        ch = child.attributes[key]
                        if ch.required:
                            kid.set(key, ch.dummy_value() )
                    kid.text = child.dummy_value()

        return elem

    def dummy_value(self):
        """dummy_value()

        Returns a value that should pass the checker.

        Not applicable to XCheck objects.

        Subclasses should override this method.

        """
        raise NotImplementedError

from dictwrap import *

from datetimecheck import DatetimeCheck
if __name__=='__main__':
    oopslog = logging.getLogger('oopsCheck')
    oopslog.addHandler(logging.StreamHandler())
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s [%(module)s:%(lineno)d]")
    oopslog.handlers[0].setFormatter(formatter)
    oopslog.setLevel(INIT)
    X = XCheck('oops')
    print X
    X('die')