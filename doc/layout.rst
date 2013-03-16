Layout 
=======================================

The layout text defines the order of the Custom Layout.  It relies on the 
:class:`PanelMaker` object.

Constants
------------

These constants are used in :meth:`PanelMaker.MakePanel`:

.. data:: PM_NO_LAYOUT
    
    No layout is attempted. Subclass the Panel and layout the elements 
    
.. data:: PM_DEFAULT_SIZER 

    Creates a default layout that is not workable, but gets everything on the screen
    
.. data:: PM_USE_BOXES

    Add StaticBoxes to the layout to differentiate between attributes and children
    
.. data:: PM_CUSTOM_LAYOUT

    Use a custom layout using the structured layout text (see below)

These constants are used by the control creation methods of :class:`PanelMaker`.

.. data:: PM_TEXT_BOX 

    Flag used to create text boxes to handle data in the panel. This is the default control
    
.. data:: PM_CHECK_BOX 

    Flag used to use a wx.CheckBox

.. data:: PM_CHOICE 

The PanelMaker class
------------------------------

.. class:: PanelMaker( checker, parent )
    
    The :class:`PanelMaker` class creates wxPanel objects from `XCheck` objects.
    
    .. note:: Currently, `PanelMaker` only creates `wxPython.Panel` objects.
    
    The :meth:`MakePanel` method creates the actual panel. The other methods
    are helpers.
    
    .. method:: MakePanel ( style = wx.TAB_TRAVERSAL, flags = 0 )
    
        Creates the panel. 
        
        :param style: bitmask style for the panel. See the wxPython docs
        :param flags: bitmask of PM_NO_LAYOUT, PM_DEFAULT_SIZER, PM_USE_BOXES, or PM_CUSTOM_LAYOUT
        :rtype: wx.Panel object
    
    .. method:: SetLayout ( text )
    
        Setts the Structured Layout Text for the PanelMaker object. The layout text
        is not used unless PM_CUSTOM_LAYOUT is used in :meth:MakePanel method.
    
    For the other methods, see :ref:`_rolling-panel-maker`.

Using :class:`PanelMaker`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. highlight:: python
.. code-block:: python
    :linenos:
    
    from xcheck import *
    from wx_xcheck import *
    
    personCh = XCheck('person')
    personCh.addattribute(IntCheck ('id'))
    personCh.addchild(TextCheck('name'))

    import wx

    class DemoFrame(wx.Frame):
        def __init__(self, parent):
            wx.Frame.__init__(self, parent)
            sizer = wx.BoxSizer(wx.VERTICAL)
            pm = PanelMaker(personCh, self)
            self.Panel = pm.MakePanel(wx.BORDER_SIMPLE, PM_DEFAULT_SIZER)
            sizer.Add(self.Panel, 1, wx.EXPAND | wx.GROW)
            self.SetSizerAndFit(sizer)
            self.Layout()

    app = wx.PySimpleApp()
    DemoFrame(None).Show()
    app.MainLoop()

The result looks like this:

.. image:: images/example1.png

The PM_DEFAULT_SIZER flag creates a vertical wxBoxSizer and creates a horizontal 
wxBoxSizer for each attribute and child. If you include PM_USE_BOXES, wxStaticBoxes will
be drawn around the xcheck objects attributes and children:

.. image:: images/example2.png

The PM_NO_LAYOUT flag is the default, and does nothing. If you use this option you will need
to find the children of the panel and layout the panel using the sizer.

The PM_DEFAULT_SIZER creates a simple sizer. PM_USE_BOXES creates static bokes.

The PM_CUSTOM_LAYOUT flag requires a layout using Layout Structured Text. Call the 
:meth:SetLayout method to set the required text.

.. code-block:: python
    :linenos:
    
    ... [Same as previous example]

    import wx

    _layout = """
    name id
    """

    class DemoFrame(wx.Frame):
        def __init__(self, parent):
            wx.Frame.__init__(self, parent)
            sizer = wx.BoxSizer(wx.VERTICAL)
            pm = PanelMaker(personCh, self)
            pm.SetLayout(_layout)
            self.Panel = pm.MakePanel(wx.BORDER_SIMPLE, PM_CUSTOM_LAYOUT)
            sizer.Add(self.Panel, 1, wx.EXPAND | wx.GROW)
            self.SetSizerAndFit(sizer)
            self.Layout()

    ...
    
This places the items in the panel in a differnt order. 

.. _rolling-panel-maker:

Creating your own PanelMaker
-------------------------------

:class:`PanelMaker` objects can be subclassed to create more customized panels.

When :meth:`MakePanel` is called, :class:`PanelMaker` processes the following steps:

1. Creates lists to store information about attributes, children, and extra controls
2. :meth:`MakePanel` goes through the checker's attribute list.
    1. Look for a custom 'make_%s' method and use that if possible
    2. Otherwise, calls :meth:`_guesscontrol`
        * If the checker has children of its own, it will call MakePanel recusively.
    3. If :meth:`_guesscontrol` cannot create a control, :meth:`MakePanel` calls :meth:`makecontrol` to generate a control
    
    The result is a pair of wxObjects: the Label and the Control, which is appended
    to the :class:`PanelMaker` :attr:`attributes` list.
    
    The Label is usually a wxStaticText object or None.
    
    The Control is a wxTextCtrl, wxChoice, or some appropriate control.

