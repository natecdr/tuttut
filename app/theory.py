from enum import Enum
from sysconfig import get_path
import numpy as np
from app.utils import *

class Note: #Note class
  def __init__(self, degree, octave):
    self._degree = degree
    self._octave = octave

  @property 
  def degree(self):
    return self._degree

  @property
  def octave(self):
    return self._octave

  def __eq__(self, other):
    return isinstance(other, Note) and self.degree is other.degree and int(self.octave) == int(other.octave)

  def __hash__(self):
    return hash((self.degree, self.octave, id(self)))

  def __repr__(self):
    return self.degree.value + str(self.octave) + "-" + str(hash(self))[2:4]

class Degree(Enum): #Degree of a note enum
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

class Tuning: #Tuning class
  standard_tuning = [Note(Degree.E, 4), Note(Degree.B, 3), Note(Degree.G, 3), Note(Degree.D, 3), Note(Degree.A, 2), Note(Degree.E, 2)]

  def __init__(self, strings = standard_tuning):
    self._strings = np.array(strings, dtype = Note)
    self.nstrings = len(strings)

  @property
  def strings(self):
    return self._strings

class Beat: #Beat class
  def __init__(self, imeasure, ibeat, tab):
    self.ibeat = ibeat
    self.imeasure = imeasure
    self.tab = tab
    self.notes = None

  def populate(self, notes_to_add, midi, time_signature):
    resolution = midi.resolution
    measure_length = measure_length_ticks(midi, time_signature)

    nsep = max(4, len(notes_to_add)+1)

    self.notes = [[] for i in range(nsep)]
    
    for note in notes_to_add:
      tick = midi.time_to_tick(note.start) - self.ibeat*resolution - self.imeasure*measure_length
      # timing = int(np.ceil(tick/resolution*(nsep-1)))
      timing = int(tick/resolution*(nsep-1))
      self.notes[timing].append(note)

class Measure: #Measure class
  def __init__(self,tab, imeasure, time_signature):
    self.beats = np.empty(time_signature.numerator, dtype = Beat)
    self.imeasure = imeasure
    self.time_signature = time_signature
    self.tab = tab

  def populate(self, notes, imeasure, midi):
    measure_length = measure_length_ticks(midi, self.time_signature)
    beat_ticks = np.arange(imeasure*measure_length,imeasure*measure_length + measure_length, step=midi.resolution)
    
    for ibeat in range(len(self.beats)): 
      current_beat_tick = beat_ticks[ibeat]
      beat_start = current_beat_tick
      beat_end = current_beat_tick + midi.resolution
      beat_notes = get_notes_between(midi, notes, beat_start, beat_end)
      beat = Beat(imeasure, ibeat, self.tab)
      beat.populate(beat_notes, midi, self.time_signature)
      self.beats[ibeat] = beat

  def get_all_notes(self):
    notes = self.beats[0].notes
    
    for i in range(1, len(self.beats)):
      notes += self.beats[i].notes

    return notes