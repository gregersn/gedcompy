from . import register_tag
from .element import Element


@register_tag("EVEN")
class Event(Element):
    """Generic base class for events, like :py:class:`Birth` (BIRT) etc."""

    @property
    def date(self):
        """
        Get the Date of this event, from the 'DATE' tagged child element.

        :returns: date value
        :rtype: string
        :raises KeyError: if there is no DATE sub-element
        """
        if self['DATE']:
            return self['DATE'].value

    @property
    def place(self):
        """
        Get the place of this event, from the 'PLAC' tagged child element.

        :returns: date value
        :rtype: string
        :raises KeyError: if there is no PLAC sub-element
        """
        return self['PLAC'].value

    @property
    def source(self):
        """
        Get the source of information for that element

        :returns: source info
        :rtype: string
        """
        source = []
        if (type(self['SOUR']) == list):
            return self['SOUR']
        else:
            source.append(self['SOUR'])
        return source

    @property
    def type(self):
        """
        Get the type of event that occurs

        :returns: event type
        :rtype: string
        """
        return self['TYPE'].value


@register_tag("TYPE")
class Type(Event):
    """Represents a type of event"""
    pass


@register_tag("RESI")
class Residence(Event):
    """Represents an individuals residence"""
    pass


@register_tag("BIRT")
class Birth(Event):
    """Represents a birth (BIRT)."""

    pass


@register_tag("DEAT")
class Death(Event):
    """Represents a death (DEAT)."""

    pass


@register_tag("BURI")
class Burial(Event):
    """Represents burial information (BURI)"""

    pass


@register_tag("MARR")
class Marriage(Event):
    """Represents a marriage (MARR)."""

    pass


@register_tag("DIV")
class Divorce(Event):
    """Represents a divorce (DIV)"""

    pass


@register_tag("DATE")
class Date(Event):
    """Represents a pointer to a date value"""

    pass


@register_tag("PLAC")
class Place(Event):
    """Represents a pointer to a place entry"""

    pass


@register_tag("BAPL")
class Baptism_LDS(Event):
    """Represents a baptism of the LDS Church"""

    pass


@register_tag("BAPM")
class Baptism(Event):
    """Represents a non-LDS baptism"""

    pass


@register_tag("BARM")
class Bar_Mitzvah(Event):
    """Represents a Bar Mitzvah"""

    pass


@register_tag("BASM")
class Bas_Mitzvah(Event):
    """Represents a Bas Mitzvah"""

    pass


@register_tag("BLES")
class Blessing(Event):
    """Represents a blessing"""

    pass


@register_tag("CHR")
class Christening(Event):
    """Represents a Christening"""

    pass


@register_tag("CHRA")
class Adult_Christening(Event):
    """Represents an adult Christening"""

    pass


@register_tag("CONF")
class Confirmation(Event):
    """Represents a Christening"""

    pass


@register_tag("CONL")
class LDS_Confirmation(Event):
    """Represents a Christening of the LDS Churc"""

    pass


@register_tag("CREM")
class Cremation(Event):
    """Represents a Cremation"""

    pass


@register_tag("EMIG")
class Emigration(Event):
    """Represents an Emigration"""

    pass


@register_tag("ENDL")
class Endowment(Event):
    """Represents an Endowment"""

    pass


@register_tag("ENGA")
class Engagement(Event):
    """Represents an Engagement"""

    pass


@register_tag("GRAD")
class Graduation(Event):
    """Represents a Graduation"""

    pass


@register_tag("IMMI")
class Immigration(Event):
    """Represents an Immigration"""

    pass


@register_tag("NATU")
class Naturalization(Event):
    """Represents a naturalization"""

    pass


@register_tag("WILL")
class Will(Event):
    """Represents a Will - treated as an event"""

    pass
