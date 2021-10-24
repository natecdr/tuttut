from enum import Enum
import numpy as np
from utils import *

class Note:
  def __init__(self, degree, octave):
    self._degree = degree
    self._octave = octave

  @property 
  def degree(self):
    return self._degree

  @property
  def octave(self):
    return self._octave

class Degree(Enum):
  __order__ = "A Asharp B C Csharp D Dsharp E F Fsharp G Gsharp "
  A = "A"
  Asharp = "A#"
  B = "B"
  C = "C"
  Csharp = "C#"
  D = "D"
  Dsharp = "D#"
  E = "E"
  F = "F"
  Fsharp = "F#"
  G = "G"
  Gsharp = "G#"

standard_tuning = [Note(Degree.E, 4), Note(Degree.B, 3), Note(Degree.G, 3), Note(Degree.D, 3), Note(Degree.A, 2), Note(Degree.E, 2)]

class Tuning:
  def __init__(self, strings = standard_tuning):
    self._strings = np.array(strings, dtype = Note)
    self.nstrings = len(strings)

  @property
  def strings(self):
    return self._strings

class Beat:
  def __init__(self, imeasure, ibeat, tab):
    self.ibeat = ibeat
    self.imeasure = imeasure
    self.tab = tab
    self.notes = -np.ones((tab.nstrings,4), dtype = Note)
    self.notes2 = -np.ones(4, dtype = Note)

  def populate(self, notes_to_add, midi, time_signature):
    resolution = midi.resolution
    measure_length = measure_length_ticks(midi, time_signature)
    if len(notes_to_add) > 4:
      self.notes2 = -np.ones(len(notes_to_add)+1, dtype = Note)

    self.notes2 = [[] for note in self.notes2]
    
    for note in notes_to_add:
      tick = midi.time_to_tick(note.start) - self.ibeat*resolution - self.imeasure*measure_length
      timing = int(np.ceil(tick/resolution*len(notes_to_add)))
      self.notes2[timing].append(note)

  def __repr__(self):
    res = ""
    istring = 0
    for string in self.tab.tuning.strings:
      res += string.degree.value if len(string.degree.value)>1 else string.degree.value + " "
      res += "|"
      for j in range(self.notes.shape[1]):
        if self.notes[istring,j] != -1:
          res += "0"
        else: 
          res += "-"
      istring += 1
      res += "\n"

    return res

class Measure:
  def __init__(self,tab, imeasure, time_signature):
    self.beats = np.empty(time_signature.denominator, dtype = Beat)
    self.imeasure = imeasure
    self.time_signature = time_signature
    self.tab = tab

  def populate(self, notes, imeasure, midi):
    measure_length = measure_length_ticks(midi, self.time_signature)
    beat_ticks = np.arange(imeasure*measure_length,imeasure*measure_length + measure_length, step=midi.resolution)
    for ibeat in range(self.time_signature.denominator):
      current_beat_tick = beat_ticks[ibeat]
      beat_notes = get_notes_between(midi, notes, current_beat_tick, current_beat_tick + midi.resolution)
      beat = Beat(imeasure, ibeat, self.tab)
      beat.populate(beat_notes, midi, self.time_signature)
      self.beats[ibeat] = beat

  def get_all_notes(self):
    notes = self.beats[0].notes2
    
    for i in range(1, len(self.beats)):
      notes += self.beats[i].notes2

    return notes

  def __repr__(self):
    notes = self.get_all_notes()

    res = ""
    istring = 0
    for string in self.tab.tuning.strings:
      res += string.degree.value if len(string.degree.value)>1 else string.degree.value + " "
      res += "|"
      for j in range(notes.shape[1]):
        if notes[istring,j] != -1:
          res += "0"
        else: 
          res += "-"
      istring += 1
      res += "\n"

    return res

  def to_string(self, init_array):
    res = init_array.copy()
    all_notes = self.get_all_notes()
    for istring in range(self.tab.nstrings):
      for timing, notes in enumerate(all_notes):
        if notes: #if notes contains one or more notes at a specific timing
          res[istring] += str(note_to_fret(self.tab.tuning.strings[istring],midi_note_to_note(notes[0])))
        else: 
          res[istring] += "-"
      res[istring] += "|"

    return res


