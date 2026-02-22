"""Unit tests for the Tab class."""

import unittest
import pretty_midi

from tuttut.logic.tab import Tab
from tuttut.logic.theory import Tuning


def _make_midi(notes_and_times):
    """Build a PrettyMIDI with a single instrument from [(pitch, start, end), ...]."""
    midi = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=25)  # acoustic guitar
    for pitch, start, end in notes_and_times:
        instrument.notes.append(pretty_midi.Note(velocity=80, pitch=pitch, start=start, end=end))
    midi.instruments.append(instrument)
    return midi


def _make_midi_with_drums(melody_notes, drum_notes):
    """Build a PrettyMIDI with a melody instrument and a drum instrument."""
    midi = pretty_midi.PrettyMIDI()
    melody = pretty_midi.Instrument(program=25)
    for pitch, start, end in melody_notes:
        melody.notes.append(pretty_midi.Note(velocity=80, pitch=pitch, start=start, end=end))
    drums = pretty_midi.Instrument(program=0, is_drum=True)
    for pitch, start, end in drum_notes:
        drums.notes.append(pretty_midi.Note(velocity=80, pitch=pitch, start=start, end=end))
    midi.instruments.append(melody)
    midi.instruments.append(drums)
    return midi


class TestBuildTimeline(unittest.TestCase):
    def setUp(self):
        self.tuning = Tuning()

    def test_simultaneous_notes_grouped_at_same_tick(self):
        """Two notes starting at the same time share one timeline entry."""
        midi = _make_midi([(64, 0.0, 0.5), (59, 0.0, 0.5)])
        tab = Tab("test", self.tuning, midi)

        tick_0 = midi.time_to_tick(0.0)
        self.assertIn("notes", tab.timeline[tick_0])
        self.assertEqual(len(tab.timeline[tick_0]["notes"]), 2)

    def test_sequential_notes_have_separate_entries(self):
        """Notes at different times each get their own timeline entry."""
        midi = _make_midi([(64, 0.0, 0.5), (59, 0.5, 1.0)])
        tab = Tab("test", self.tuning, midi)

        tick_0 = midi.time_to_tick(0.0)
        tick_1 = midi.time_to_tick(0.5)
        self.assertEqual(len(tab.timeline[tick_0]["notes"]), 1)
        self.assertEqual(len(tab.timeline[tick_1]["notes"]), 1)

    def test_drum_tracks_excluded_from_timeline(self):
        """Notes from drum instruments do not appear in the timeline."""
        midi = _make_midi_with_drums(
            melody_notes=[(64, 0.0, 0.5)],
            drum_notes=[(38, 0.0, 0.5)],  # snare at the same time
        )
        tab = Tab("test", self.tuning, midi)

        tick_0 = midi.time_to_tick(0.0)
        notes = tab.timeline[tick_0]["notes"]
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].pitch, 64)

    def test_time_signature_recorded_in_timeline(self):
        """At least one timeline entry contains a time_signature."""
        midi = _make_midi([(64, 0.0, 0.5)])
        tab = Tab("test", self.tuning, midi)

        has_time_sig = any("time_signature" in v for v in tab.timeline.values())
        self.assertTrue(has_time_sig)


class TestPopulate(unittest.TestCase):
    def setUp(self):
        self.tuning = Tuning()

    def test_at_least_one_measure_created(self):
        """Populating a non-empty MIDI creates at least one measure."""
        midi = _make_midi([(64, 0.0, 0.5)])
        tab = Tab("test", self.tuning, midi)

        self.assertGreater(len(tab.measures), 0)

    def test_measure_boundaries_are_contiguous(self):
        """Each measure's end tick equals the next measure's start tick."""
        midi = _make_midi([(64, 0.0, 0.5), (59, 1.0, 1.5), (55, 2.0, 2.5)])
        tab = Tab("test", self.tuning, midi)

        for i in range(len(tab.measures) - 1):
            self.assertEqual(tab.measures[i].measure_end, tab.measures[i + 1].measure_start)

    def test_all_measures_have_positive_duration(self):
        """Every measure has a non-zero tick span."""
        midi = _make_midi([(64, 0.0, 0.5), (59, 1.0, 1.5)])
        tab = Tab("test", self.tuning, midi)

        for measure in tab.measures:
            self.assertGreater(measure.measure_end, measure.measure_start)

    def test_tab_measure_count_matches_measures_list(self):
        """The 'measures' list in the tab dict has the same length as tab.measures."""
        midi = _make_midi([(64, 0.0, 0.5), (59, 2.5, 3.0)])
        tab = Tab("test", self.tuning, midi)

        self.assertEqual(len(tab.tab["measures"]), len(tab.measures))


