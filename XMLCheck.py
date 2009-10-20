"""XMLCheck
SAX based validation scheme
"""

__author__ = "Josh English <http://joshua.r.english.googlepages.com/>"

__version__ = "1.2.7"
__history__ ="""
    1.0.0 (Mid 2006)    Wrote bulk of program
    1.0.1 (Nov 16, 2006)    Added custom error feature--instances of XMLChecker can now have
                    their own errors
                    Added check that attributes are unique
        1.0.2 (Jun 15, 2007)    Added ListChecker.  Not comprehensive but it works well enough for now
        1.1.0 (Aug 30, 2007)    Added the Validator
        1.2.0 (Jan 28, 2008)    Added SetUnique,SetRequired,SetMinOccurs,SetMaxOccers,
                                UseAttribute,AddChild to XMLCheck
        1.2.1 (Mar 14, 2008)    XMLCheck.expected_children can be a mix of
                                strings or XMLCheck objects. XMLCheck.AddChild adds the
                                XMLCheck object.
        1.2.2 (May 31, 2008)    Fixed a bug in DateChecker that ignored formats
        1.2.3 (Jun  1, 2008)    Fixed a bug where required=False isn't treated as optional
                                by the SequenceChecker._getPattern
        1.2.4 (Dec 27, 2008) Fixed a bug in XML_Validator._getPattern where the item name failed
        1.2.5 (Jan  8, 2009) Changed DateChecker to accept time using the datetime module
        1.2.6 (Feb 21, 2009) Added itemCheck option to ListChecker
        1.2.7 (2009) Moved infinity plus and infinity minus to their own module and use the decimal module
"""

from xml.sax import make_parser,parse
from xml.sax.handler import ContentHandler

### support class
import datetime

class SimpleLog:
    """SimpleLog(name,maxlevel)
    0 -- No information is reported
    1 -- Some information (usually errors) -- automatically write report
    2 -- More information than 1 (including 1)
    3 -- same, etc.
    """
    def __init__(self,name,maxlevel=0):
        self.name = name
        self.data = []
        self.maxlevel = maxlevel
    
    def log(self,lvl,msg):
        if lvl <= self.maxlevel:
            self.data.append((lvl,datetime.datetime.now().ctime(),msg))
            print self.data[-1]
            if lvl == 1: self.report()
    
    def report(self):
        if self.data:
            print '\n'.join(["%d: (%s) %s" % d for d in self.data])
    
    def __call__(self,lvl,msg):
        self.log(lvl,msg)

try:
    from decimal import Decimal
    Inf = Decimal("Infinity")
    NInf = Decimal("-Infinity")
except:
    from infinity import *
    Inf = InfinityPlus()
    NInf = InfinityMinus()
    del infinity



class XMLCheckError(Exception): pass

### UberClass
class XMLChecker:
    """XMLChecker(name,**kwargs)
        Base class for checkers.  Defines the following default attributes (Default types):
            main (False)
            unique (False)
            required (True)
            minOccurs (1)
            maxOccurs(1)
            expected_children ([])
            expected_attributes ({})
        XMLChecker.__call__(arg) always raises an XMLCheckError, so users should subclass
            XMLChecker or use one of the built-in subclasses
    """
    def __init__(self,name,**kwargs):
        self.name = name
        self.main = False
        self.unique = False       # used in attribute check
        self.required = True      # used in attribute check
        self.minOccurs = 1        # used in element children checks
        self.maxOccurs = 1        # used in element children checks
        self.expected_children = []
        self.expected_attributes = {}
        self.error = XMLCheckError
        
        #update
        self.__dict__.update(kwargs)
        
        #check for proper attribute types
        if self.main != bool(self.main):
            raise XMLCheckError, "given main (%s) not a boolean value" % str(self.main)
        if self.unique != bool(self.unique):
            raise XMLCheckError, "given unique (%s) not a boolean value" % str(self.unique)
        if self.required != bool(self.required):
            raise XMLCheckError, "given required (%s) not a boolean value" % str(self.required)
        if self.minOccurs != int(self.minOccurs):
            raise XMLCheckError, "given minOccurs (%s) not an integer" % str(self.minOccurs)
        #print self.maxOccurs,type(self.maxOccurs)
        if self.maxOccurs != int(self.maxOccurs):
            raise XMLCheckError, "given maxOccurs (%s) not an integer or InfinityPlus" % str(self.maxOccurs)
        if not self.required:
            self.minOccurs = 0
    
    def SetUnique(self,b):
        """SetUnique(bool)
        If true, the value passed to this element must be unique.
        """
        self.unique = bool(b)
    
    def SetRequired(self,r):
        """SetRequired(bool)
        If true. the element or attribute must appear
        """
        self.required(bool(r))
    
    def SetMinOccurs(self,m):
        """SetMinOccurs(int)
        If zero, this acts the same as required=false
        """
        self.minOccurs = int(m)
    
    def SetMaxOccurs(self,m):
        """SetMaxOccurs(int)
        This must be an integer greater than one
        """
        self.maxOccurs = max(1,int(m))
    
    def ismain(self):
        return self.main
    
    def __repr__(self):
        return "%s_Checker (%s)" % (self.name,id(self))
    
    def new(self):
        clone = self.__class__(self.name)
        clone.__dict__.update(self.__dict__)
        return clone
    
    def __call__(self,arg):
        raise XMLCheckError, "Do not call this class by itself."

    def UseAttribute(self,checker):
        if isinstance(checker,XMLChecker):
            self.expected_attributes[checker.name]=checker
        else:
            raise XMLCheckError,"Cannot assign checker as attribute"

    def AddChild(self,checker):
        if isinstance(checker,XMLChecker):
            self.expected_children.append(checker)
        else:
            raise XMLCheckError,"Cannot assign checker as child"



