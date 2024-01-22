import pretty_midi
import tuttut.logic.theory as theory
# from app.graph_utils import 

def measure_length_ticks(midi, time_signature): 
  """Returns the number of ticks in a measure for a midi file.

  Args:
      midi (pretty_midi.PrettyMIDI): MIDI object
      time_signature (pretty_midi.TimeSignature): Current time signature 

  Returns:
      int: Duration of one measure in ticks
  """
  n_quarter_notes = time_signature.numerator * (4/time_signature.denominator)
  measure_length = n_quarter_notes * midi.resolution 
  return measure_length

def get_notes_between(midi, notes, begin, end):
  """Return all notes between two specific timings in a midi file.

  Args:
      midi (pretty_midi.PrettyMIDI): MIDI object
      notes (list): Notes to search in
      begin (int): Timing of the lower bound in ticks
      end (int): Timing of the upper bound in ticks

  Returns:
      list: Notes between the lower and upper bounds
  """
  res = []
  for note in notes:
    note_start_ticks = midi.time_to_tick(note.start)
    if note_start_ticks >= begin and note_start_ticks < end:
      res.append(note)

  return res

def get_non_drum(instruments):
  """Returns all instruments that are non-drums.

  Args:
      instruments (list): List of pretty_midi.Instrument objects in the MIDI

  Returns:
      list: List of non-drum instruments
  """
  return [instrument for instrument in instruments if not instrument.is_drum]

def fill_measure_str(str_array):
  """Fills column of a measure so that all strings are of equal length.

  Args:
      str_array (list): List of the strings (text) representing the guitar strings

  Returns:
      list: New updated list of strings
  """
  maxlen = len(max(str_array, key = len))
  res = []
  for str in str_array:
    res.append(str.ljust(maxlen, "-"))
  return res
  
def sort_notes_by_tick(notes):
  """Returns sorted notes by tick.

  Args:
      notes (list): List of notes to sort 

  Returns:
      list: New sorted list of notes
  """
  return sorted(notes, key = lambda n: n.start)
  
def round_to_multiple(n, base=10):
  """Rounds a number to the closest multiple of a base.

  Args:
      n (int): Number to round
      base (int, optional): Multiple base to round to. Defaults to 10.

  Returns:
      int: Rounded number
  """
  return int(base * round(n/base))

def quantize(midi):
  """Quantizes a MIDI object.

  Args:
      midi (pretty_midi.PrettyMIDI): MIDI object to quantize
  """
  quantization_factor = 32
  
  for instrument in midi.instruments:
      quantized_notes = []
      for note in instrument.notes:
          rounded = round_to_multiple(midi.time_to_tick(note.start), base=midi.resolution/quantization_factor)
          quantized_notes.append(pretty_midi.Note(velocity = note.velocity, pitch = note.pitch, start = midi.tick_to_time(rounded), end=note.end))

      instrument.notes = quantized_notes
      
def transpose_note(note, semitones):
    return theory.Note(note.pitch + semitones)

def remove_duplicate_notes(notes):
  pitches = []
  res_notes = []
  for note in notes:
    if not note.pitch in pitches:
      pitches.append(note.pitch)
      res_notes.append(note)
      
  return res_notes

def sort_notes_by_pitch(notes):
  return sorted(notes, key = lambda n: n.pitch)

def get_events_between(timeline, start_ticks, end_ticks):
    return {key: timeline[key] for key in timeline.keys() if start_ticks <= key < end_ticks}