3. :meth:`MakePanel` goes through the same steps with the checker's children list.

Here are the methods that assist in creating the panel.
    
    .. method:: makebasiclabel( parent, name )

        Returns a wx.StaticText object.

        :param parent: the parent for the wx.StaticBox
        :type parent: wx.Window
        :param name: the text and name of the label
        :type name: string
        :rtype: wx.StaticText. The `Name` attribute of the label is "{0}Lbl".format(name)

        This method returns only the wx.StaticText object.

    .. method:: makebasiclabel( parent, name )
        
        Returns a wx.TextCtrl object.

        :param parent: the parent for the wx.TextCtrl
        :type parent: wx.Window
        :param name: the text and name of the control
        :type name: string
        :rtype: wx.StaticText. The `Name` attribute of the label is "{0}Ctrl".format(name)

        This method returns only the wx.StaticText object. 

    .. method:: makecontrol( parent, name[, flag=PM_TEXT_BOX, style = 0] )
        
        :param parent: the parent for the controls
        :type parent: wx.Window
        :param name: the text of the label (if made) and the control.
        :type name: string
        :param flag: See below 
        :type flag: integer
        :param style: wx.Control style flags
        :type style: bitmask
        :rtype: tuple of two items (Label, Control)
        
        The label is either a wx.StaticText (usually returned by :meth:`makebasiclabel`) or None.
        The control is whatever is appropriate from the flags
        
        :data: PM_TEXT_BOX 
            Creates a wx.StaticText label and wx.TextCtrl named "%{name}sLbl" and "%{name}sCtrl"
        :data: PM_CHECK_BOX
            Creates a wx.CheckBox named "%{name}sCheck". Label is None.
        :data: PM_CHOICE
            Creates a wx.Choice control and a regular label.
    
    The following methods are further shortcuts to the :meth:`makecontrol` method.
    
    .. method:: checkbox ( name, wxStyle=wx.CHK_2STATE )
    
        Calls :meth:`makecontrol` with the PM_CHOICE flag.
    
    .. method:: radiobox ( name, choices, wxStyle =wx.RA_SPECIFY_COLS )
    
        Returns a radio box with given choices.
    
    .. method:: choice ( name, choices )
    
        Creates a label and a wx.Choice.
        
    .. method:: _guesscontrol( checker )
    
        Determines the best control based on the class of the checker.
        
* BoolCheck is represented by wx.CheckBox 
* SelectionCheck is represented by wx.RadioBox or wx.Choice 
* ListCheck is represented by wx.TextCtrl plus an extra button named 'Edit{name}Btn' 
    
    Subclasses of :class:`PanelMaker` can define functions to make specific elements. These
    functions must be named "make_{name}" where name is the name of the checker. These 
    functions must return a tuple of (label, control) or (None, control). 
    
    If extra controls must be made, they should start with 'Edit{name}' to be found by
    the default sizers.
    
.. code-block::

    from xcheck import *
    from wx_xcheck import *

    personCh = XCheck('person')
    personCh.addattribute(IntCheck ('id'))
    personCh.addchild(TextCheck('name'))

    import wx
    import wx.lib.intctrl

    class PersonPanelMaker(PanelMaker):
        def make_id(self):
            lbl = self.makebasiclabel(self.panel, 'id')
            ctrl = wx.lib.intctrl.IntCtrl( self.panel, size=( 50, -1 ) )
            return lbl, ctrl

    class DemoFrame(wx.Frame):
        def __init__(self, parent):
            wx.Frame.__init__(self, parent)
            sizer = wx.BoxSizer(wx.VERTICAL)
            pm = PersonPanelMaker(personCh, self)
            self.Panel = pm.MakePanel(wx.BORDER_SIMPLE, PM_DEFAULT_SIZER)
            sizer.Add(self.Panel, 1, wx.EXPAND | wx.GROW)
            self.SetSizerAndFit(sizer)
            self.Layout()

    app = wx.PySimpleApp()
    DemoFrame(None).Show()
    app.MainLoop()
        
Layout Structured Text
-----------------------------------

Layout Structured Text is a simple multiline text object. Each line
that is not a command represents one line of the layout.

Commands begin with a `:` and usually occur in the beginning of the line.
Some commands can appear in the middle of a line.

Block Commands
^^^^^^^^^^^^^^^^

.. describe:: VBOX(Label)

Inline Commands
^^^^^^^^^^^^^^^^^^

.. describe:: HBOX(Label)
    
    *HBOX* can appear in the middle of a line. It creates a wxStaticBox around
    the next controls until the `:ENDHB` command
    
.. describe:: ENDHB

    *ENDHB* closes the static box on the line and resumes normal processing.
    
Example:

.. code-block:: python

    person = XCheck('person')
    person.addattribute(IntCheck ('id'))
    person.addchild(TextCheck('name'))
    
    


