Rolling your own
================

Creating your own validator is easy. Keep these rules in mind:

* Subclass :class:`xcheck`
* Capture custom attributes
* write a `checkContent` method
* write a `normalizeContent` method
* interrupt the __call__ method if necessary

For example, :mod:`xcheck` does not have a URI or URL checker. Let's create a
simple website address validator by following the five steps outlined above:

Lets assume that we want to allow `None` as well. We can rely on Python's ``urlparse``
module to do the work.

.. code-block:: python

    import urlparse

    class URLError(XCheckError): pass
    
    class URLCheck(XCheck):
        def __init__(self, name, **kwargs):
            self.allowNone = kwargs.pop('allowNone', True)
            if 'error' not in kwargs:
                kwargs['error'] = URLError
            XCheck.__init__(self, name, **kwargs)
        
        def checkContent(self, item):
            try:
                self._url = urlparse.urlparse(item)
            except:
                raise self.error, "cannot validate %s as URL" % item
        
        def normalizeContent(self, item):
            return self._url.geturl()

This example doesn't have to re-write the __call__ method. The :class:`DateTimeCheck` does this.

.. code-block:: python

    def __call__(self, item, **kwargs):
        self._asDateTime = kwargs.pop('_asDateTime', False)
        self._asStruct = kwargs.pop('_asStruct', False)
        
        if self._asDateTime or self._asStruct:
            kwargs['_normalize'] = True
        else:
            kwargs['_normalize'] = False
        
        return XCheck.__call__(self, item, **kwargs)
    
    def normalizeContent(self, item):
        if self._asDateTime:
            return item 
        elif self._asStruct:
            return item.timetuple() 
        else:
            if self.format:
                return item.strftime(self.format)
            else:
                return item.strftime(self.formats[0])
                
        raise ValueError, "cannot normalize %s" % item

Because the :class:`DateTimeCheck` can return normalized values as
a `datetime.datetime` object, a `time.struct_time` object, it
uses two extra attributes in the `__call__` method. If either one is **True**
then `_normalize` will be turned to **True**. The normalized 
value will be returned appropriately. If _normalize is **True** ot the call,
but `_asDateTime` and `_asStruct` are false, then a string representing
the date will be returned.