class TestTabStructure(unittest.TestCase):
    def setUp(self):
        self.tuning = Tuning()

    def test_tab_dict_has_required_keys(self):
        """Generated tab dict contains 'tuning' and 'measures'."""
        midi = _make_midi([(64, 0.0, 0.5)])
        tab = Tab("test", self.tuning, midi)

        self.assertIn("tuning", tab.tab)
        self.assertIn("measures", tab.tab)

    def test_tab_tuning_matches_input_pitches(self):
        """Tuning pitches in the tab dict match the input Tuning."""
        midi = _make_midi([(64, 0.0, 0.5)])
        tab = Tab("test", self.tuning, midi)

        expected = [s.pitch for s in self.tuning.strings]
        self.assertEqual(tab.tab["tuning"], expected)

    def test_note_events_have_string_and_fret(self):
        """Every note produced by the HMM has 'string' and 'fret' fields."""
        midi = _make_midi([(64, 0.0, 0.5)])
        tab = Tab("test", self.tuning, midi)

        for measure in tab.tab["measures"]:
            for event in measure["events"]:
                for note in event.get("notes", []):
                    self.assertIn("string", note)
                    self.assertIn("fret", note)

    def test_fret_values_in_valid_range(self):
        """All assigned frets are within [0, nfrets]."""
        midi = _make_midi([(64, 0.0, 0.5), (59, 0.5, 1.0), (55, 1.0, 1.5)])
        tab = Tab("test", self.tuning, midi)

        for measure in tab.tab["measures"]:
            for event in measure["events"]:
                for note in event.get("notes", []):
                    self.assertGreaterEqual(note["fret"], 0)
                    self.assertLessEqual(note["fret"], self.tuning.nfrets)

    def test_string_values_in_valid_range(self):
        """All assigned strings are within [0, nstrings-1]."""
        midi = _make_midi([(64, 0.0, 0.5), (59, 0.5, 1.0)])
        tab = Tab("test", self.tuning, midi)

        for measure in tab.tab["measures"]:
            for event in measure["events"]:
                for note in event.get("notes", []):
                    self.assertGreaterEqual(note["string"], 0)
                    self.assertLess(note["string"], self.tuning.nstrings)

    def test_chord_notes_assigned_to_distinct_strings(self):
        """Notes in a chord fingering each land on a different string."""
        midi = _make_midi([(64, 0.0, 0.5), (59, 0.0, 0.5)])  # E4 + B3 simultaneously
        tab = Tab("test", self.tuning, midi)

        for measure in tab.tab["measures"]:
            for event in measure["events"]:
                notes = event.get("notes", [])
                if len(notes) > 1:
                    strings = [n["string"] for n in notes]
                    self.assertEqual(len(strings), len(set(strings)))

    def test_note_event_count_matches_unique_onsets(self):
        """Number of note events in the tab matches distinct note-onset ticks."""
        midi = _make_midi([(64, 0.0, 0.5), (59, 0.5, 1.0), (55, 1.0, 1.5)])
        tab = Tab("test", self.tuning, midi)

        note_events = sum(
            1 for measure in tab.tab["measures"]
            for event in measure["events"]
            if "notes" in event
        )
        self.assertEqual(note_events, 3)

    def test_event_measure_timing_is_fractional(self):
        """All event measure_timing values are in [0.0, 1.0]."""
        midi = _make_midi([(64, 0.0, 0.5), (59, 0.5, 1.0)])
        tab = Tab("test", self.tuning, midi)

        for measure in tab.tab["measures"]:
            for event in measure["events"]:
                self.assertGreaterEqual(event["measure_timing"], 0.0)
                self.assertLessEqual(event["measure_timing"], 1.0)


class TestToString(unittest.TestCase):
    def setUp(self):
        self.tuning = Tuning()

    def test_returns_one_line_per_string(self):
        """to_string() produces exactly nstrings lines."""
        midi = _make_midi([(64, 0.0, 0.5)])
        tab = Tab("test", self.tuning, midi)

        self.assertEqual(len(tab.to_string()), self.tuning.nstrings)

    def test_each_line_starts_with_string_degree(self):
        """Each line starts with the degree name of the corresponding string."""
        midi = _make_midi([(64, 0.0, 0.5)])
        tab = Tab("test", self.tuning, midi)

        for i, string in enumerate(self.tuning.strings):
            self.assertTrue(tab.to_string()[i].startswith(string.degree))

    def test_all_lines_equal_length(self):
        """All string lines have the same length (tab is properly aligned)."""
        midi = _make_midi([(64, 0.0, 0.5), (59, 0.5, 1.0)])
        tab = Tab("test", self.tuning, midi)

        lengths = [len(line) for line in tab.to_string()]
        self.assertEqual(len(set(lengths)), 1)


class TestTabEdgeCases(unittest.TestCase):
    def setUp(self):
        self.tuning = Tuning()

    def test_out_of_range_note_placed_on_valid_fret(self):
        """A note below the fretboard range is octave-shifted to a playable position."""
        # C1 (MIDI 24) is well below standard guitar range
        midi = _make_midi([(24, 0.0, 0.5)])
        tab = Tab("test", self.tuning, midi)

        for measure in tab.tab["measures"]:
            for event in measure["events"]:
                for note in event.get("notes", []):
                    self.assertGreaterEqual(note["fret"], 0)
                    self.assertLessEqual(note["fret"], self.tuning.nfrets)

    def test_repeated_note_populates_fingering_cache(self):
        """The same note appearing twice results in a non-empty fingering cache."""
        midi = _make_midi([(64, 0.0, 0.5), (64, 1.0, 1.5)])
        tab = Tab("test", self.tuning, midi)

        self.assertGreater(len(tab.fretboard._fingering_cache), 0)

    def test_custom_weights_accepted(self):
        """Tab accepts custom difficulty weights without error."""
        midi = _make_midi([(64, 0.0, 0.5)])
        weights = {"b": 2, "height": 0.5, "length": 3, "n_changed_strings": 1}
        tab = Tab("test", self.tuning, midi, weights=weights)

        self.assertEqual(tab.weights, weights)
