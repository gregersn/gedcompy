import os
import unittest
import gedcom


class TestConnection(unittest.TestCase):
    def setUp(self):
        filename = os.path.join(os.path.dirname(__file__), "test.ged")
        self.ged = gedcom.parse(filename)

    def test_parent(self):
        A = self.ged['@I1@']
        B = self.ged['@I4580@']
        connections = gedcom.individual.connection(A, B)

        self.assertIsNotNone(connections)
        # self.assertEqual(len(connections), 2)

        self.assertListEqual([A, B], connections)
    
    def test_child(self):
        A = self.ged['@I4580@']
        B = self.ged['@I1@']
        connections = gedcom.individual.connection(A, B)

        self.assertIsNotNone(connections)
        # self.assertEqual(len(connections), 2)

        self.assertListEqual([A, B], connections)
    
    def test_grandfather(self):
        A = self.ged['@I1@']
        B = self.ged['@I4584@']
        C = self.ged['@I4587@']

        connections = gedcom.individual.connection(A, C)

        self.assertIsNotNone(connections)
        self.assertEqual(A, connections[0])
        self.assertEqual(C, connections[-1])
        self.assertEqual(len(connections), 3)
        self.assertListEqual([A, B, C], connections)
    
    def test_grandchild(self):
        A = self.ged['@I4587@']
        B = self.ged['@I4584@']
        C = self.ged['@I1@']

        connections = gedcom.individual.connection(A, C)

        self.assertIsNotNone(connections)
        self.assertEqual(A, connections[0])
        self.assertEqual(C, connections[-1])
        self.assertEqual(len(connections), 3)
        self.assertListEqual([A, B, C], connections)
    
    def test_aunt(self):
        A = self.ged['@I1@']
        B = self.ged['@I4584@']
        C = self.ged['@I4587@']
        D = self.ged['@I4588@']

        connections = gedcom.individual.connection(A, D)

        self.assertIsNotNone(connections)
        # self.assertEqual(len(connections), 3)
        self.assertListEqual([A, B, C, D], connections)
