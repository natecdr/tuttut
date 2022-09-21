import numpy as np
from pretty_midi.containers import TimeSignature
from app.theory import Measure
from app.utils import *
import networkx as nx

class Tab:
  def __init__(self, name, tuning, midi):
    quantize(midi)
    self.name = name
    self.tuning = tuning
    self.time_signatures = midi.time_signature_changes if len(midi.time_signature_changes) > 0 else [TimeSignature(4, 4, 0)]
    self.nstrings = len(tuning.strings)
    self.measures = []
    self.midi = midi
    self.graph = self.build_complete_graph()

  def populate(self):
    for i,time_signature in enumerate(self.time_signatures):
      measure_length = measure_length_ticks(self.midi, time_signature)
      time_sig_start = time_signature.time
      time_sig_end = self.time_signatures[i+1].time if i < len(self.time_signatures)-1 else self.midi.time_to_tick(self.midi.get_end_time())
      measure_ticks = np.arange(time_sig_start, time_sig_end, measure_length)

      for imeasure, measure_tick in enumerate(measure_ticks):
        notes = []
        for instrument in get_non_drum(self.midi.instruments):
          notes = np.concatenate((notes, get_notes_between(self.midi, instrument.notes, measure_tick, measure_tick + measure_length))) 
        notes = sort_notes_by_tick(notes)
        measure = Measure(self, imeasure, time_signature)
        measure.populate(notes, imeasure, self.midi)
        self.measures.append(measure)

  def get_all_notes(self):
    notes = self.measures[0].get_all_notes()
    for i in range(1, len(self.measures)):
      notes = np.concatenate((notes, self.measures[i].get_all_notes()), axis = 1)
    return notes
    
  def build_complete_graph(self):
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
    res = []
    for string in self.tuning.strings:
      s = string.degree.value
      s += "||" if len(string.degree.value)>1 else " ||"
      res.append(s)

    for measure in self.measures:
      res = measure.to_string(res)

    return res

  def to_file(self):
    notes_str = self.to_string()

    with open(f"./tabs/{self.name}.txt","w") as file:
      for string_notes in notes_str:
        file.write(string_notes + "\n")

  def __repr__(self):
    res = ""
    notes_str = self.to_string()
    for string_notes in notes_str:
      res += string_notes + "\n"

    return res
