from .element import Element, register_tag


@register_tag("FAM")
class Family(Element):
    """Represents a family 'FAM' tag."""

    @property
    def partners(self):
        """
        Return list of partners in this marriage. all HUSB/WIFE child elements. Not dereferenced.

        :rtype: list of Husband or Wives
        """
        return self.get_list("HUSB") + self.get_list("WIFE")

    @property
    def wife(self):
        """
        Return the wife records for this element

        :return: wife or none if there are no wife records
        :rtype: :py:class: `Wife`
        """
        if (len(self.get_list("WIFE")) == 0):
            return None
        else:
            return self.get_list("WIFE")[0]

    @property
    def husband(self):
        """
        Return the husband records for this element

        :return: husband or None if there are no husband records
        :rtype: :py:class: `Husband`
        """
        if (len(self.get_list("HUSB")) == 0):
            return None
        else:
            return self.get_list("HUSB")[0]

    @property
    def has_husband(self):
        if (len(self.get_list("HUSB")) > 0):
            return True
        else:
            return False

    @property
    def has_wife(self):
        if (len(self.get_list("WIFE")) > 0):
            return True
        else:
            return False

    @property
    def has_children(self):
        pass

    @property
    def children(self):
        """
        Return a list of children for this object.

        :return: children
        :rtype: list of :py:class: `Child`
        """
        return self.get_list("CHIL")

    @property
    def marriage(self):
        """
        Return a list of marriage records. all MARR child elements.

        :return: marriages
        :rtype: list of :py:class: `Marriage` information
        """
        return self.get_list("MARR")


@register_tag("FAMS")
class Spouse(Element):
    """Generic base class for HUSB/WIFE."""

    def as_individual(self):
        """
        Return the :py:class:`Individual` for this object.

        :returns: the individual
        :rtype: :py:class:`Individual`
        :raises KeyError: if id/pointer not found in the file.
        """
        return self.gedcom_file[self.value]


@register_tag("FAMC")
class Children(Element):
    """ Generic base class for CHIL """

    def as_individual(self):
        """
        Return the :py:class:`Individual` for this object.

        :returns: the individual
        :rtype: :py:class:`Individual`
        :raises KeyError: if id/pointer not found in the file.
        """

        return self.gedcom_file[self.value]

    @property
    def father_relation(self):
        """
        Return child relation to father

        :returns: Natural if it exists
        :raise NotImplementedError: if anything other than Natural
        :rtype: string
        """
        father_relation = self.get_list("_FREL")
        if father_relation[0].value == "Natural":
            return father_relation[0].value
        else:
            raise NotImplementedError()

    @property
    def mother_relation(self):
        """
        Return child relation to mother

        :returns: Natural if it exists
        :raise NotImplementedError: if anything other than Natural
        :rtype: string
        """
        mother_relation = self.get_list("_MREL")
        if mother_relation[0].value == "Natural":
            return mother_relation[0].value
        else:
            raise NotImplementedError()


@register_tag("HUSB")
class Husband(Spouse):
    """Represents pointer to a husband in a family."""

    pass


@register_tag("WIFE")
class Wife(Spouse):
    """Represents pointer to a wife in a family."""

    pass


@register_tag("_FREL")
class Father_Relation(Children):
    """Represents pointer to a father relation"""

    pass


@register_tag("_MREL")
class Mother_Relation(Children):
    """Represents pointer to a father relation"""

    pass


@register_tag("CHIL")
class Child(Children):
    """Represents pointer to a child in a family"""

    pass
