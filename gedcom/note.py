from .element import Element, register_tag


@register_tag("NOTE")
class Note(Element):
    """Represents a note (NOTE)."""

    @property
    def full_text(self):
        """
        Return the full text of this note.

        Internally, notes are stores across many child nodes, with child
        CONT/CONS child nodes that store the other lines. This method assembles
        these elements into one continuusous string.
        """
        result = "" + self.value or ''

        for cons in self.child_elements:
            if cons.tag == 'CONT':
                result += "\n"
                result += cons.value or ''
            elif cons.tag == 'CONC':
                result += cons.value or ''
            else:
                raise ValueError("Full text can only consist of CONS and CONT")

        return result

