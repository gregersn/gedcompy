import re
import numbers

tags_to_classes = {}


class Element(object):
    """
    Generic represetation for a GEDCOM element.

    Can be used as is, or subclassed for specific functionality.
    """

    def __init__(self, level=None,
                 tag=None, value=None,
                 id=None, parent_id=None,
                 parent=None, gedcom_file=None):
        """
        Create an element.

        :param int level: The level of this element (0, 1, 2, ...)
        :param str tag: GEDCOM tag (e.g. 'FAM', 'INDI', 'DATE', etc.)
        :param str value: *optional* value for this tag
        :param string parent_id: ID/Pointer for the parent element for this element.
        :param Element parent: The actual parent element of this object.
        :param GedcomFile gedcom_file: File this element is in (used for lookups)
        """
        self.level = level
        if tag is not None:
            if hasattr(self, 'default_tag'):
                if tag != self.default_tag:
                    raise ValueError("Tag {} differs from default {}".format(tag, self.default_tag))
            self.tag = tag
        else:
            self.tag = self.default_tag
        self.value = value
        self.child_elements = []
        self.parent_element = parent
        self.id = id
        self.parent_id = parent_id
        self.gedcom_file = gedcom_file

        if parent is not None:
            self.parent_element.add_child_element(self)

    def __repr__(self):
        """Interal string represation of this object, for debugging purposes."""
        return "{classname}({level}, {tag!r}{id}{value}{children})".format(
            classname=self.__class__.__name__, level=self.level, tag=self.tag, id=(", " + repr(self.id) if self.id else ""),
            value=(", " + repr(self.value) if self.value else ""), children=(", " + repr(self.child_elements) if len(self.child_elements) > 0 else ""))

    def to_dict(self):
        output = {
            'level': self.level,
            'tag': self.tag,
            'id': self.id,
            'value': self.value,
        }

        for el in self.child_elements:
            output[el.tag] = el.to_dict()

        return output

    def __getitem__(self, key):
        """
        Get the child element that has ``key`` as a tag.

        :param string key: tag name of child element you want
        :raises IndexError: If there are no child elements with this tag
        :returns: Element
        :rtype: Element (or subclass)
        """
        children = [c for c in self.child_elements if c.tag == key]
        if len(children) == 0:
            pass
        elif len(children) == 1:
            return children[0]
        elif len(children) > 1:
            return children

    def __contains__(self, key):
        """
        Return True iff there is at least one child element with this tag, False otherwise.

        :param str key: Tag to look for.
        """
        return any(c.tag == key for c in self.child_elements)

    def add_child_element(self, child_element):
        """
        Add `child_element` as a child of this.

        It sets the :py:attr:`parent` and :py:attr:`parent_id` of `child_element` to this
        element, but does not set the :py:meth:`level`. See
        :py:meth:`set_levels_downward` to correct that.

        :param Element child_element: The Element you want to add as a child.
        """
        child_element.parent = self
        child_element.parent_id = self.id
        child_element.gedcom_file = self.gedcom_file
        self.child_elements.append(child_element)

    def get_by_id(self, other_id):
        """
        Return an Element from the GEDCOM file with this id/pointer.

        :param str other_id: ID/Pointer of element to search for
        :returns: Element with ID
        :rtype: Element
        :raises KeyError: If this id/pointer doesn't exist in the file
        """
        return self.gedcom_file[other_id]

    def get_list(self, tag):
        """
        Return a list of all child elements that have this tag.

        :param str tag: Tag to search for (e.g. 'DATE')
        :returns: list of any child nodes that have this tag
        :rtype: list
        """
        return [c for c in self.child_elements if c.tag == tag]

    def set_levels_downward(self):
        """Set all :py:attr:`level` attributes for all child elements recursively, based on the :py:attr:`level` for this object."""
        if not isinstance(self.level, numbers.Integral):
            raise TypeError(self.level)
        for c in self.child_elements:
            c.level = self.level + 1
            c.gedcom_file = self.gedcom_file
            c.set_levels_downward()

    def gedcom_lines(self):
        """
        Iterator over the encoded lines for this element.

        :rtype: iterator over string
        """
        line_format = re.compile("^(?P<level>[0-9]+) ((?P<id>@[a-zA-Z0-9]+@) )?(?P<tag>[A-Z]+)( (?P<value>.*))?$")
        line = u"{level}{id} {tag}{value}".format(level=self.level, id=(" " + self.id if self.id else ""), tag=self.tag, value=(" " + self.value if self.value else ""))
        yield line
        for child in self.child_elements:
            for line in child.gedcom_lines():
                yield line

    @property
    def note(self):
        """
        Return the text of the Note (if any) of this Element.

        Return None if there is no Note.
        """
        if 'NOTE' not in self:
            return None
        else:
            return self['NOTE'].full_text


def register_tag(tag):
    """Internal class decorator to mark a python class as to be the handler for this tag."""
    def classdecorator(klass):
        global tags_to_classes
        tags_to_classes[tag] = klass
        klass.default_tag = tag
        return klass
    return classdecorator


def class_for_tag(tag):
    """
    Return the class object for this `tag`.

    :param str tag: tag (e.g. INDI)
    :rtype: class (Element or something that's a subclass)
    """
    global tags_to_classes
    return tags_to_classes.get(tag, Element)


def line_to_element(**line_dict):
    """
    Return an instance of :py:class:`Element` (or subclass) based on these parsed out values from :py:const:`line_regex`.

    :rtype: Element or subclass
    """
    return class_for_tag(line_dict['tag'])(**line_dict)

