from typing import List
from .element import Element, register_tag
from .family import Family

@register_tag("INDI")
class Individual(Element):
    """Represents and INDI (Individual) element."""

    @property
    def parents(self):
        """
        Return list of parents of this person.
        Gedcom standard allows for a person to be the child of more than one family,
        whether the data makes sense or is accurate,
        we handle this by returning all `Individual` elements.

        NB: There may be 0, 1, 2, 3, ... elements in this list.

        :returns: List of Individual's
        """
        if 'FAMC' in self:
            famc = []
            if type(self['FAMC']) != list:
                famc.append(self['FAMC'])
            else:
                famc = self['FAMC']

            parents = []
            for fam in famc:
                family_as_child_id = fam.value
                family = self.get_by_id(family_as_child_id)
                if not any(child.value == self.id for child in family.get_list("CHIL")):
                    # raise Exception("Invalid family", family, self)
                    pass
                for fp in family.partners:
                    parents.append(fp)
            parents = [p.as_individual() for p in parents]
            return parents
        else:
            return []

    @property
    def name(self):
        """
        Return this person's name.

        Returns a tuple of (firstname, lastname). If firstname or lastname isn't in the file, then None is returned.
        :returns: (firstname, lastname)
        """
        name_tag = self['NAME']
        first = ''
        last = ''
        if isinstance(name_tag, list):
            # We have more than one name, get the preferred name
            # Don't assume it's the first
            for name in name_tag:
                preferred_name = name
                if 'TYPE' not in name:
                    break

        else:
            # We've only one name
            preferred_name = name_tag
        if preferred_name.value in ('', None):
            if 'GIVN' in preferred_name:
                first = preferred_name['GIVN'].value
            else:
                first = None

            if 'SURN' in preferred_name:
                last = preferred_name['SURN'].value
            else:
                last = None
        else:
            vals = preferred_name.value.split("/")
            assert len(vals) > 0
            if len(vals) == 1:
                # Only first name
                first = vals[0].strip()
                last = None
            elif len(vals) == 2:
                # malformed line
                raise Exception
            elif len(vals) == 3:
                # Normal
                first, last, dud = vals

                first = first.strip()
                last = last.strip()
            else:
                first = preferred_name['GIVN'].value
                last = preferred_name['SURN'].value

        return first, last

    @property
    def aka(self):
        """Return a list of 'also known as' names."""
        aka_list = []
        name_tag = self['NAME']

        if isinstance(name_tag, list):
            # We have more than one name, get the aka names
            for name in name_tag:

                if 'TYPE' in name and name['TYPE'].value.lower() == 'aka':
                    if name.value in ('', None):
                        first = name['GIVN'].value
                        last = name['SURN'].value
                    else:
                        first, last, dud = name.value.split("/")
                        first = first.strip()
                        last = last.strip()
                    aka_list.append((first, last))

        return aka_list

    @property
    def birth(self):
        """Class representing the birth of this person."""
        if self['BIRT'] is None:
            return None
        else:
            if type(self['BIRT']) != list:
                return self['BIRT']
            else:
                return self['BIRT'][0]

    @property
    def death(self):
        """Class representing the death of this person."""
        if self['DEAT'] is None:
            return None
        else:
            if type(self['DEAT']) != list:
                return self['DEAT']
            else:
                return self['DEAT'][0]

    @property
    def sex(self):
        """
        Return the sex of this person, as the string 'M' or 'F'.
        Return empty string if nothing can be found

        NB: This should probably support more sexes/genders.

        :rtype: str
        """
        try:
            return self['SEX'].value
        except AttributeError:
            return ''

    @property
    def gender(self):
        """
        Return the sex of this person, as the string 'M' or 'F'.

        NB: This should probably support more sexes/genders.

        :rtype: str
        """
        return self['SEX'].value

    @property
    def father(self):
        """
        Calculate and return the individual represenating the father of this person.

        Returns `None` if none found.

        :return: the father, or `None` if not in file.
        :raises NotImplementedError: If it cannot figure out who's the father.
        :rtype: :py:class:`Individual`
        """
        male_parents = [p for p in self.parents if p.is_male]
        if len(male_parents) == 0:
            return None
        elif len(male_parents) == 1:
            return male_parents[0]
        elif len(male_parents) > 1:
            # TODO: return ALL parents, not caring who the father actually is, only relying on the data that is provided.
            #  raise NotImplementedError()
            return male_parents[0]

    @property
    def mother(self):
        """
        Calculate and return the individual represenating the mother of this person.

        Returns `None` if none found.

        :return: the mother, or `None` if not in file.
        :raises NotImplementedError: If it cannot figure out who's the mother.
        :rtype: :py:class:`Individual`
        """
        female_parents = [p for p in self.parents if p.is_female]
        if len(female_parents) == 0:
            return None
        elif len(female_parents) == 1:
            return female_parents[0]
        elif len(female_parents) > 1:
            # TODO: return ALL parents, not caring who the mother actually is, only relying on the data that is provided.
            #  raise NotImplementedError()
            return female_parents[0]

    @property
    def is_female(self):
        """Return True iff this person is recorded as female."""
        return self.sex.lower() == 'f'

    @property
    def is_male(self):
        """Return True iff this person is recorded as male."""
        return self.sex.lower() == 'm'

    @property
    def has_father(self):
        """Return True iff this preson has a father record"""
        return self.father is not None

    @property
    def has_mother(self):
        """Return True iff this preson has a mother record"""
        return self.mother is not None

    def set_sex(self, sex):
        """
        Set the sex for this person.

        :param str sex: 'M' or 'F' for male or female resp.
        :raises TypeError: if `sex` is invalid
        """
        sex = sex.upper()
        if sex not in ['M', 'F']:
            raise TypeError("Currently only support M or F")
        sex_node = self['SEX']
        if sex_node is not None:
            sex_node.value = sex
        else:
            self.add_child_element(self.gedcom_file.element("SEX", value=sex))

    @property
    def title(self):
        """Return the value of the Title (TITL) of this person, or None if no title."""
        try:
            return self['TITL'].value
        except:
            return None

    @property
    def source(self):
        """
        Get the source of information for that element

        :returns: source info
        :rtype: list of  `Source` classes
        :raises :AttributeError: if there is no source info
        """
        source = []
        if (type(self['SOUR']) == list):
            return self['SOUR']
        else:
            source.append(self['SOUR'])
        return source

    @property
    def residence(self):
        """
        return :py:class: `Residence` for this individual

        :returns: residence
        :rtype: :py:class: `Residence`
        :raises :AttributeError: if there is no residence record
        """
        residence = []
        if self['RESI'] is None:
            return None
        else:
            if (type(self['RESI']) == list):
                return self['RESI']
            else:
                residence.append(self['RESI'])
            return residence

    @property
    def event(self):
        """
        get any event about an individual

        :returns: events
        :rtype: list of :py:class: `Event` for his individual
        :raises: AttributeError: if there is no record
        """
        event = []
        if self['EVEN'] is None:
            return None
        else:
            if (type(self['EVEN']) == list):
                return self['EVEN']
            else:
                event.append(self['EVEN'])
            return event

    @property
    def burial(self):
        """
        get burial information for an individual

        :returns: burial
        :rtype: :py:class: `Burial`
        :raises: IndexError: if there is no record for this individual
        """
        if self['BURI'] is None:
            return None
        else:
            return self['BURI']

    @property
    def divorce(self):
        """
        return a list of divorce records

        :returns: divorce records
        :rtype: py:class: `Divorce`
        :raises: AttributeError: if there is no record for this individual
        """
        if (len(self.get_list("DIV")) == 0):
            return None
        else:
            return self.get_list("DIV")

    # TODO need to add properties/return cases for events
    @property
    def baptism_lds(self):
        """
        return records of baptism of the LDS church
        ['BAPL']

        :returns: LDS baptism records
        :rtype: TBD
        :raises: AttributeError: if there is no record for this individual
        """
        if (len(self.get_list("BAPL")) == 0):
            return None
        else:
            return self.get_list("BAPL")[0]

    @property
    def baptism(self):
        """
        return records of Baptism
        ['BAPM']

        :returns: baptism records
        :rtype: $
        :raises: AttributeError: if there is no record for this individual
        """
        if (len(self.get_list("BAPM")) == 0):
            return None
        else:
            return self.get_list("BAPM")[0]

    @property
    def bar_mitzvah(self):
        """
        return records of Bar_Mitzvah
        ['BARM']

        :returns: bar_mitzvah records
        :rtype: $
        :raises: AttributeError: if there is no record for this individual
        """
        if (len(self.get_list("BARM")) == 0):
            return None
        else:
            return self.get_list("BARM")[0]

    @property
    def bas_mitzvah(self):
        """
        ['BASM']

        :returns: bas_mitzvah records
        :rtype: $
        :raises: AttributeError: if there is no record for this individual
        """
        if (len(self.get_list("BASM")) == 0):
            return None
        else:
            return self.get_list("BASM")[0]

    @property
    def blessing(self):
        """
        ['BLES']

        :returns: blessing records
        :rtype: $
        :raises: AttributeError: if there is no record for this individual
        """
        if (len(self.get_list("BLES")) == 0):
            return None
        else:
            return self.get_list("BLES")[0]

    @property
    def christening(self):
        """
        ['CHR']

        :returns: christening records
        :rtype: $
        :raises: AttributeError: if there is no record for this individual
        """
        if (len(self.get_list("CHR")) == 0):
            return None
        else:
            return self.get_list("CHR")[0]

    @property
    def adult_christening(self):
        """
        ['CHRA']

        :returns: adult christening
        :rtype: $
        :raises: AttributeError: if there is no record for this individual
        """
        if (len(self.get_list("CHRA")) == 0):
            return None
        else:
            return self.get_list("CHRA")[0]

    @property
    def confirmation(self):
        """
        ['CONF']

        :returns: confirmation records
        :rtype: $
        :raises: AttributeError: if there is no record for this individual
        """
        if (len(self.get_list("CONF")) == 0):
            return None
        else:
            return self.get_list("CONF")[0]

    @property
    def confirmation_lds(self):
        """
        ['CONL']

        :returns: lds church confirmation records
        :rtype: $
        :raises: AttributeError: if there is no record for this individual
        """
        if (len(self.get_list("CONL")) == 0):
            return None
        else:
            return self.get_list("CONL")[0]

    @property
    def cremation(self):
        """
        ['CREM']

        :returns: records of cremation
        :rtype: $
        :raises: AttributeError: if there is no record for this individual
        """
        if (len(self.get_list("CREM")) == 0):
            return None
        else:
            return self.get_list("CREM")[0]

    @property
    def emigration(self):
        """
        ['EMIG']

        :returns: emigration records
        :rtype: $
        :raises: AttributeError: if there is no record for this individual
        """
        if (len(self.get_list("EMIG")) == 0):
            return None
        else:
            return self.get_list("EMIG")[0]

    @property
    def endowment(self):
        """
        ['ENDL']

        :returns: endowment records
        :rtype: $
        :raises: AttributeError: if there is no record for this individual
        """
        if (len(self.get_list("ENDL")) == 0):
            return None
        else:
            return self.get_list("ENDL")[0]

    @property
    def engagement(self):
        """
        ['ENGA']

        :returns: engagement records
        :rtype: $
        :raises: AttributeError: if there is no record for this individual
        """
        if (len(self.get_list("ENGA")) == 0):
            return None
        else:
            return self.get_list("ENGA")[0]

    @property
    def graduation(self):
        """
        ['GRAD']

        :returns: graduation records
        :rtype: $
        :raises: AttributeError: if there is no record for this individual
        """
        if (len(self.get_list("GRAD")) == 0):
            return None
        else:
            return self.get_list("GRAD")[0]

    @property
    def immigration(self):
        """
        ['IMMI']

        :returns: immigration records
        :rtype: $
        :raises: AttributeError: if there is no record for this individual
        """
        if (len(self.get_list("IMMI")) == 0):
            return None
        else:
            return self.get_list("IMMI")[0]

    @property
    def naturalization(self):
        """
        ['NATU']

        :returns: naturalization records
        :rtype: $
        :raises: AttributeError: if there is no record for this individual
        """
        if (len(self.get_list("NATU")) == 0):
            return None
        else:
            return self.get_list("NATU")[0]

    @property
    def will(self):
        """
        ['WILL']

        :returns: will records
        :rtype: $
        :raises: AttributeError: if there is no record for this individual
        """
        if (len(self.get_list("WILL")) == 0):
            return None
        else:
            return self.get_list("WILL")[0]


