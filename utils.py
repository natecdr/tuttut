import pretty_midi
import theory

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

def get_all_possible_notes():
  pass


if __name__== "__main__":
  for i in range(100):
    print(i, note_number_to_note(i).degree)
