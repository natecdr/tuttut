import unittest
import pretty_midi

from app import graph_utils

class TestGraphUtils(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_distance_between(self):
        p1 = (0, 0)
        
        p2 = (1, 0)
        self.assertEqual(graph_utils.distance_between(p1, p2), 1/6)
        
        p2 = (0, 1)
        self.assertEqual(graph_utils.distance_between(p1, p2), 1)
        
        p2 = (18, 4) #for 3 (18/6), 4 and 5 triangle
        self.assertEqual(graph_utils.distance_between(p1, p2), 5) 
        
    def test_get_fret_distance(self):
        scale_length = 650
        
        nfret = 0
        self.assertAlmostEqual(graph_utils.get_fret_distance(nfret, scale_length=scale_length), 0, places=1)
        
        nfret = 10
        self.assertAlmostEqual(graph_utils.get_fret_distance(nfret, scale_length=scale_length), 285.20, places=1)
        
        scale_length = 660
        
        nfret = 0
        self.assertAlmostEqual(graph_utils.get_fret_distance(nfret, scale_length=scale_length), 0, places=1)
        
        nfret = 20
        self.assertAlmostEqual(graph_utils.get_fret_distance(nfret, scale_length=scale_length), 452.11, places=1)
        
        