@register_tag("SEX")
class Sex(Individual):
    """Represents a pointer to a sex entry"""

    pass


@register_tag("NAME")
class Name(Individual):
    """Represents a pointer to a name entry"""

    pass


def search_children(start: Individual, target: Individual):
    best_result = None
    if 'FAMS' not in start:
        return None

    children = []
    if type(start['FAMS']) == list:
        for f in start['FAMS']:
            children += f.as_individual().children
    else:
        children = start['FAMS'].as_individual().children

    for child in children:
        if child.as_individual() == target:
            return [start, target, ]

        res = search_children(child.as_individual(), target)
        if res is not None:
            if best_result is None or len(res) < len(best_result):
                best_result = [start, ] + res

    return best_result


def search_siblings(start: Individual, target: Individual):
    best_result = None
    if 'FAMC' not in start:
        return None
    
    if start == target:
        return [target, ]
    
    children = []
    if type(start['FAMC']) == list:
        for f in start['FAMC']:
            children += f.as_individual().children
    else:
        children = start['FAMC'].as_individual().children

    for child in children:
        if child.as_individual() == start:
            continue

        if child.as_individual() == target:
            return [start, target, ]
        
        res = search_children(child.as_individual(), target)
        if res is not None:
            if best_result is None or len(res) < len(best_result):
                best_result = [start, ] + res

    return best_result