import re

### SuperClasses    
class AnyChecker(XMLChecker):
    """AnyChecker(name,**kwargs)
    This checker simply collects elements.  The validate_xml function will
    accept any child and pass the results to another checker.
    """
    def __init__(self,name,**dwargs):
        self.name = "anything"
        self.rule = 'anything'
        self.found_children = []
        XMLChecker.__init__(self,'anything',**dwargs)

class EmptyChecker(XMLChecker):
    """EmptyChecker(name, **kwargs)
    Checks that the XML element or node has no children, only attrubitues
    """
    def __init__(self,name,**kwargs):
        self.name = name
        self.rule = 'empty'
        XMLChecker.__init__(self,name,**kwargs)
    
    def __call__(self, data=None):
        if data is not None:
            raise self.Error, "EmptyChecker shouldn't have data"

### Simple Classes
class TextChecker(XMLChecker):
    """TextChecker(name,**kwargs)
    The following supplemental arguments are used:
        minlen (default 0) -- the minimum length of the string
        maxlen (default Inf) -- the maximum length of the string
        pattern (default None) -- a regular expression    
    """
    def __init__(self,name,**kwargs):
        
        # set defaults
        self.rule = "text"
        self.minlen = 0
        self.maxlen = Inf
        self.pattern = None
        # run superclass init, overriding settings
        XMLChecker.__init__(self,name,**kwargs)
                
    def __call__(self,data):
        ok = True
        ok &= (len(data) >= self.minlen)
        ok &= (len(data) <= self.maxlen)
        if self.pattern:
            ok &= bool(re.match(self.pattern,data))
        if not ok: raise self.error, "%s failure %s" % (self.name, str(data))
        return True
    
class EmailChecker(TextChecker):
        """EmailChecker(name,)
        Checks emails for valid email address or "None"
        """
        def __init__(self,name,**kwargs):
            self.rule="text"
            self.minlen=5
            self.pattern = r'(None|(.+)@(.+)\.(.+))'
            TextChecker.__init__(self,name,**kwargs)

class DateChecker(XMLChecker):
        """DateChecker(name,format='%b %d, %Y',**kwargs)
        This checker has a format attribute, but ignores everything else
        """
        def __init__(self,name,format=None,**kwargs):
                self.rule="date"
                if format:
                        #print "Found a Format"
                        if type(format)==type([]): self.format = format
                        else:
                                self.format=[format]
                else:
                        #print "Setting default format"
                        self.format=['%b %d, %Y']
                XMLChecker.__init__(self,name,**kwargs)

        def __call__(self,data):
            t = None
            d = data.strip()
            for format in self.format:
                try:
                    t = datetime.datetime.strptime(d,format)
                except:
                    pass
            if not t: 
                raise self.error,"Cannot convert %s to date (%s)" % (d,self.format)
            return True

