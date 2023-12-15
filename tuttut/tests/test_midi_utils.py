import unittest
import pretty_midi

from tuttut import midi_utils

class TestMidiUtils(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self) -> None:
        pass
    
    def test_measure_length_ticks(self):
        midi = pretty_midi.PrettyMIDI(resolution = 220)
        
        time_signature = pretty_midi.TimeSignature(4, 4, 0)
        self.assertEqual(midi_utils.measure_length_ticks(midi, time_signature), 880)
        
        time_signature = pretty_midi.TimeSignature(4, 2, 0)
        self.assertEqual(midi_utils.measure_length_ticks(midi, time_signature), 1760)
        
        time_signature = pretty_midi.TimeSignature(4, 8, 0)
        self.assertEqual(midi_utils.measure_length_ticks(midi, time_signature), 440)
        
    def test_get_notes_between(self):
        midi = pretty_midi.PrettyMIDI(resolution = 220)
        
        notes = [
            pretty_midi.Note(velocity=100, pitch = 60, start = 0, end = 1),
            pretty_midi.Note(velocity=100, pitch = 60, start = 1, end = 2),
            pretty_midi.Note(velocity=100, pitch = 60, start = 2.5, end = 3),
            pretty_midi.Note(velocity=100, pitch = 60, start = 3, end = 3.5)
        ]
        
        midi.notes = notes
        
        self.assertEqual(
            midi_utils.get_notes_between(midi, notes, 0, 4),
            [notes[0]]
        )
        
        self.assertEqual(
            midi_utils.get_notes_between(midi, notes, midi.time_to_tick(0), midi.time_to_tick(4)),
            notes
        )
        
        self.assertEqual(
            midi_utils.get_notes_between(midi, notes, midi.time_to_tick(1), midi.time_to_tick(3)),
            [notes[1], notes[2]]
        )
        
        self.assertEqual(
            midi_utils.get_notes_between(midi, notes, midi.time_to_tick(-1), midi.time_to_tick(2.51)),
            [notes[0], notes[1], notes[2]]
        )
    
    def test_get_non_drum(self):
        instruments = [
            pretty_midi.Instrument(0, is_drum=True),
            pretty_midi.Instrument(127, is_drum = False)
        ]
        
        self.assertEqual(midi_utils.get_non_drum(instruments), [instruments[1]])
        
    def test_fill_measure_str(self):
        str = [
            'E ||', 
            'B ||1', 
            'G ||', 
            'D ||-2', 
            'A ||3', 
            'E ||'
        ]
        
        self.assertEqual(midi_utils.fill_measure_str(str),
                         [
                            'E ||--', 
                            'B ||1-', 
                            'G ||--', 
                            'D ||-2', 
                            'A ||3-', 
                            'E ||--'
                         ])
        
    def test_sort_notes_by_tick(self):        
        notes = [
            pretty_midi.Note(velocity=100, pitch = 60, start = 0, end = 1),
            pretty_midi.Note(velocity=100, pitch = 60, start = 1, end = 2),
            pretty_midi.Note(velocity=100, pitch = 60, start = 2.5, end = 3),
            pretty_midi.Note(velocity=100, pitch = 60, start = 3, end = 3.5)
        ]
        
        unsorted_notes = {
            notes[3],
            notes[1],
            notes[0],
            notes[2]
        }
        
        self.assertEqual(len(midi_utils.sort_notes_by_tick(unsorted_notes)), len(notes))
        
        self.assertEqual(midi_utils.sort_notes_by_tick(notes), notes)
        
    def test_round_to_multiple(self):
        base = 5
        
        to_round = 2 
        self.assertEqual(midi_utils.round_to_multiple(to_round, base), 0)
        
        to_round = 111
        self.assertEqual(midi_utils.round_to_multiple(to_round, base), 110)
        
        to_round = -3
        self.assertEqual(midi_utils.round_to_multiple(to_round, base), -5)
        
    def test_quantize(self):
        pass