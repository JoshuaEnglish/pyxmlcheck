"""utils
Utility Fuctions for XCheck

"""

__history__="""
2013-10-05 - Rev 29 - added simple_formatter and debug_formatter for logging
"""

try:
    from elementtree import ElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

#utility functions
def get_bool(item):
    """get_bool(item)
    Return True if item is a Boolean True, 1, Yes, T, or Y
    Return False if item is a False, 0, No, F, or N
    Raises a ValueError if anything else

    get_bool() is case-insensitive.
    get_bool() raises a :py:exc:ValueError if item cannot be parsed.
    """

    if str(item).lower() in ['true','yes','1','t','y']:
        return True
    if str(item).lower() in ['false', 'no', '0', 'f', 'n']:
        return False
    raise ValueError("'%s' cannot be parsed into a boolean value" % item)

def get_elem(elem):
    """Assume an ETree.Element object or a string representation.
    Return the ETree.Element object"""
    if not ET.iselement(elem):
        try:
            elem = ET.fromstring(elem)
        except:
            raise ValueError("Cannot convert to element")

    return elem

def indent(elem, level=0):
    """indent(elem, [level=0])
    Turns an ElementTree.Element into a more human-readable form.

    indent is recursive.
    """
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for e in elem:
            indent(e, level+1)
            if not e.tail or not e.tail.strip():
                e.tail = i + "  "
        if not e.tail or not e.tail.strip():
            e.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
        else:
            elem.tail="\n"

def list_requirements(checker, prefix=None):
    """
    lists the required attributes and children of a checker.
    Returns a list of tuples
    """
    res = []
    prefix = prefix or ()
    for att in checker.attributes.values():
        if att.required:
            res.append(prefix + (att.name,))


    for child in checker.children:
        if child.has_attributes and not child.has_children:
            _prefix = (prefix + (child.name,))
            for att in child.attributes.values():
                res.append(_prefix + (att.name,))
        if child.has_children:
            _prefix = (prefix + (child.name,))
            res.extend(list_requirements(child, _prefix))
        elif child.min_occurs > 0:
            if prefix:
                res.append(prefix + (child.name,))
            else:
                res.append((child.name,))


    return res

def get_minimum_keys(checker):
    res = {}
    count = 0
    for key in checker.get_all_paths():
        idx = 1
        found_one = False
        tokens = key.split('.')[1:]
        while idx <= len(tokens):
            test_key = '.'.join(tokens[-idx:])
            test_path = checker.xpath_to(test_key)
            if test_path:
                res[test_key] = test_path
                found_one = True
                break
            else:
                idx += 1

        if not found_one:
            if tokens:
                res['.'.join(tokens)] = xpath_to(key)
    return res

#-------------------------------------------------------------------------------
# logging help

import logging
simple_formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
_dstr = "%(name)s - %(levelname)s - %(message)s [%(module)s.%(funcName)s:%(lineno)d]"
debug_formatter = logging.Formatter(_dstr)

#-------------------------------------------------------------------------------
# Node Maniplation Tools
def insert_node(checker, parent, child):
    new_check, new_parent = drill_down_to_node(checker, parent, child)
    insert_child_into_node(new_check, new_parent, child)

def drill_down_to_node(checker, parent, child):
    """
    Starting at the parent node, return the node that should contain that
    child node, creating the nodes as needed.

    :param checker: the parent checker
    :type checker: xcheck object
    :param parent: the parent element
    :type parent: Element
    :param child: the child node
    :type child: Element
    """

    xpath = checker.xpath_to(child.tag)
    checker.logger.debug('drilling down to %s', xpath)

    if xpath is None:
        raise checker.error(
            "%sCheck cannot determine proper place for %s" % (checker.name, child.tag))

    if '@' in xpath:
        raise checker.error(
            "%sCheck cannot insert '%s' attribute as a child node" % (checker.name, child.tag))

    this_node = parent
    this_check = checker
    tags = xpath.split('/')
    tags.pop(0)
    while tags:

        this_tag = tags.pop(0)
        checker.logger.debug('looking for %s', this_tag)
        if this_tag == child.tag:
            checker.logger.debug('found what we are looking for')
            break
        acceptable_children = [ch.name for ch in this_check.children]

        #this may never be raised
        if this_tag not in this_check.child_names:
            raise checker.error("Cannot insert %s into %s" % (this_tag, this_check.name))

        known_children = [nd.tag for nd in this_node]
        if this_tag not in known_children:
            checker.logger.debug('Must create %s child', this_tag)
            lvl = this_check.logger.level
            this_check.logger.setLevel(checker.logger.level)
            insert_child_into_node(this_check, this_node, ET.Element(this_tag))
            this_check.logger.setLevel(lvl)



        next_check = this_check.get(this_tag)
        checker.logger.debug('next_check is %s', next_check)
        # bug? Sometimes next_check is not found
        if next_check is None:
            next_check = this_check.get('.%s' % this_tag)
            checker.logger.debug('next_check is %s', next_check)


        next_node = this_node.find(this_tag)

        this_check = next_check
        this_node = next_node

    return (this_check, this_node)

