from . import register_tag
from .element import Element


@register_tag("SOUR")
class Source(Element):
    """Represents an information source element"""

    @property
    def page(self):
        """
        Get the page of source information for that element

        :returns: page info
        :rtype: string
        """
        return self['PAGE'].value

    @property
    def data(self):
        """
        get the data of the source info for that element

        :returns: data element
        :rtype:pyclass:`Data`
        """
        return self['DATA'].text


@register_tag("DATA")
class Data(Source):
    """represents source reference level"""

    @property
    def text(self):
        """
        get the source reference for that element

        :returns: source reference
        :rtype: string
        """
        if self['TEXT'] is not None:
            return self['TEXT'].value


@register_tag("TEXT")
class Text(Data):
    """represents source reference"""

    pass


@register_tag("PAGE")
class Page(Source):
    """Represents source information"""

    pass
