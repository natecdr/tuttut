"""End-to-end integration test: MIDI → ASCII tab."""

import os
import tempfile
import unittest

import pretty_midi

from tuttut.logic.tab import Tab
from tuttut.logic.theory import Tuning


def _make_simple_midi(notes_and_times):
    """Build a PrettyMIDI with a single instrument from [(pitch, start, end), ...].

    Args:
        notes_and_times: list of (pitch, start_sec, end_sec) tuples

    Returns:
        pretty_midi.PrettyMIDI
    """
    midi = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=25)  # acoustic guitar
    for pitch, start, end in notes_and_times:
        instrument.notes.append(pretty_midi.Note(velocity=80, pitch=pitch, start=start, end=end))
    midi.instruments.append(instrument)
    return midi


class TestIntegration(unittest.TestCase):
    def test_single_note_tab(self):
        """A MIDI with one note produces a non-empty tab file."""
        midi = _make_simple_midi([(64, 0.0, 0.5)])   # E4 for half a second

        with tempfile.TemporaryDirectory() as tmp:
            tab = Tab("test_single", Tuning(), midi, output_dir=tmp)
            tab.to_ascii()

            out_path = os.path.join(tmp, "test_single.txt")
            self.assertTrue(os.path.isfile(out_path), "Tab file was not created")

            with open(out_path) as f:
                lines = f.readlines()

            # One line per string
            self.assertEqual(len(lines), Tuning().nstrings)
            # Every line has content beyond the header
            for line in lines:
                self.assertGreater(len(line.strip()), 2)

    def test_multi_note_tab_has_correct_string_count(self):
        """A MIDI with several notes produces a tab with the right number of strings."""
        midi = _make_simple_midi([
            (64, 0.0, 0.5),   # E4
            (59, 0.5, 1.0),   # B3
            (55, 1.0, 1.5),   # G3
        ])

        with tempfile.TemporaryDirectory() as tmp:
            tab = Tab("test_multi", Tuning(), midi, output_dir=tmp)
            tab.to_ascii()

            with open(os.path.join(tmp, "test_multi.txt")) as f:
                lines = f.readlines()

        self.assertEqual(len(lines), Tuning().nstrings)

    def test_custom_tuning(self):
        """Tab respects a custom tuning (ukulele)."""
        ukulele = Tuning(Tuning.standard_ukulele_tuning)
        midi = _make_simple_midi([(69, 0.0, 0.5)])   # A4

        with tempfile.TemporaryDirectory() as tmp:
            tab = Tab("test_ukulele", ukulele, midi, output_dir=tmp)
            tab.to_ascii()

            with open(os.path.join(tmp, "test_ukulele.txt")) as f:
                lines = f.readlines()

        self.assertEqual(len(lines), ukulele.nstrings)  # 4 strings for ukulele
