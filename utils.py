import pretty_midi
from pretty_midi.utilities import note_name_to_number
import theory
import math
import networkx as nx
import matplotlib.pyplot as plt

def note_number_to_note(note_number):
  note = str(pretty_midi.note_number_to_name(note_number))
  (degree, octave) = (note[:-1], note[-1:]) if not '-' in note else (note[:-2], note[-2:])
  degree = theory.Degree(degree)
  
  return theory.Note(degree, octave)

def midi_note_to_note(note):
  return note_number_to_note(note.pitch)

def measure_length_ticks(midi, time_signature):
  measure_length = midi.time_to_tick(midi.get_beats()[time_signature.denominator])
  return measure_length

def get_notes_between(midi, notes, begin, end):
  res = []
  for note in notes:
    start = midi.time_to_tick(note.start)
    if start >= begin and start< end:
      res.append(note)

  return res
  
def note_to_fret(string, note):
  string_name = string.degree.value + str(string.octave)
  note_name = note.degree.value + str(note.octave)
  n_string = pretty_midi.note_name_to_number(string_name)
  n_note = pretty_midi.note_name_to_number(note_name)

  return n_note - n_string

def get_non_drum(instruments):
  res = []
  for instrument in instruments:
    if not instrument.is_drum:
      res.append(instrument)
  return res

def get_all_possible_notes(tuning, nfrets = 20):
  nstrings = len(tuning.strings)
  res = []
  for string in tuning.strings:
    string_note_number = note_name_to_number(string.degree.value + str(string.octave))
    string_notes = []
    for ifret in range(nfrets):
      string_notes.append(note_number_to_note(string_note_number+ifret))
    res.append(string_notes)
  
  return res

def distance_between(x, y):
  return math.dist(x,y)

def get_notes_in_graph(G, note):
  nodes = list(G.nodes)
  res = []
  for node in nodes:
    if node == note:
      res.append(node)
  return res

def build_path_graph(G, note_arrays):
  res = nx.DiGraph()

  for x, note_array in enumerate(note_arrays):
    for y, possible_note in enumerate(note_array):
      res.add_node(possible_note, pos = (x, y))

  for idx, note_array in enumerate(note_arrays):
    for possible_note in note_array:
      if idx < len(note_arrays)-1:
        for possible_target_note in note_arrays[idx+1]:
          res.add_edge(possible_note, possible_target_note, distance = G[possible_note][possible_target_note]["distance"])

  return res

def find_shortest_path(path_graph, note_arrays):
  shortest_path = None

  # edge_labels = nx.get_edge_attributes(path_graph,'distance')
  # pos=nx.get_node_attributes(path_graph,'pos')
  # nx.draw(path_graph, pos, with_labels=True)
  # nx.draw_networkx_edge_labels(path_graph, pos, edge_labels = edge_labels)
  # plt.show()

  for possible_source_node in note_arrays[0]:
    for possible_target_node in note_arrays[-1]: 
      try:
        path = nx.shortest_path(path_graph, possible_source_node, possible_target_node, weight = "distance")
        if not shortest_path or path < shortest_path:
          shortest_path = path
      except nx.NetworkXNoPath:
        #print("No path ???")
        pass

  return shortest_path
  
def fill_measure_str(str_array):
  maxlen = len(max(str_array, key = len))
  res = []
  for str in str_array:
    res.append(str.ljust(maxlen, "-"))
  return res

if __name__ == "__main__":
  pass
  