import itertools as I
def insert_child_into_node(checker, parent, child):
    """
    :param checker: XCheck object attached to parent
    :param parent: Element node
    :param child: Element node
    """
    if not checker.name == parent.tag:
        raise checker.error("Checker/Parent mismatch: %s, %s" % (checker, parent))

    checker.logger.debug('Acceptable children: [%s]', ' '.join(checker.child_names))
    if child.tag not in checker.child_names:
        raise checker.error(
            "%sCheck object cannot have %s as child" % (
                checker.name, child.tag))

    known_children = [nd.tag for nd in parent]

    if not known_children:
        checker.logger.debug('No children -- appending')
        parent.append(child)
        return True

    checker.logger.debug('Known children: [%s]', ' '.join(known_children))

    child_check = checker.get(child.tag)
    checker.logger.debug('Need %sCheck, found %s' % (child.tag, child_check))

    if known_children.count(child.tag) >= child_check.max_occurs:
        raise child_check.error("Too many %s children (%d already, no more than %d)" %
            (child.tag, known_children.count(child.tag), child_check.max_occurs))

    child_index = 0
    pre_tag = True
    in_tag = False

    checker.logger.debug('%sCheck acceptable children: [%s]',
        checker.name,
        ' '.join(checker.child_names))

    tags_preceding_child = list(
        I.dropwhile(lambda x: x != child.tag, checker.child_names))
    checker.logger.debug('remaining children: %s', tags_preceding_child)

    tags_after_child = list(
        I.dropwhile(lambda x: x == child.tag, tags_preceding_child))
    checker.logger.debug('remaining children: %s', tags_after_child)


    ins = None
    for tag_to_find in tags_after_child:
        if tag_to_find in known_children:
            ins = known_children.index(tag_to_find)
            checker.logger.debug('setting ins to %d', ins)
            break
    if ins is None:
        checker.logger.debug('fallback - appending child')
        parent.append(child)
        return True

    parent.insert(ins, child)
    return True

def get_value(checker, elem, tag, nth=0, normalize=True, **kwargs):
    xpath = checker.xpath_to(tag)
    check = checker.get(tag)
    child = elem.find(xpath)
    if child is None:
        return None

    if checker.is_att(tag):
        xpath = xpath[:xpath.find('[')]
        child = elem.find(xpath)
        return check(child.get(tag.split('.')[-1]), normalize=normalize, **kwargs)
    else:
        return check(child.text, normalize=normalize, **kwargs)

def set_value(checker, elem, tag, value, nth=0):
    xpath = checker.xpath_to(tag)
    check = checker.get(tag)
    dotted = checker.dotted_path_to(tag)

    # If the child was created by an earlier call, it has no attributes
    # so look for the child node without regard to attributes
    if checker.is_att(tag):
        child = elem.find(checker.xpath_to(dotted.split('.')[-2]))
    else:
        child = elem.find(xpath)

    if child is None:
        if checker.is_att(tag):
            child = ET.Element(dotted.split('.')[-2])
            checker.insert_node(elem, child)
        else:
            child = ET.Element(dotted.split('.')[-1])
            checker.insert_node(elem, child)

    val = check(value, normalize=True, as_string=True)
    if checker.is_att(tag):
        child.set(check.name, val)
    else:
        child.text = val


if __name__=='__main__':
    from loader import load_checker
    from core import check_node
    story = load_checker("""<xcheck name="story">
    <attributes>
        <text name="code" required="true"/>
        <decimal name="revision" required="false"/>
    </attributes>
    <children>
        <text name="title" />
        <text name="pasttitle" min_occurs="0" max_occurs="99"/>
        <int name="wordcount" />
        <selection name="status"
            values="treatment, draft, critique, on_market, sold, reprint, retired" />
        <list name="genres" min_occurs="0"
            values="sf, fantasy, horror, lit, punk, realism"/>
        <list name="keywords" min_occurs="0"/>
        <text name="file" min_occurs="0"/>
        <xcheck name="history" min_occurs="0">
            <text name="item" min_occurs="0" max_occurs="99">
                <attributes>
                    <datetime name="date"/>
                </attributes>
            </text>
        </xcheck>
        <text name="plot" min_occurs="0" />
    </children>
</xcheck>
""")
    print story
    charlie = ET.fromstring("""<story code="charlie" >
    <title>Uncle Charlie Goes Swimming</title>
    <wordcount>5000</wordcount>
    <status>draft</status>
    <genres>fantasy</genres>
  </story>"""
  )
    h = logging.StreamHandler()
    h.setFormatter(debug_formatter)
    logging.getLogger().addHandler(h)
##    logging.getLogger().setLevel(logging.DEBUG)
##    for error in check_node(story, charlie):
##        print error
##    print '--'
    print story(charlie)
    for dotted in ['code', 'title','wordcount', 'genres']:
        val = get_value(story, charlie, dotted, as_string=True)
        print dotted, val, type(val)