class IntegerChecker(XMLChecker):
    """IntegerChecker(name,name,**kwawrgs)
    The following supplemental arguments are used:
        min (default NInf)
        max (default Inf)
    """
    def __init__(self,name,**kwargs):
        self.rule = "integer"
        self.min = NInf
        self.max = Inf
        self.deliminator = ','
        XMLChecker.__init__(self,name,**kwargs)
    
    def __call__(self,data):
        #data = data.replace(self.deliminator,'')
        try:
            data = int(data)
        except ValueError, TypeError:
            raise self.error,"Cannot convert %s to integer" % str(data)
        #print self.min,self.max
        ok = True
        ok &= (self.min <= data <= self.max)
        if not ok: raise self.error, "IntegerChecker failure %s" % str(data)
        return True

class DecimalChecker(XMLChecker):
    """DecimalChecker(name,**kwawrgs)
    The following supplemental arguments are used:
        min (default InfinityMinus)
        max (default InfinityPlus)
    """
    def __init__(self,name,**kwargs):
        self.rule = "decimal"
        self.min = NInf
        self.max = Inf
        self.deliminator = ','
        XMLChecker.__init__(self,name,**kwargs)
    
    def __call__(self,data):
        #data = data.replace(self.deliminator,'')
        try:
            data = float(data)
        except ValueError:
            raise self.error, 'Cannot convert to decimal'
        ok = True
        ok &= (self.min <= data <= self.max)
        if not ok: raise self.error, "DecimalChecker failure %s" % str(data)
        return True

class BooleanChecker(XMLChecker):
    """BooleanChecker(name)
    No arguments are supported. It simply tells you if the 
    element data is 'True' or 'False'.
    Also allows 'T','t','1','yes','y','Y' for 'True'.
    Also allows 'F','f','0','no','n','N' for 'False'
    """
    def __init__(self,name,**kwargs):
        self.rule = "boolean"
        XMLChecker.__init__(self,name,**kwargs)
    
    def __call__(self,data):
        data = data.lower().strip()
        if data not in ['t','f','true','false','0','1','y','n','yes','no']:
            raise self.error, "Boolean Checker failure %s" % str(data)
        return True

class EnumerationChecker(XMLChecker):
    """EnumerationChecker(name,**kwargs)
    values is a list that limits which values are acceptable.
    ignorecase (default False), if True, will do just that.
    """
    def __init__(self,name,**kwargs):
        self.rule = "enumeration"
        self.values = []
        self.ignorecase = False
        XMLChecker.__init__(self,name,**kwargs)
        if self.ignorecase:
            self.values = map(str.lower,self.values)
    
    def __call__(self,data):
        data = str(data)
        data = data.strip()
        if self.ignorecase: data = data.lower()
        if data not in self.values:
            raise self.error, "Enumeration Checker failure %s(%s)" % (self.name,data)
        return True
        

### These are more complex types of checkers, these have children
class SequenceChecker(XMLChecker):
    """SequenceChecker(name,**kwargs)
    SequenceCheckers expect children in a certain order, but do not expect
    text.
    Possible arguments:
        expected_children (required list)
        expected_attributes (dictionary)
    """
    def __init__(self,name,**kwargs):
        self.rule = "sequence"
        self.found_children = []
        self.index = 0
        XMLChecker.__init__(self,name,**kwargs)
    
    def __call__(self,pattern,foundlings):
        pattern = r'%s' % ''.join(pattern)
        match = re.match(pattern,''.join(foundlings))
        if not match:
            raise self.error, "Sequence_Checker (%s) didn't like the list of children"% (self.name)
        return True
        
class ListChecker(XMLChecker):
        """ListChecker(name,**kwargs)
        List checkers expect text formatted as a delimited list.
        Possible arguments:
                values (required list) [if empty, any values will be accepted]
                delimiter (',' is the default)
        """
        def __init__(self,name,**kwargs):
                self.rule = "list"
                self.values = []
                self.index = 0
                self.delimiter = ','
                self.minlen = 0
                self.maxlen = Inf
                self.itemCheck = kwargs.pop('itemCheck',None)
                
                XMLChecker.__init__(self,name,**kwargs)
                if self.itemCheck and self.values:
                    raise XMLCheckError, "ListChecker cannot have values and itemCheck"

        def __call__(self,data):
                ### strip each item before checking
                items =  data.split(self.delimiter)
                res = []
                for item in items:
                        i = item.strip()
                        if i: res.append(i)
                if len(res) < self.minlen:
                        raise self.error, "Not enough items in %s" % self.name
                if len(res) > self.maxlen:
                        raise self.error, "Too many items in %s" % self.name
                for item in res:
                        if self.values:
                                if item not in self.values:
                                        raise self.error, "ListChecker (%s) didn't like %s" % (self.name,item)
                        if self.itemCheck:
                            try:
                                self.itemCheck(item)
                            except self.itemCheck.error:
                                raise self.error, "ListChecker (%s) item '%s' failed %s" % (self.name, item, self.itemCheck.name)
                                
                return True
