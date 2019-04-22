import os
import unittest
import gedcom
from gedcom.individual import connection, ancestor


class TestConnection(unittest.TestCase):
    def setUp(self):
        filename = os.path.join(os.path.dirname(__file__), "test.ged")
        self.ged = gedcom.parse(filename)

    def test_parent(self):
        A = self.ged['@I1@']
        B = self.ged['@I4580@']
        connections = connection(A, B)

        self.assertIsNotNone(connections)
        self.assertEqual(len(connections), 2)

        self.assertListEqual([A, B], connections)

        self.assertEqual(ancestor(connections), B)

    def test_child(self):
        A = self.ged['@I4580@']
        B = self.ged['@I1@']
        connections = connection(A, B)

        self.assertIsNotNone(connections)
        self.assertEqual(len(connections), 2)

        self.assertListEqual([A, B], connections)
        self.assertEqual(ancestor(connections), A)

    def test_grandfather(self):
        A = self.ged['@I1@']
        B = self.ged['@I4584@']
        C = self.ged['@I4587@']

        connections = connection(A, C)

        self.assertIsNotNone(connections)
        self.assertEqual(A, connections[0])
        self.assertEqual(C, connections[-1])
        self.assertEqual(len(connections), 3)
        self.assertListEqual([A, B, C], connections)

        self.assertEqual(ancestor(connections), C)

    def test_grandchild(self):
        A = self.ged['@I4587@']
        B = self.ged['@I4584@']
        C = self.ged['@I1@']

        connections = connection(A, C)

        self.assertIsNotNone(connections)
        self.assertEqual(A, connections[0])
        self.assertEqual(C, connections[-1])
        self.assertEqual(len(connections), 3)
        self.assertListEqual([A, B, C], connections)
        self.assertEqual(ancestor(connections), A)

    def test_aunt(self):
        A = self.ged['@I1@']
        B = self.ged['@I4584@']
        D = self.ged['@I4588@']

        connections = connection(A, D)

        self.assertIsNotNone(connections)
        self.assertEqual(len(connections), 3)

        for i, p in enumerate([A, B, D]):
            self.assertEqual(p, connections[i])
        
        self.assertEqual(ancestor(connections), B)

    def test_nephew(self):
        A = self.ged['@I4588@']
        C = self.ged['@I4584@']
        D = self.ged['@I1@']

        connections = connection(A, D)

        self.assertIsNotNone(connections)
        self.assertEqual(len(connections), 3)
        self.assertListEqual([A, C, D], connections)
        self.assertEqual(ancestor(connections), A)

    def test_unrelated(self):
        A = self.ged['@I1@']
        B = self.ged['@I4591@']

        connections = connection(A, B)
        self.assertIsNone(connections)