def search(start: Individual, target: Individual):
    best_result = None

    if start == target:
        return [target, ]

    parents = start.parents
    for parent in parents:
        res = search(parent, target)
        if res is not None:
            if best_result is None or len(res) < len(best_result):
                best_result = [start, ] + res
    
    res = search_siblings(start, target)
    if res is not None:
        if best_result is None or len(res) < len(best_result):
            best_result = res

    res = search_children(start, target)
    if res is not None:
        if best_result is None or len(res) < len(best_result):
            best_result = res

    return best_result


def connection(indi1: Individual, indi2: Individual, all=True):
    res = search(indi1, indi2)
    return res


def ancestor(individuals: List, current=None):
    individual = individuals[0]
    distance = 0
    direction = 0.0

    if current is not None:
        individual, distance, direction = current['individual'], current['distance'], current['direction']

    if len(individuals) > 1:
        cur, nex = individuals[0:2]
        if nex in cur.parents:
            distance += 1
            if nex == cur.father:
                direction -= pow(0.5, distance)
            elif nex == cur.mother:
                direction += pow(0.5, distance)
            return ancestor(individuals[1:], {'individual': nex,
                                              'distance': distance,
                                              'direction': direction})
    else:
        individual = individuals[0]          

    return {
        'individual': individual,
        'distance': distance,
        'direction': direction
    }
