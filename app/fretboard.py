import traceback
import numpy as np
from pretty_midi.containers import TimeSignature
from app.theory import Measure, Note
from app.midi_utils import *
from app.graph_utils import *
import networkx as nx
import json
import os
from pathlib import Path

class Fretboard:
    def __init__(self, tuning):
        self.tuning = tuning
        self.graph = self._build_complete_graph()

    def _build_complete_graph(self):
        """Builds the complete graph representing the fretboard.
        
        Each fret for each string is a node, each node is connected to all the others.
        Each edge contains the distance between their 2 nodes as their weight.

        Returns:
            nx.Graph: Graph representing the fretboard
        """
        note_map = self.tuning.get_all_possible_notes()

        complete_graph = nx.Graph()
        for istring, string in enumerate(note_map):
            for inote, note in enumerate(string):
                complete_graph.add_node(note, pos = (istring, inote))

        complete_graph_nodes = list(complete_graph.nodes(data=True))

        for node in complete_graph_nodes:
            for node_to_link in complete_graph_nodes:
                dst = 0 if node_to_link[1]['pos'][1] == 0 else distance_between(node[1]['pos'], node_to_link[1]['pos'])
                complete_graph.add_edge(node[0], node_to_link[0], distance = dst)
            
        return complete_graph
    
    def get_note_options(self, notes):
        """Returns note arrays from a list of theory.Notes"""
        note_options =[get_notes_in_graph(self.graph, note) for note in notes]
        note_options = [note_array for note_array in note_options if len(note_array) > 0]
        
        return note_options
    
    def get_possible_fingerings(self, note_options): 
        """Returns all possible fingerings in a path graph

        Args:
            G (networkx.Graph): Fretboard graph
            note_arrays (list): List of possible positions for the notes

        Returns:
            list: List of paths
        """
        fingerings = []
        
        if len(note_options) == 1:
            return [(note,) for note in note_options[0]]

        for note_options_permutation in list(itertools.permutations(note_options)):
            path_graph = build_path_graph(self.graph, note_options_permutation)
            # display_path_graph(path_graph)
            for possible_source_node in note_options_permutation[0]:
                permutation_fingerings = nx.all_simple_paths(path_graph, possible_source_node, target=note_options_permutation[-1])
                for fingering in permutation_fingerings:
                    if not is_path_already_checked(fingerings, fingering) and is_path_possible(self.graph, fingering, note_options_permutation):
                        fingerings.append(tuple(fingering))
                    
        return fingerings