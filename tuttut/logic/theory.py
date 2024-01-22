from enum import Enum
import numpy as np
import tuttut.logic.midi_utils as midi_utils
from pretty_midi import note_number_to_name, note_name_to_number
from collections import defaultdict

class Note:
  """Note object."""
  def __init__(self, pitch : int):
    """Constructor for the Note object.

    Args:
        pitch (int) : MIDI note number of the note
    """

    self.pitch = pitch
    self.name = note_number_to_name(pitch)
    self.degree = self.name[:-1]
    self.octave = self.name[-1]

  def __eq__(self, other):
    """States the rules for whether or not 2 notes are equal.
    
    Two notes are considered equal if they are note objects and their degrees and octaves are the same.
    """
    return isinstance(other, Note) and self.pitch == other.pitch
  
  def __hash__(self):
    """Computes the hash for the Note."""
    return hash((self.name, id(self)))

  def __repr__(self):
    """Returns a representation of the Note."""
    return self.name + "-" + str(hash(self))[2:4]

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
  standard_tuning = ["E4", "B3", "G3", "D3", "A2", "E2"]
  standard_ukulele_tuning = ["A4", "E4", "C4", "G4"]

  def __init__(self, strings = standard_tuning):
    """Constructor for the Tuning object.

    Args:
        strings (list, optional): List of notes corresponding to the string notes. Defaults to standard_tuning.
    """
    self._strings = np.array([Note(note_name_to_number(note)) for note in strings]) #Thin to thick
    self.nstrings = len(strings)
    self.nfrets = 20

  @property
  def strings(self):
    """Returns the list of notes corresponding to the strings.

    Returns:
        list: List of notes corresponding to the string notes
    """
    return self._strings
  
  def get_all_possible_notes(self):
    """Returns all possible_notes on a fretboard for k strings and n frets.

    Args:
        tuning (Tuning): Tuning object
        nfrets (int, optional): Number of frets. Defaults to 20.

    Returns:
        list: All possible notes for the specified fretboard parameters
    """
    res = []
    for string in self.strings:
      string_notes = []
      for ifret in range(self.nfrets + 1): # + 1 to take into account fret 0
        string_notes.append(Note(string.pitch + ifret))
      res.append(string_notes)

    return res
  
  def get_pitch_bounds(self):
    min_pitch = min([string.pitch for string in self.strings])
    max_pitch = max([string.pitch for string in self.strings]) + self.nfrets
    
    return min_pitch, max_pitch

class Measure: 
  """Measure class."""
  def __init__(self, tab, imeasure, time_signature, measure_start, measure_end):
    """Constructor for the Measure object.

    Args:
        tab (Tab): Tab object
        imeasure (int): Measure number in the song
        time_signature (pretty_midi.TimeSignature): Current time signature of the song
    """
    self.imeasure = imeasure
    self.time_signature = time_signature
    self.tab = tab
    
    self.measure_start = measure_start
    self.measure_end = measure_end
    
    self.timeline = midi_utils.get_events_between(self.tab.timeline, measure_start, measure_end)

  @property
  def duration_ticks(self):
    return self.measure_end - self.measure_start