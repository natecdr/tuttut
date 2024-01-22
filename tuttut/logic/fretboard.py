import traceback
import numpy as np
from pretty_midi.containers import TimeSignature
from tuttut.logic.theory import Measure, Note
from tuttut.logic.midi_utils import *
from tuttut.logic.graph_utils import *
import networkx as nx
import json
import os
from pathlib import Path

class Fretboard:
    def __init__(self, tuning):
        self.tuning = tuning
        self.nstrings = tuning.nstrings
        self.scale_length = 650
        self.G = self._build_complete_graph()

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
                dst = 0 if node_to_link[1]['pos'][1] == 0 else self.distance_between(node[1]['pos'], node_to_link[1]['pos'])
                complete_graph.add_edge(node[0], node_to_link[0], distance = dst)
            
        return complete_graph
    
    def get_note_options(self, notes):
        """Returns note arrays from a list of theory.Notes"""
        note_options =[self.get_specific_note_options(note) for note in notes]
        note_options = [note_array for note_array in note_options if len(note_array) > 0]
        
        return note_options
    
    def get_specific_note_options(self, note):
        """Get all nodes that correspond to a specific note in a graph.

        Args:
            note (Note): Note to find on the fretboard

        Returns:
            list: List of nodes thar play the specified note
        """
        nodes = list(self.G.nodes)

        return [node for node in nodes if node == note]
    
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
            path_graph = build_path_graph(self.G, note_options_permutation)
            # display_path_graph(path_graph)
            for possible_source_node in note_options_permutation[0]:
                permutation_fingerings = nx.all_simple_paths(path_graph, possible_source_node, target=note_options_permutation[-1])
                for fingering in permutation_fingerings:
                    if not is_path_already_checked(fingerings, fingering) and self.is_fingering_possible(fingering, note_options_permutation):
                        fingerings.append(tuple(fingering))
                    
        return fingerings
    
    def fix_oob_notes(self, notes, preserve_highest_note = False):
        min_possible_pitch, max_possible_pitch = self.tuning.get_pitch_bounds()
        
        if preserve_highest_note:
            highest_pitch_before = max([note.pitch for note in notes])
            
            if highest_pitch_before > max_possible_pitch:
                highest_pitch_semitones_above_max = max(highest_pitch_before - max_possible_pitch, 0)
                highest_pitch_after = highest_pitch_before - (math.ceil(highest_pitch_semitones_above_max/12) * 12)
            else:
                highest_pitch_semitones_below_max = max(min_possible_pitch - highest_pitch_before, 0)
                highest_pitch_after = highest_pitch_before + (math.ceil(highest_pitch_semitones_below_max/12) * 12)
            
            #Highest pitch after processing (n octaves below highest before processing)
            max_possible_pitch = highest_pitch_after
        
        res_notes = []
        
        for note in notes:
            n_octaves_to_adjust = 0
            
            if note.pitch > max_possible_pitch:
                semitones_above_max = max(note.pitch - max_possible_pitch, 0)
                n_octaves_to_adjust = - math.ceil(semitones_above_max/12)
            
            if note.pitch < min_possible_pitch:
                semitones_below_min = max(min_possible_pitch - note.pitch, 0)
                n_octaves_to_adjust = math.ceil(semitones_below_min/12)
            
            new_note = transpose_note(note, n_octaves_to_adjust * 12)
            
            if new_note.pitch >= min_possible_pitch and new_note.pitch <= max_possible_pitch:
                res_notes.append(new_note)
            
        return remove_duplicate_notes(res_notes)  
    
    def distance_between(self, p1, p2):
        """Computes the distance between two points on the fretboard. 
        Distance between 2 strings is assumed to be 1/6.

        Args:
            x (tuple): Source point
            y (tuple): Destination point

        Returns:
            float: Distance between the two points
        """
        p1 = (p1[0]/self.nstrings, p1[1])
        p2 = (p2[0]/self.nstrings, p2[1])
        return math.dist(p1,p2)
    
    def get_fret_distance(self, nfret):
        """Returns the distance of the fret from the nut.

        Args:
            nfret (int): Number of the fret

        Returns:
            float: Distance of the fret from the nut
        """
        res = 0
        remaining_scale_length = self.scale_length
        
        for _ in range(nfret):
            fret_height = remaining_scale_length / 17.817
            res += fret_height
            remaining_scale_length -= fret_height
            
        return res
    
    def is_edge_possible(self, possible_note, possible_target_note):
        """Checks if a connection is possible between 2 nodes

        Args:
            possible_note (Note): Source note
            possible_target_note (Note): Target note
            G (networkx.Graph): Fretboard graph

        Returns:
            bool: Possibility of the connection
        """
        is_distance_possible = self.G[possible_note][possible_target_note]["distance"] < 6
        is_different_string = self.G.nodes[possible_note]["pos"][0] != self.G.nodes[possible_target_note]["pos"][0]
        return is_distance_possible and is_different_string
    
    def is_fingering_possible(self, fingering, note_arrays):
        """Checks if path is possible and playable.

        Args:
            G (networkx.Graph): Fretboard graph
            path (tuple): Notes path
            note_arrays (list): List of possible positions for the notes

        Returns:
            bool: If the path is possible and playable
        """
        #No 2 fingers on a single string
        plucked_strings = [self.G.nodes[note]["pos"][0] for note in fingering]
        one_per_string = len(plucked_strings) == len(set(plucked_strings))

        #No more than 5 fret span
        used_frets = [self.G.nodes[note]["pos"][1] for note in fingering if self.G.nodes[note]["pos"][1] != 0]
        max_fret_span = (max(used_frets) - min(used_frets)) < 5 if len(used_frets) > 0 else True

        #Path doesn't visit more nodes than necessary
        right_length = len(fingering) <= len(note_arrays)

        return one_per_string and max_fret_span and right_length
    
    def display_fingering_on_graph(self, fingering):
        """Displays notes played on a plt graph.

        Args:
            G (networkx.Graph): Fretboard graph
            path (tuple): Path to display
        """
        pos = nx.get_node_attributes(self.G,'pos')
        plt.figure(figsize=(2,6))
        nx.draw(self.G, pos)
        nx.draw(self.G.subgraph(fingering), pos = pos, node_color="red")
        plt.show()
        
    def display_complete_graph(self):
        positions = nx.get_node_attributes(self.G, "pos")
        nx.draw(self.G, pos=positions)
        plt.show()