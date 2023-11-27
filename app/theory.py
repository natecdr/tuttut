from enum import Enum
import numpy as np
import app.midi_utils as midi_utils
import app.theory as theory
from pretty_midi import note_number_to_name

class Note:
  """Note object."""
  def __init__(self, pitch):
    """Constructor for the Note object.

    Args:
        degree (Degree): Degree of the note
        octave (int): Octave of the note
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
  standard_tuning = [Note(64), Note(59), Note(55), Note(50), Note(45), Note(40)]
  standard_ukulele_tuning = [Note(69), Note(64), Note(60), Note(67)]

  def __init__(self, strings = standard_tuning):
    """Constructor for the Tuning object.

    Args:
        strings (list, optional): List of notes corresponding to the string notes. Defaults to standard_tuning.
    """
    self._strings = np.array(strings)
    self.nstrings = len(strings)

  @property
  def strings(self):
    """Returns the list of notes corresponding to the strings.

    Returns:
        list: List of notes corresponding to the string notes
    """
    return self._strings
  
  def get_all_possible_notes(self, nfrets = 20):
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
      for ifret in range(nfrets):
        string_notes.append(theory.Note(string.pitch + ifret))
      res.append(string_notes)

    return res

class Beat:
  """Beat object."""
  def __init__(self, imeasure, ibeat, tab):
    """Constructor for the Beat object.

    Args:
        imeasure (int): Measure number in the song
        ibeat (int): Beat number in the measure
        tab (Tab): Tab object
    """
    self.ibeat = ibeat
    self.imeasure = imeasure
    self.tab = tab
    self.notes = None

  def populate(self, notes_to_add, midi, time_signature):
    """Populates the Beat with its corresponding notes.

    Args:
        notes_to_add (list): List of notes to add to the beat
        midi (pretty_midi.PrettyMIDI): MIDI object
        time_signature (pretty_midi.TimeSignature): Current time signature of the song
    """
    measure_length = midi_utils.measure_length_ticks(midi, time_signature)

    self.notes = {}
    
    for note in notes_to_add:
      tick = midi.time_to_tick(note.start) - self.ibeat*midi.resolution - self.imeasure*measure_length
      timing = tick/midi.resolution + self.ibeat
      if timing in self.notes:
        self.notes[timing].append(note)
      else:
        self.notes[timing] = [note]

class Measure: #Measure class
  """Measure object."""
  def __init__(self, tab, imeasure, time_signature):
    """Constructor for the Measure object.

    Args:
        tab (Tab): Tab object
        imeasure (int): Measure number in the song
        time_signature (pretty_midi.TimeSignature): Current time signature of the song
    """
    self.beats = np.empty(time_signature.numerator, dtype = Beat)
    self.imeasure = imeasure
    self.time_signature = time_signature
    self.tab = tab

  def populate(self, notes):
    """Populates the Measure with beats.

    Args:
        notes (list): Notes to add to the beats
    """
    midi = self.tab.midi
    measure_length = midi_utils.measure_length_ticks(midi, self.time_signature)
    beat_ticks = np.arange(self.imeasure*measure_length,self.imeasure*measure_length + measure_length, step=midi.resolution)
    
    for ibeat in range(len(self.beats)): 
      current_beat_tick = beat_ticks[ibeat]
      beat_start = current_beat_tick
      beat_end = current_beat_tick + midi.resolution
      beat_notes = midi_utils.get_notes_between(midi, notes, beat_start, beat_end)
      beat = Beat(self.imeasure, ibeat, self.tab)
      beat.populate(beat_notes, midi, self.time_signature)
      self.beats[ibeat] = beat

  def get_all_notes(self):
    """Returns all notes in the measure.

    Returns:
        list: All notes in the measure's beats
    """
    notes = {}
    for beat in self.beats: 
      notes.update(beat.notes)

    return notes