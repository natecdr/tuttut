from enum import Enum
import numpy as np
from app.utils import *

class Note:
  """Note object."""
  def __init__(self, degree, octave):
    """Constructor for the Note object.

    Args:
        degree (Degree): Degree of the note
        octave (int): Octave of the note
    """
    self._degree = degree
    self._octave = octave

  @property 
  def degree(self):
    """Returns the note's degree.

    Returns:
        Degree: Note's degree
    """
    return self._degree

  @property
  def octave(self):
    """Returns the note's octave.

    Returns:
        int: Note's octave
    """
    return self._octave

  def __eq__(self, other):
    """States the rules for whether or not 2 notes are equal.
    
    Two notes are considered equal if they are note objects and their degrees and octaves are the same.
    """
    return isinstance(other, Note) and self.degree is other.degree and int(self.octave) == int(other.octave)

  def __hash__(self):
    """Computes the hash for the Note."""
    return hash((self.degree, self.octave, id(self)))

  def __repr__(self):
    """Returns a representation of the Note."""
    return self.degree.value + str(self.octave) + "-" + str(hash(self))[2:4]

class Degree(Enum): #Degree of a note enum
  """Degree of a note enum."""
  __order__ = "A Asharp B C Csharp D Dsharp E F Fsharp G Gsharp"
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

class Tuning:
  """Tuning object."""
  standard_tuning = [Note(Degree.E, 4), Note(Degree.B, 3), Note(Degree.G, 3), Note(Degree.D, 3), Note(Degree.A, 2), Note(Degree.E, 2)]

  def __init__(self, strings = standard_tuning):
    """Constructor for the Tuning object.

    Args:
        strings (list, optional): List of notes corresponding to the string notes. Defaults to standard_tuning.
    """
    self._strings = np.array(strings, dtype = Note)
    self.nstrings = len(strings)

  @property
  def strings(self):
    """Returns the list of notes corresponding to the strings.

    Returns:
        list: List of notes corresponding to the string notes
    """
    return self._strings

class Beat: #Beat class
  def __init__(self, imeasure, ibeat, tab):
    self.ibeat = ibeat
    self.imeasure = imeasure
    self.tab = tab
    self.notes = None

  def populate(self, notes_to_add, midi, time_signature):
    measure_length = measure_length_ticks(midi, time_signature)

    self.notes = {}
    
    for note in notes_to_add:
      tick = midi.time_to_tick(note.start) - self.ibeat*midi.resolution - self.imeasure*measure_length
      timing = tick/midi.resolution + self.ibeat
      if timing in self.notes:
        self.notes[timing].append(note)
      else:
        self.notes[timing] = [note]

class Measure: #Measure class
  def __init__(self, tab, imeasure, time_signature):
    self.beats = np.empty(time_signature.numerator, dtype = Beat)
    self.imeasure = imeasure
    self.time_signature = time_signature
    self.tab = tab

  def populate(self, notes):
    midi = self.tab.midi
    measure_length = measure_length_ticks(midi, self.time_signature)
    beat_ticks = np.arange(self.imeasure*measure_length,self.imeasure*measure_length + measure_length, step=midi.resolution)
    
    for ibeat in range(len(self.beats)): 
      current_beat_tick = beat_ticks[ibeat]
      beat_start = current_beat_tick
      beat_end = current_beat_tick + midi.resolution
      beat_notes = get_notes_between(midi, notes, beat_start, beat_end)
      beat = Beat(self.imeasure, ibeat, self.tab)
      beat.populate(beat_notes, midi, self.time_signature)
      self.beats[ibeat] = beat

  def get_all_notes(self):
    notes = {}
    for beat in self.beats: 
      notes.update(beat.notes)

    return notes