### This is the content handler workhorse

class XML_Validator(ContentHandler):
    def __init__(self,checks,startcheck=None,debug = 0):
        self.checks = checks            # This is a dictionary
        self.check_stack = []        # simple list as stack
        self.unique_tokens = {}        # dictionary to keep track of unique tokens

        self.Log = SimpleLog('xml_validator',debug)
        
        if startcheck:
            self.setExpectations(self.checks[startcheck])
        else:
            mainchecks = filter(XMLChecker.ismain,checks.values())
            if len(mainchecks) < 1:
                self.Log(1,"Error: No Main Elements")
                raise XMLCheckError, "No main elements"
            elif len(mainchecks) > 1:
                self.Log(1,"Error: Too many main elements")
                raise XMLCheckError, "Too many main elements"
            self.setExpectations(mainchecks[0])
        self._ok = True
        self.write = False
        self.buffer = ''
        self.elem_stack = []

    
    def setExpectations(self,checker):
        """setExpectations(checker)
        checker is a XMLCheck object
        """
        
        self.check_stack.append(checker.new())
        self.current_check = self.check_stack[-1]
        self.Log(3, "Setting Expectation %s " % self.current_check.name)

    
    def byeExpectation(self):
        """byeExpectation
        Everything should be done, if no errors have cropped up, we're good.
        """
        last_check = self.check_stack.pop()
        self.Log(3, "Removing Expectation %s" % last_check.name)
        try:
            self.current_check = self.check_stack[-1]
        except IndexError:
            pass
            
        if self.current_check.rule == "anything":
            self.current_check.found_children.append(last_check.name)

    def startElement(self,name,attrs):
        self.Log(4,"looking for '%s', got '%s'." % (self.current_check.name,name))
        self.Log(5,"Stack: %s" % ', '.join(map(str,self.check_stack)))
            
        if self.current_check.name == "anything":
            try:
                self.setExpectations(self.checks[name])
            except:
                raise XMLCheckError, "Unknown tag %s" % name
        else:
            if name != self.current_check.name:
                self.Log(1,"Unexpected Element %s" % (str(name)))
                raise Exception, "Unexpected Element %s" % (str(name))
        
        ### stop to check that the expected attributes are valid
        
        self.Log(4,"Searching for attributes...")
        self.Log(6,str(dir(attrs)))
        for k,v in attrs.items():
            #print k,v
            self.Log(5,"Expected attributes: %s" % self.current_check.expected_attributes)
            if k in self.current_check.expected_attributes:
                self.Log(5,"Checking attribute %s" % k)
                self.current_check.expected_attributes[k](v)
            else:
                self.Log(1,"Unacceptable %s attribute in %s element" % (str(k),str(self.current_check.name)))
                raise self.current_check.expected_attributes[k].error, \
                    "Unacceptable %s attribute in %s element" % (str(k),str(self.current_check.name))
        for n,c in self.current_check.expected_attributes.items():
            if c.required:
                if not attrs.has_key(n):
                    raise self.current_check.expected_attributes[n].error, \
                        "Missing required %s attribute in %s element" % (n,self.current_check.name)
            if c.unique:
                thisname = "%s.%s" % (name,n)
                thisval = attrs.getValue(n)
                if self.unique_tokens.has_key(thisname):    
                    if thisval in self.unique_tokens[thisname]:
                        raise c.error, "%s must be unique" % (thisname)
                    else:
                        self.unique_tokens[thisname].append(thisval)
                else:
                    self.unique_tokens[thisname] = [thisval]
                #print self.unique_tokens
                
        self.Log(4,"...done with  the attributes")
        
        ### so I know the element that is expected is the one we got
        ### Now figure out what to expect next:
        if self.current_check.rule in ['text','date','integer','decimal','boolean','enumeration','list']:
            #print "expecting %s" % self.current_check.rule
            self.write = True
            self.buffer = ''
        
        if self.current_check.rule == 'sequence':
            self.Log(4,"expecting a sequence")
            self.Log(5,str(self.current_check))
            kids = self.current_check.expected_children
            self.Log(6,str(kids))
            i = self.current_check.index
            #next = self.checks[kids[i]]
            self.Log(5,"moving on to %s" % kids[i])
            #self.setExpectations(next)
            self.setExpectations(AnyChecker('anything',stopat = self.current_check.name))
            
            
    def endElement(self,name):
        #print "Here ends %s" % name
        ### So current_check.rule tells us what to expect.
        if self.current_check.rule in ['text','date','integer','decimal','boolean','enumeration','list']:
            ### validate the text in the buffer
            self.Log(4,"validating %s..." % self.current_check.name)
            self.Log(6,"%s is %s" % (self.current_check.name,self.buffer.strip()))
            self.current_check(self.buffer)  ## Raises errors if necessary
            self.write = False
            self.byeExpectation()

        elif self.current_check.rule == 'anything':
            #print "Ending anything"
            #print self.check_stack    
            last_checker = self.check_stack.pop()
            self.current_check = self.check_stack[-1]
            #print last_checker.found_children
            ### must call _getPattern to chance the expected_children to
            ### something appropriate for reqular expressions
            ### It requires knowledge of other checkers, hence must be called
            ### here and not part of the SequenceChecker
            self.current_check(self._getPattern(self.current_check.expected_children),last_checker.found_children)
            self.byeExpectation()
            ## Added to debug 10/15
        elif self.current_check.rule == 'empty':
            self.byeExpectation()    

    
    def _getPattern(self,stuff):
        pattern = []
        self.Log(5,"Searcing for proper order of things")
        for item in stuff:
            #print item
            if isinstance(item,XMLChecker):
                s = "(%s)" % item.name
                key = item.name
            else:
                s = "(%s)" % str(item)
                key = str(item)
            mn,mx = self.checks[key].minOccurs,self.checks[key].maxOccurs
            if mn == 0 or self.checks[key].required==False:
                if mx == 1:
                    s += "?"
                elif isinstance(mx,Inf):
                    s += "*"
                else:
                    s += "{0,%d}" % mx
            elif mn == 1:
                if isinstance(mx,Inf.__class__):
                    s += "+"
                elif mx != 1:
                    s += "{1,%d}" % mx
            else:
                s += "{%d,%d}" % (mn,mx)
                
            pattern.append(s)
            self.Log(6,"Adding to pattern:%s" % s)
        self.Log(5,"Pattern: %s" % pattern)
        #print pattern
        return pattern
    
    def endDocument(self):
        #self.Log.report()
        pass
        
    def characters(self,ch):
        if self.write:
            self.buffer += ch
            

