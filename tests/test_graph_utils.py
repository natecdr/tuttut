import unittest
import numpy as np

from tuttut.logic import graph_utils
from tuttut.logic.difficulty import (
    compute_path_difficulty,
    compute_isolated_path_difficulty,
    laplace_distro,
    get_nfingers,
    get_n_changed_strings,
    get_height_score,
    get_raw_height,
    get_path_length,
)
from tuttut.logic.theory import Note, Tuning
from tuttut.logic.fretboard import Fretboard


class TestGraphUtils(unittest.TestCase):
    """
    Standard Tuning(): E4(64), B3(59), G3(55), D3(50), A2(45), E2(40)  [string 0→5]
    Each (string, fret) is a distinct Note instance in the graph even when pitches
    overlap (Note.__hash__ uses id, so each instance is unique as a graph node).
    """

    def setUp(self):
        self.tuning = Tuning()
        self.fretboard = Fretboard(self.tuning)
        self.G = self.fretboard.G
        self.positions = self.fretboard.positions
        self.weights = {"b": 1, "height": 1, "length": 1, "n_changed_strings": 1}

        # Index nodes by (string, fret) position for explicit access
        by_pos = {self.G.nodes[n]["pos"]: n for n in self.G.nodes}

        # String 0 (E4=64): frets 0-20
        self.s0f0  = by_pos[(0, 0)]   # open E4, pitch 64
        self.s0f1  = by_pos[(0, 1)]   # F4,  pitch 65
        self.s0f2  = by_pos[(0, 2)]   # F#4, pitch 66
        self.s0f5  = by_pos[(0, 5)]   # A4,  pitch 69
        self.s0f10 = by_pos[(0, 10)]  # D5,  pitch 74

        # String 1 (B3=59): frets 0-20
        self.s1f0 = by_pos[(1, 0)]    # open B3, pitch 59
        self.s1f1 = by_pos[(1, 1)]    # C4,  pitch 60
        self.s1f5 = by_pos[(1, 5)]    # E4,  pitch 64  (same pitch as s0f0)

        # String 5 (E2=40): frets 0-20
        self.s5f0 = by_pos[(5, 0)]    # open E2, pitch 40
        self.s5f5 = by_pos[(5, 5)]    # A2,  pitch 45

    def assertSameNotes(self, notes1, notes2):
        notes1_pitches = sorted([note.pitch for note in notes1])
        notes2_pitches = sorted([note.pitch for note in notes2])
        self.assertEqual(notes1_pitches, notes2_pitches)

    # -------------------------------------------------------------------------
    # Fretboard geometry
    # -------------------------------------------------------------------------

    def test_distance_between(self):
        fb = Fretboard(Tuning())

        p1 = (0, 0)
        self.assertEqual(fb.distance_between(p1, (1, 0)), 1/6)
        self.assertEqual(fb.distance_between(p1, (0, 1)), 1)
        self.assertEqual(fb.distance_between(p1, (18, 4)), 5)  # 3-4-5 triangle

    def test_get_fret_distance(self):
        fb = Fretboard(Tuning())
        self.assertAlmostEqual(fb.get_fret_distance(nfret=0), 0, places=1)
        self.assertAlmostEqual(fb.get_fret_distance(nfret=10), 285.20, places=1)

    # -------------------------------------------------------------------------
    # Note lookup (pitch index)
    # -------------------------------------------------------------------------

    def test_get_notes_in_graph(self):
        # E4 (pitch 64) can be played on 5 different string/fret positions
        e4_nodes = self.fretboard.get_specific_note_options(Note(64))
        self.assertEqual(len(e4_nodes), 5)
        for node in e4_nodes:
            self.assertEqual(node.pitch, 64)

        # A pitch outside guitar range returns nothing
        self.assertEqual(self.fretboard.get_specific_note_options(Note(1)), [])

        # get_note_options filters out empty arrays
        options = self.fretboard.get_note_options([Note(64), Note(1)])
        self.assertEqual(len(options), 1)
        self.assertEqual(options[0][0].pitch, 64)

    # -------------------------------------------------------------------------
    # Path graph
    # -------------------------------------------------------------------------

    def test_build_path_graph(self):
        # Two open strings on adjacent strings
        opts_s0 = [self.s0f0]
        opts_s1 = [self.s1f0]
        pg = graph_utils.build_path_graph(self.G, [opts_s0, opts_s1])

        import networkx as nx
        self.assertIsInstance(pg, nx.DiGraph)

        # All nodes from both arrays must appear
        for node in opts_s0 + opts_s1:
            self.assertIn(node, pg.nodes)

        # Edges only go from layer 0 to layer 1
        for u, v in pg.edges:
            self.assertIn(u, opts_s0)
            self.assertIn(v, opts_s1)

    def test_is_edge_possible(self):
        # Same string → impossible
        self.assertFalse(graph_utils.is_edge_possible(self.s0f0, self.s0f1, self.G))

        # Adjacent strings, open positions (distance 0 → possible)
        self.assertTrue(graph_utils.is_edge_possible(self.s0f0, self.s1f0, self.G))

        # Different strings, adjacent frets → possible
        self.assertTrue(graph_utils.is_edge_possible(self.s0f1, self.s1f1, self.G))

        # Edge to an open-string node always has stored distance 0, so it is possible
        # (open strings are treated as "costless" transitions in the graph).
        self.assertTrue(graph_utils.is_edge_possible(self.s0f1, self.s1f0, self.G))

        # Two fretted nodes 14 frets apart → distance > MAX_EDGE_DISTANCE=6 → impossible
        by_pos = {self.G.nodes[n]["pos"]: n for n in self.G.nodes}
        s1f15 = by_pos[(1, 15)]
        self.assertFalse(graph_utils.is_edge_possible(self.s0f1, s1f15, self.G))

    def test_is_path_already_checked(self):
        path_a = (self.s0f1, self.s1f1)
        path_b = (self.s1f1, self.s0f1)   # same Note instances, reversed
        path_c = (self.s0f1, self.s5f5)   # different path

        # Same instances in any order → already checked
        self.assertTrue(graph_utils.is_path_already_checked([path_a], path_b))
        # Different path → not yet checked
        self.assertFalse(graph_utils.is_path_already_checked([path_a], path_c))
        # Empty history → nothing is checked
        self.assertFalse(graph_utils.is_path_already_checked([], path_a))

    # -------------------------------------------------------------------------
    # Difficulty scoring
    # -------------------------------------------------------------------------

    def test_laplace_distro(self):
        # Peak at mu=0: value = 1/(2b)
        self.assertAlmostEqual(laplace_distro(0, b=1), 0.5)
        self.assertAlmostEqual(laplace_distro(0, b=2), 0.25)
        # Symmetric
        self.assertAlmostEqual(laplace_distro(1, b=1), laplace_distro(-1, b=1))
        # Decreases away from mu
        self.assertGreater(laplace_distro(0, b=1), laplace_distro(1, b=1))

    def test_get_nfingers(self):
        self.assertEqual(get_nfingers(self.positions, (self.s0f0,)), 0)   # open
        self.assertEqual(get_nfingers(self.positions, (self.s0f1,)), 1)   # fretted
        self.assertEqual(get_nfingers(self.positions, (self.s0f0, self.s1f1)), 1)  # mixed

    def test_get_n_changed_strings(self):
        path = (self.s0f1, self.s1f1)
        score = get_n_changed_strings(self.positions, path, path, self.tuning)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)

        # Completely different strings → higher score than repeating same path
        score_same = get_n_changed_strings(self.positions, (self.s0f1,), (self.s0f1,), self.tuning)
        score_diff = get_n_changed_strings(self.positions, (self.s0f1,), (self.s1f1,), self.tuning)
        self.assertGreaterEqual(score_diff, score_same)

    def test_get_height(self):
        # Fretted note has positive normalised height
        height = get_height_score(get_raw_height(self.positions, (self.s0f1,)), self.tuning)
        self.assertGreater(height, 0)
        self.assertLessEqual(height, 1)

        # Higher fret → higher score
        height_low  = get_height_score(get_raw_height(self.positions, (self.s0f1,)),  self.tuning)
        height_high = get_height_score(get_raw_height(self.positions, (self.s0f10,)), self.tuning)
        self.assertGreater(height_high, height_low)

        # Open string falls back to previous path's raw height
        self.assertEqual(
            get_raw_height(self.positions, (self.s0f0,), (self.s0f5,)),
            get_raw_height(self.positions, (self.s0f5,))
        )

    def test_get_path_length(self):
        # Single note → no edges → length 0
        self.assertEqual(get_path_length(self.G, (self.s0f1,)), 0)

        # Two notes → normalised in [0, 1]
        length = get_path_length(self.G, (self.s0f1, self.s1f1))
        self.assertGreaterEqual(length, 0)
        self.assertLessEqual(length, 1)

    def test_compute_isolated_path_difficulty(self):
        diff = compute_isolated_path_difficulty(self.positions, (self.s0f1, self.s1f1), self.tuning)
        self.assertGreater(diff, 0)
        self.assertTrue(np.isfinite(diff))

        # Higher fret → harder
        diff_low  = compute_isolated_path_difficulty(self.positions, (self.s0f1,),  self.tuning)
        diff_high = compute_isolated_path_difficulty(self.positions, (self.s0f10,), self.tuning)
        self.assertLess(diff_low, diff_high)

    def test_compute_path_difficulty(self):
        path = (self.s0f1, self.s1f1)
        diff = compute_path_difficulty(self.positions, path, path, self.weights, self.tuning)
        self.assertGreater(diff, 0)
        self.assertTrue(np.isfinite(diff))

    # -------------------------------------------------------------------------
    # HMM matrices
    # -------------------------------------------------------------------------

    def test_difficulties_to_probabilities(self):
        difficulties = np.array([1.0, 2.0, 1.0])
        probs = graph_utils.difficulties_to_probabilities(difficulties)
        self.assertAlmostEqual(float(np.sum(probs)), 1.0)
        self.assertAlmostEqual(float(probs[1]), 0.5)  # 2 / (1+2+1)

        for p in graph_utils.difficulties_to_probabilities(np.ones(3)):
            self.assertAlmostEqual(float(p), 1/3)

    def test_expand_emission_matrix(self):
        # First chord: 3 fingerings → column of ones, shape (3, 1)
        em = graph_utils.expand_emission_matrix(np.array([]), [1, 2, 3])
        self.assertEqual(em.shape, (3, 1))
        np.testing.assert_array_equal(em[:, 0], [1, 1, 1])

        # Second chord: 2 new fingerings → shape (5, 2)
        em = graph_utils.expand_emission_matrix(em, [4, 5])
        self.assertEqual(em.shape, (5, 2))
        self.assertEqual(em[3, 1], 1.0)   # new fingering emits obs 1
        self.assertEqual(em[4, 1], 1.0)
        self.assertEqual(em[0, 1], 0.0)   # old fingering does not

    def test_build_transition_matrix(self):
        fingerings = [(self.s0f1,), (self.s0f5,)]
        Tm = graph_utils.build_transition_matrix(self.positions, fingerings, self.weights, self.tuning)
        self.assertEqual(Tm.shape, (2, 2))
        for row in Tm:
            self.assertAlmostEqual(float(np.sum(row)), 1.0)
        self.assertTrue(np.all(Tm >= 0))

    def test_viterbi(self):
        Tm = np.array([[0.9, 0.1], [0.1, 0.9]])
        Em = np.array([[0.9, 0.1], [0.1, 0.9]])
        result = graph_utils.viterbi([0, 0, 0, 1, 1, 1], Tm, Em, np.array([0.5, 0.5]))
        self.assertEqual(list(result), [0, 0, 0, 1, 1, 1])

        # Single observation
        result_single = graph_utils.viterbi([0], Tm, Em, np.array([0.5, 0.5]))
        self.assertEqual(len(result_single), 1)
        self.assertEqual(result_single[0], 0)

    # -------------------------------------------------------------------------
    # Fretboard fingering logic
    # -------------------------------------------------------------------------

    def test_is_path_possible(self):
        note_arrays = [[self.s0f1], [self.s1f1]]
        # Different strings, adjacent frets → valid
        self.assertTrue(self.fretboard.is_fingering_possible(
            (self.s0f1, self.s1f1), note_arrays))
        # Same string → invalid
        self.assertFalse(self.fretboard.is_fingering_possible(
            (self.s0f1, self.s0f2), [[self.s0f1], [self.s0f2]]))

    def test_find_all_paths(self):
        # Single note: one fingering per fretboard position
        e4_opts = self.fretboard.get_specific_note_options(Note(64))  # 5 positions
        fingerings = self.fretboard.get_possible_fingerings([e4_opts])
        self.assertEqual(len(fingerings), len(e4_opts))
        for f in fingerings:
            self.assertEqual(len(f), 1)

        # Two notes: E4 + B3 — should produce valid two-note fingerings
        two_opts = self.fretboard.get_note_options([Note(64), Note(59)])
        fingerings_two = self.fretboard.get_possible_fingerings(two_opts)
        self.assertTrue(len(fingerings_two) > 0)
        for f in fingerings_two:
            self.assertEqual(len(f), 2)
            strings = [self.G.nodes[n]["pos"][0] for n in f]
            self.assertEqual(len(strings), len(set(strings)))  # no two notes on same string

    def test_fix_impossible_notes(self):
        fretboard = Fretboard(Tuning(["F#1", "E2"]))
        fretboard.tuning.nfrets = 10
        # Tuning bounds: 30 – 50

        notes = [Note(52), Note(46), Note(20), Note(30)]

        self.assertSameNotes(
            fretboard.fix_oob_notes(notes, preserve_highest_note=False),
            [Note(40), Note(46), Note(32), Note(30)]
        )
        self.assertSameNotes(
            fretboard.fix_oob_notes(notes, preserve_highest_note=True),
            [Note(40), Note(34), Note(32), Note(30)]
        )

    # -------------------------------------------------------------------------
    # Display helpers (smoke tests)
    # -------------------------------------------------------------------------

    def test_display_path_graph(self):
        pass  # requires display; skipped in headless CI

    def test_display_notes_on_graph(self):
        pass  # requires display; skipped in headless CI
