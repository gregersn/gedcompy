import unittest
import gedcom
import six
import tempfile
from os import remove

# Sample GEDCOM file from Wikipedia
GEDCOM_FILE = """0 HEAD
1 SOUR Reunion
2 VERS V8.0
2 CORP Leister Productions
1 DEST Reunion
1 DATE 11 FEB 2006
1 FILE test
1 GEDC
2 VERS 5.5
1 CHAR MACINTOSH
0 @I1@ INDI
1 NAME Robert /Cox/
1 NAME Bob /Cox/
2 TYPE aka
1 NAME
2 GIVN Rob
2 SURN Cox
2 TYPE aka
1 SEX M
1 FAMS @F1@
1 CHAN
2 DATE 11 FEB 2006
0 @I2@ INDI
1 NAME Joann /Para/
1 SEX F
1 FAMS @F1@
1 CHAN
2 DATE 11 FEB 2006
0 @I3@ INDI
1 NAME Bobby Jo /Cox/
1 SEX M
1 FAMC @F1@
1 CHAN
2 DATE 11 FEB 2006
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 MARR
1 CHIL @I3@
0 TRLR
"""


def v(string):
    return string.format(version=gedcom.__version__)


class GedComTestCase(unittest.TestCase):

    def testCanParse(self):
        parsed = gedcom.parse_string(GEDCOM_FILE)
        self.assertTrue(isinstance(parsed, gedcom.GedcomFile))

        people = list(parsed.individuals)
        self.assertTrue(len(people), 3)

        bob = people[0]
        self.assertEqual(bob.name, ("Robert", "Cox"))
        self.assertEqual(bob.aka, [("Bob", "Cox"), ('Rob', 'Cox')])
        self.assertEqual(bob.sex, 'M')
        self.assertEqual(bob.gender, 'M')
        self.assertTrue(bob.is_male)
        self.assertFalse(bob.is_female)
        self.assertEqual(bob.parents, [])
        self.assertEqual(bob.father, None)
        self.assertEqual(bob.mother, None)

        joann = people[1]
        self.assertEqual(joann.name, ("Joann", "Para"))
        self.assertEqual(joann.sex, 'F')
        self.assertEqual(joann.gender, 'F')
        self.assertFalse(joann.is_male)
        self.assertTrue(joann.is_female)
        self.assertEqual(joann.parents, [])

        bobby_jo = people[2]
        self.assertEqual(bobby_jo.name, ("Bobby Jo", "Cox"))
        self.assertEqual(bobby_jo.sex, 'M')
        self.assertEqual(bobby_jo.gender, 'M')
        self.assertTrue(bobby_jo.is_male)
        self.assertFalse(bobby_jo.is_female)
        self.assertEqual(bobby_jo.parents, [bob, joann])
        self.assertEqual(bobby_jo.father, bob)
        self.assertEqual(bobby_jo.mother, joann)

        families = list(parsed.families)
        self.assertEqual(len(families), 1)
        family = families[0]
        self.assertEqual(family.__class__, gedcom.Family)
        self.assertEqual([p.as_individual() for p in family.partners], [bob, joann])

    def testCreateEmpty(self):
        gedcomfile = gedcom.GedcomFile()
        self.assertEqual(gedcomfile.gedcom_lines_as_string(), v('0 HEAD\n1 SOUR\n2 NAME gedcompy\n2 VERS {version}\n1 CHAR UTF-8\n1 GEDC\n2 VERS 5.5\n2 FORM LINEAGE-LINKED\n0 TRLR'))

    def testCanCreate(self):
        gedcomfile = gedcom.GedcomFile()
        individual = gedcomfile.individual()
        individual.set_sex("M")
        self.assertEqual(individual.level, 0)

        self.assertEqual(list(gedcomfile.individuals)[0], individual)

        self.assertEqual(individual.tag, 'INDI')
        self.assertEqual(individual.level, 0)
        self.assertEqual(individual.note, None)

        family = gedcomfile.family()

        self.assertEqual(family.tag, 'FAM')
        self.assertEqual(family.level, 0)

        self.assertEqual(gedcomfile.gedcom_lines_as_string(), v('0 HEAD\n1 SOUR\n2 NAME gedcompy\n2 VERS {version}\n1 CHAR UTF-8\n1 GEDC\n2 VERS 5.5\n2 FORM LINEAGE-LINKED\n0 @I1@ INDI\n1 SEX M\n0 @F2@ FAM\n0 TRLR'))
        self.assertEqual(repr(gedcomfile), v("GedcomFile(\nElement(0, 'HEAD', [Element(1, 'SOUR', [Name(2, 'NAME', 'gedcompy'), Element(2, 'VERS', '{version}')]), Element(1, 'CHAR', 'UTF-8'), Element(1, 'GEDC', [Element(2, 'VERS', '5.5'), Element(2, 'FORM', 'LINEAGE-LINKED')])]),\nIndividual(0, 'INDI', '@I1@', [Sex(1, 'SEX', 'M')]),\nFamily(0, 'FAM', '@F2@'),\nElement(0, 'TRLR'))"))

    def testCanOnlyAddIndividualOrFamilyToFile(self):
        gedcomfile = gedcom.GedcomFile()
        title = gedcom.Element(tag="TITL")
        self.assertRaises(Exception, gedcomfile.add_element, (title))

    def testCanAddIndividualRaw(self):
        gedcomfile = gedcom.GedcomFile()
        element = gedcom.Element(tag="INDI")
        gedcomfile.add_element(element)

    def testCanAddFamilyRaw(self):
        gedcomfile = gedcom.GedcomFile()
        element = gedcom.Element(tag="FAM")
        gedcomfile.add_element(element)

    def testCanAddIndividualObj(self):
        gedcomfile = gedcom.GedcomFile()
        element = gedcom.Individual()
        gedcomfile.add_element(element)

    def testCanAddFamilyObj(self):
        gedcomfile = gedcom.GedcomFile()
        element = gedcom.Family()
        gedcomfile.add_element(element)


    def testIndividualIdsWork(self):
        gedcomfile = gedcom.GedcomFile()
        element1 = gedcom.Individual()
        element2 = gedcom.Individual()
        self.assertEqual(element1.id, None)
        self.assertEqual(element2.id, None)

        gedcomfile.add_element(element1)
        gedcomfile.add_element(element2)

        self.assertEqual(element1.id, '@I1@')
        self.assertEqual(element2.id, '@I2@')

    def testIdAssismentIsRobust(self):
        gedcomfile = gedcom.parse_string("0 HEAD\n0 @I1@ INDI\n1 NAME\n2 GIVN Bob\n2 SURN Cox\n\n0 TRLR")
        element1 = gedcom.Individual()
        self.assertEqual(element1.id, None)
        gedcomfile.add_element(element1)
        self.assertEqual(element1.id, '@I2@')

    def testCanAutoDetectInputFP(self):
        fp = six.StringIO(GEDCOM_FILE)
        parsed = gedcom.parse(fp)
        self.assertTrue(isinstance(parsed, gedcom.GedcomFile))

    def testCanAutoDetectInputString(self):
        parsed = gedcom.parse(GEDCOM_FILE)
        self.assertTrue(isinstance(parsed, gedcom.GedcomFile))

    def testCanAutoDetectInputFilename(self):
        myfile = tempfile.NamedTemporaryFile()
        filename = myfile.name
        parsed = gedcom.parse(filename)
        self.assertTrue(isinstance(parsed, gedcom.GedcomFile))

    def testSupportNameInGivenAndSurname(self):
        gedcomfile = gedcom.parse_string("0 HEAD\n0 @I1@ INDI\n1 NAME\n2 GIVN Bob\n2 SURN Cox\n\n0 TRLR")
        self.assertEqual(gedcomfile['@I1@'].name, ('Bob', 'Cox'))

    def testSupportNameInOneWithSlashes(self):
        gedcomfile = gedcom.parse_string("0 HEAD\n0 @I1@ INDI\n1 NAME Bob /Cox/\n\n0 TRLR")
        self.assertEqual(gedcomfile['@I1@'].name, ('Bob', 'Cox'))

    def testSaveFile(self):
        gedcomfile = gedcom.parse_string(GEDCOM_FILE)
        outputfile = tempfile.NamedTemporaryFile()
        outputfilename = outputfile.name
        gedcomfile.save(outputfile)
        outputfile.seek(0,0)
        
        self.assertEqual(outputfile.read(), GEDCOM_FILE.encode("utf8"))
        self.assertRaises(Exception, gedcomfile.save, (outputfilename))
        outputfile.close()
        
        gedcomfile.save(outputfilename)
        with open(outputfilename) as output:
            self.assertEqual(output.read(), GEDCOM_FILE)
        remove(outputfilename)

    def testErrorWithBadTag(self):
        self.assertRaises(Exception, gedcom.Individual, [], {'tag': 'FAM'})

    def testErrorWithBadLevel(self):
        individual = gedcom.Individual(level='foo')
        self.assertRaises(Exception, individual.set_levels_downward)

    def testNote(self):
        gedcomfile = gedcom.parse_string("0 HEAD\n0 @I1@ INDI\n1 NAME\n2 GIVN Bob\n2 SURN Cox\n1 NOTE foo\n0 TRLR")
        self.assertEqual(list(gedcomfile.individuals)[0].note, 'foo')

    def testNoteCont(self):
        gedcomfile = gedcom.parse_string("0 HEAD\n0 @I1@ INDI\n1 NAME\n2 GIVN Bob\n2 SURN Cox\n1 NOTE foo\n2 CONT bar\n0 TRLR")
        self.assertEqual(list(gedcomfile.individuals)[0].note, 'foo\nbar')

    def testNoteConc(self):
        gedcomfile = gedcom.parse_string("0 HEAD\n0 @I1@ INDI\n1 NAME\n2 GIVN Bob\n2 SURN Cox\n1 NOTE foo\n2 CONC bar\n0 TRLR")
        self.assertEqual(list(gedcomfile.individuals)[0].note, 'foobar')

    def testNoteError(self):
        gedcomfile = gedcom.parse_string("0 HEAD\n0 @I1@ INDI\n1 NAME\n2 GIVN Bob\n2 SURN Cox\n1 NOTE foo\n2 TITL bar\n0 TRLR")
        ind = list(gedcomfile.individuals)[0]
        self.assertRaises(ValueError, lambda : ind.note)

    def testBirth(self):
        gedcomfile = gedcom.parse_string("0 HEAD\n0 @I1@ INDI\n1 NAME\n2 GIVN Bob\n2 SURN Cox\n1 BIRT\n2 DATE 1980\n2 PLAC London\n0 TRLR")
        ind = list(gedcomfile.individuals)[0]
        birth = ind.birth
        self.assertEqual(birth.place, "London")
        self.assertEqual(birth.date, "1980")

    def testDeath(self):
        gedcomfile = gedcom.parse_string("0 HEAD\n0 @I1@ INDI\n1 NAME\n2 GIVN Bob\n2 SURN Cox\n1 DEAT\n2 DATE 1980\n2 PLAC London\n0 TRLR")
        ind = list(gedcomfile.individuals)[0]
        death = ind.death
        self.assertEqual(death.place, "London")
        self.assertEqual(death.date, "1980")

    def testSetSex(self):
        gedcomfile = gedcom.GedcomFile()
        ind = gedcomfile.individual()
        ind.set_sex('m')
        ind.set_sex('M')
        ind.set_sex('f')
        ind.set_sex('F')
        self.assertRaises(TypeError, ind.set_sex, 'foo')
        self.assertRaises(TypeError, ind.set_sex, 'female')
        self.assertRaises(TypeError, ind.set_sex, 'male')

    def testTitle(self):
        gedcomfile = gedcom.parse_string("0 HEAD\n0 @I1@ INDI\n1 NAME\n2 GIVN Bob\n2 SURN Cox\n1 TITL King\n0 TRLR")
        self.assertEqual(list(gedcomfile.individuals)[0].title, 'King')

        gedcomfile = gedcom.parse_string("0 HEAD\n0 @I1@ INDI\n1 NAME\n2 GIVN Bob\n2 SURN Cox\n0 TRLR")
        self.assertEqual(list(gedcomfile.individuals)[0].title, None)

    def testParseError(self):
        self.assertRaises(Exception, gedcom.parse_string, "foo")

    def testFirstNameOnly1(self):
        gedcomfile = gedcom.parse_string("0 HEAD\n0 @I1@ INDI\n1 NAME\n2 GIVN Bob\n0 TRLR")
        self.assertEqual(list(gedcomfile.individuals)[0].name, ('Bob', None))

    def testFirstNameOnly2(self):
        gedcomfile = gedcom.parse_string("0 HEAD\n0 @I1@ INDI\n1 NAME Bob\n0 TRLR")
        self.assertEqual(list(gedcomfile.individuals)[0].name, ('Bob', None))

    def testLastNameOnly1(self):
        gedcomfile = gedcom.parse_string("0 HEAD\n0 @I1@ INDI\n1 NAME\n2 SURN Bob\n0 TRLR")
        self.assertEqual(list(gedcomfile.individuals)[0].name, (None, 'Bob'))

    def testEmptyName(self):
        gedcomfile = gedcom.parse_string("0 HEAD\n0 @I1@ INDI\n1 NAME \n0 TRLR")
        self.assertEqual(list(gedcomfile.individuals)[0].name, (None, None))

    def testInvalidNames(self):
        gedcomfile = gedcom.parse_string("0 HEAD\n0 @I1@ INDI\n1 NAME Bob /Russel\n0 TRLR")
        self.assertRaises(Exception, lambda : list(gedcomfile.individuals)[0].name)

    def testDashInID(self):
        gedcomfile = gedcom.parse_string("0 HEAD\n0 @I1-123@ INDI\n1 NAME\n2 GIVN Bob\n0 TRLR")
        self.assertEqual(list(gedcomfile.individuals)[0].name, ('Bob', None))

if __name__ == '__main__':
    unittest.main()