def validate_xml(checks,feed,startcheck = None,debug = 5):
    """validate_xml(checks, feed, startcheck = None, debug = 5
    validates xml text (feed) according to the checks (a dictionary of XMLCheck objects)
    """
    from StringIO import StringIO
    v = XML_Validator(checks,startcheck,debug)
    p = make_parser()
    p.setContentHandler(v)
    p.parse(StringIO(feed))
    return v._ok

class Validator:
    def __init__(self,name):
        self.name = name
        self.check = {}

    def register(self,check):
        if isinstance(check,XMLChecker):
            self.check[check.name]=check
            for child in check.expected_children:
                    if isinstance(check,XMLChecker):
                            self.register(child)
        elif isinstance(check,str):
                if self.check.has_key(check): pass
        else:
            raise "Cannot use: %s not a check object" % repr(check)

    def validate(self,feed,start = None,debug=0):
        validate_xml(self.check,feed,start,debug)

    def main(self):
        m = filter(XMLChecker.ismain,self.check.values())
        return m[0]

    run = validate
    use = load = register

    def __getitem__(self,item):
        return self.check.get(item,None)






if __name__=='__main__':
    nameCheck = TextChecker('name')
    emailCheck = EmailChecker('email')

    contactCheck = SequenceChecker('contact', main=True)
    
    contactCheck.AddChild(nameCheck)
    contactCheck.AddChild(emailCheck)
    
    v = Validator('contactValidator')
    v.use(contactCheck)
    
    text = """<contact>
   <name>John Q. Public</name>
   <email>johnq@example.com</email>
</contact>"""
    
    v.run(text)
    
    print "ok"
    
    v.run("""<contact />""")
    
    
    
 
