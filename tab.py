import numpy as np
from pretty_midi.containers import TimeSignature
from theory import Measure
from utils import measure_length_ticks, get_notes_between, get_non_drum
import networkx as nx

class Tab:
  def __init__(self, name, tuning, midi):
    self.name = name
    self.tempo = midi.estimate_tempo()
    self.tuning = tuning
    self.time_signatures = midi.time_signature_changes if len(midi.time_signature_changes) > 0 else [TimeSignature(4, 4, 0)]
    self._nstrings = len(tuning.strings)
    self.measures = []
    self.midi = midi
    self.graph = self.build_graph(tuning)

  def populate(self):
    for i,time_signature in enumerate(self.time_signatures):
      measure_length = measure_length_ticks(self.midi, time_signature)
      for instrument in get_non_drum(self.midi.instruments):
        time_sig_start = time_signature.time
        time_sig_end = self.time_signatures[i+1].time if i < len(self.time_signatures)-1 else self.midi.time_to_tick(self.midi.get_end_time())
        measure_ticks = np.arange(time_sig_start, time_sig_end, measure_length)
        for imeasure, measure_tick in enumerate(measure_ticks):
          notes = get_notes_between(self.midi, instrument.notes, measure_tick, measure_tick + measure_length)
          measure = Measure(self,imeasure, time_signature)
          measure.populate(notes, imeasure, self.midi)
          self.measures.append(measure)

  @property 
  def nstrings(self):
    return self._nstrings

  def get_all_notes(self):
    notes = self.measures[0].get_all_notes()
    for i in range(1, len(self.measures)):
      notes = np.concatenate((notes, self.measures[i].get_all_notes()), axis = 1)
    return notes

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
    
  def build_graph(self, tuning):
    G = nx.generators.classic.complete_graph(25)
    return G

  def __repr__(self):
    res = ""
    notes_str = self.to_string()
    for string_notes in notes_str:
      res += string_notes + "\n"

    return res
