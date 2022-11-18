import traceback
import numpy as np
from pretty_midi.containers import TimeSignature
from app.theory import Measure
from app.utils import *
import networkx as nx
import json
import os

class Tab:
  """Tab object."""
  def __init__(self, name, tuning, midi):
    """Constructor for the Tab object.

    Args:
        name (string): Name of the tab
        tuning (Tuning): Tuning of the instrument for the tab
        midi (pretty_midi.PrettyMIDI): The MIDI we're trying to convert to tab
    """
    quantize(midi)
    
    self.name = name
    self.tuning = tuning
    self.time_signatures = midi.time_signature_changes if len(midi.time_signature_changes) > 0 else [TimeSignature(4, 4, 0)]
    self.nstrings = len(tuning.strings)
    self.measures = []
    self.midi = midi
    self.graph = self._build_complete_graph()
    
    self.populate()
    
    self.tab = self.gen_tab()

  def populate(self):
    """Populates tab with Measures."""
    for i,time_signature in enumerate(self.time_signatures):
      measure_length = measure_length_ticks(self.midi, time_signature)
      time_sig_start = time_signature.time
      time_sig_end = self.time_signatures[i+1].time if i < len(self.time_signatures)-1 else self.midi.time_to_tick(self.midi.get_end_time())
      measure_ticks = np.arange(time_sig_start, time_sig_end, measure_length)

      for imeasure, measure_tick in enumerate(measure_ticks):
        notes = []
        for instrument in get_non_drum(self.midi.instruments):
          measure_start = measure_tick
          measure_end = measure_start + measure_length
          notes = np.concatenate((notes, get_notes_between(self.midi, instrument.notes, measure_start, measure_end)))
        notes = sort_notes_by_tick(notes)
        measure = Measure(self, imeasure, time_signature)
        measure.populate(notes)
        self.measures.append(measure)

  def _build_complete_graph(self):
    """Builds the complete graph representing the fretboard.
    
    Each fret for each string is a node, each node is connected to all the others.
    Each edge contains the distance between their 2 nodes as their weight.

    Returns:
        nx.Graph: Graph representing the fretboard
    """
    note_map = get_all_possible_notes(self.tuning)

    complete_graph = nx.Graph()
    for istring, string in enumerate(note_map):
      for inote, note in enumerate(string):
        complete_graph.add_node(note, pos = (istring, inote))

    complete_graph_nodes = list(complete_graph.nodes(data=True))

    for node in complete_graph_nodes:
      for node_to_link in complete_graph_nodes:
        if not node is node_to_link:
          if node_to_link[1]['pos'][1] == 0:
            dst = 0
          else:
            dst = distance_between(node[1]['pos'], node_to_link[1]['pos'])
          complete_graph.add_edge(node[0], node_to_link[0], distance = dst)

    return complete_graph

  def to_string(self):
    """Generates the text for the ascii tabs.

    Returns:
        list: List containing tab text for each guitar string
    """
    res = []
    for string in self.tuning.strings:
      header = string.degree.value
      header += "||" if len(header)>1 else " ||"
      res.append(header)

    for measure in self.tab["measures"]:
      for ievent, event in enumerate(measure["events"]):
        if "notes" in event:
          for note in event["notes"]:
            string, fret = note["string"], note["fret"]
            res[string] += str(fret)

        next_event_timing = measure["events"][ievent + 1]["measure_timing"] if ievent < len(measure["events"]) - 1 else 1.0
        dashes_to_add = max(1, math.floor((next_event_timing - event["measure_timing"]) * 16))

        res = fill_measure_str(res)

        for istring in range(self.nstrings):
          res[istring] += "-" * dashes_to_add

      for istring in range(self.nstrings):
        res[istring] += "|"

    return res

  def gen_tab(self):
    """Generates the tab data and the fingerings."""
    tab = {"measures":[]}

    time_sig_index = -1

    present_notes = []
    notes_sequence = []

    present_fingerings = []

    emission_matrix = np.array([])

    for imeasure, measure in enumerate(self.measures):
      print(f"{imeasure}/{len(self.measures)}")
      res_measure = {"events":[]}

      all_notes = measure.get_all_notes()

      for timing, notes in all_notes.items():
        ts_change = False
        if notes: #if notes contains one or more notes at a specific timing
          start_time = notes[0].start
          start_time_ticks = int(self.midi.time_to_tick(start_time))

          note_arrays = []
          for note in notes:
            note = midi_note_to_note(note)
            note_arrays.append(get_notes_in_graph(self.graph, note))

          try:
            notes_pitches = tuple([note.pitch for note in notes])

            if notes_pitches not in present_notes:
              all_paths = find_all_paths(self.graph, note_arrays)
              present_notes.append(notes_pitches)
              present_fingerings += all_paths

              emission_matrix = expand_emission_matrix(emission_matrix, all_paths)

            notes_sequence.append(present_notes.index(notes_pitches))
          except Exception as e:
            print(traceback.print_exc())
            print("Note arrays :", note_arrays)
            print("Notes :", notes)
            print(midi_note_to_note(notes[0]))
            print("Measure no.", imeasure)
            print("")

          if time_sig_index+1 < len(self.time_signatures) and self.time_signatures[time_sig_index+1].time <= start_time:
            time_sig_index += 1
            ts = self.time_signatures[time_sig_index]
            ts_change = True

          event = self.build_event(start_time, start_time_ticks, timing, ts, ts_change)

        res_measure["events"].append(event)

      tab["measures"].append(res_measure)

    transition_matrix = build_transition_matrix(self.graph, present_fingerings)

    sequence_indices = viterbi(notes_sequence, transition_matrix, emission_matrix)
    sequence_indices = [int(i) for i in sequence_indices]

    final_sequence = np.array(present_fingerings, dtype=object)[sequence_indices]

    tab = self.populate_tab_notes(tab, final_sequence)
    
    return tab

  def populate_tab_notes(self, tab, sequence):
    """Populates the tab template with notes and their fingerings.

    Args:
        tab (dict): The tab template without notes
        sequence (list): Sequence of notes and fingerings to be used

    Returns:
        dict: The final tab with notes and fingerings
    """
    ievent = 0
    for measure in tab["measures"]:
      for event in measure["events"]:
        for path_note in sequence[ievent]:
          string, fret = self.graph.nodes[path_note]["pos"]   
          event["notes"].append({
            "degree": str(path_note.degree),
            "octave": int(path_note.octave),
            "string": string,
            "fret": fret
            })
        ievent += 1
        
    return tab

  def build_event(self, start_time, start_time_ticks, timing, ts, ts_change):
    """Builds the template for an event in the tab.

    Args:
        start_time (float): Time of occurence of the event in seconds
        start_time_ticks (int): Time of occurence of the event in ticks
        timing (float): Timing of the event within the measure
        ts (pretty_midi.TimeSignature): Current time signature at the time of the event
        ts_change (bool): If the time signature has changed in the current event

    Returns:
        dict: Template for the event.
    """
    event = {"time":start_time,
            "measure_timing":None,
            "time_ticks":start_time_ticks,
            "notes":[]}

    if ts_change:
      event["time_signature_change"] = [ts.numerator, ts.denominator]

    event["measure_timing"] = timing/ts.numerator

    return event

  def to_json(self):
    """Exports the tab to a json file."""
    if self.tab is None:
      return

    json_object = json.dumps(self.tab, indent=4)

    with open(os.path.join("json", self.name + ".json"), "w") as outfile:
        outfile.write(json_object)

  def to_ascii(self):
    """Exports the tab to a text file."""
    if self.tab is None:
      return

    notes_str = self.to_string()

    with open(f"./tabs/{self.name}.txt","w") as file:
      for string_notes in notes_str:
        file.write(string_notes + "\n")

  def __repr__(self):
    """Used to print out the tab.

    Returns:
        str: String representation of the tab.
    """
    return self.tab
