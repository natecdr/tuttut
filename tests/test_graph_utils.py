import unittest
import pretty_midi

from tuttut import graph_utils
from tuttut.theory import Note, Tuning
from tuttut.fretboard import Fretboard

class TestGraphUtils(unittest.TestCase):
    def setUp(self):
        pass
            
    def tearDown(self):
        pass
    
    def assertSameNotes(self, notes1, notes2):
        notes1_pitches = sorted([note.pitch for note in notes1])
        notes2_pitches = sorted([note.pitch for note in notes2])
        
        self.assertEqual(notes1_pitches, notes2_pitches)
        
    def test_distance_between(self):
        fretboard = Fretboard(Tuning())
        
        p1 = (0, 0)
        
        p2 = (1, 0)
        self.assertEqual(fretboard.distance_between(p1, p2), 1/6)
        
        p2 = (0, 1)
        self.assertEqual(fretboard.distance_between(p1, p2), 1)
        
        p2 = (18, 4) #for 3 (18/6), 4 and 5 triangle
        self.assertEqual(fretboard.distance_between(p1, p2), 5) 
        
    def test_get_fret_distance(self):
        fretboard = Fretboard(Tuning())
        
        self.assertAlmostEqual(fretboard.get_fret_distance(nfret=0), 0, places=1)
        
        self.assertAlmostEqual(fretboard.get_fret_distance(nfret=10), 285.20, places=1)
        
    def test_get_notes_in_graph(self):
        pass
    
    def test_build_path_graph(self):
        pass
    
    def test_is_edge_possible(self):
        pass
    
    def test_find_all_paths(self):
        pass
    
    def test_is_path_already_checked(self):
        pass
    
    def test_is_path_possible(self):
        pass
    
    def test_compute_path_difficulty(self):
        pass
    
    def test_compute_isolated_path_difficulty(self):
        pass
    
    def test_laplace_distro(self):
        pass
    
    def test_get_nfingers(self):
        pass
    
    def test_get_n_changed_strings(self):
        pass
    
    def test_get_height(self):
        pass
    
    def test_get_path_length(self):
        pass
    
    def test_display_path_graph(self):
        pass
    
    def test_viterbi(self):
        pass
    
    def test_build_transition_matrix(self):
        pass
    
    def test_difficulties_to_probabilities(self):
        pass
    
    def test_expand_emission_matrix(self):
        pass
    
    def test_display_notes_on_graph(self):
        pass
    
    def test_fix_impossible_notes(self):
        fretboard = Fretboard(Tuning(["F#1", "E2"]))
        fretboard.tuning.nfrets = 10
        #Tuning bounds : 30 - 50
        
        notes = [
            Note(52),
            Note(46),
            Note(20),
            Note(30)
        ]
        
        self.assertSameNotes(
            fretboard.fix_oob_notes(notes, preserve_highest_note=False),
            [
                Note(40),
                Note(46),
                Note(32),
                Note(30)
            ]
        )
        
        self.assertSameNotes(
            fretboard.fix_oob_notes(notes, preserve_highest_note=True),
            [
                Note(40),
                Note(34),
                Note(32),
                Note(30)
            ]
        )