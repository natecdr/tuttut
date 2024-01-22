import traceback
import numpy as np
from pretty_midi.containers import TimeSignature
from tuttut.logic.theory import Measure, Note
from tuttut.logic.fretboard import Fretboard
from tuttut.logic.midi_utils import *
from tuttut.logic.graph_utils import *
import networkx as nx
import json
import os
from pathlib import Path
from time import time

class Tab:
  """Tab object."""
  def __init__(self, name, tuning, midi, output_dir = None, weights = None):
    """Constructor for the Tab object.

    Args:
        name (string): Name of the tab
        tuning (Tuning): Tuning of the instrument for the tab
        midi (pretty_midi.PrettyMIDI): The MIDI we're trying to convert to tab
    """
    # quantize(midi)
    
    self.name = name
    self.tuning = tuning
    self.time_signatures = midi.time_signature_changes if len(midi.time_signature_changes) > 0 else [TimeSignature(4, 4, 0)]
    self.nstrings = len(tuning.strings)
    self.measures = []
    self.midi = midi
    self.fretboard = Fretboard(tuning)
    self.weights = {"b":1, "height":1, "length":1, "n_changed_strings":1} if weights is None else weights
    self.timeline = self.build_timeline()
    self.output_dir = output_dir
    
    self.populate()
    
    self.tab = self.gen_tab()

  def populate(self):
    """Populates tab with Measures."""
    for i, time_signature in enumerate(self.time_signatures):
      measure_length_in_ticks = measure_length_ticks(self.midi, time_signature)
      
      time_sig_start = self.midi.time_to_tick(time_signature.time)
      
      time_sig_end = self.time_signatures[i+1].time if i < len(self.time_signatures)-1 else self.midi.get_end_time()
      time_sig_end = self.midi.time_to_tick(time_sig_end)
      
      measure_ticks = np.arange(time_sig_start, time_sig_end, measure_length_in_ticks) #List of all the measure start ticks (ex : [0, 1024, 2048])
      
      for imeasure, measure_start in enumerate(measure_ticks):
        measure_end = min(measure_start + measure_length_in_ticks, time_sig_end)
        self.measures.append(Measure(self, imeasure, time_signature, measure_start, measure_end))
  
  def build_timeline(self):
    timeline = defaultdict(dict)
    non_drum_instruments = get_non_drum(self.midi.instruments)
    
    #Notes
    for instrument in non_drum_instruments:
      notes = instrument.notes
      notes.sort(key=lambda x: x.start)
      
      assert [note.start for note in notes] == sorted([note.start for note in notes]) #Are notes sorted by time
      
      for note in notes:
        note_tick = self.midi.time_to_tick(note.start)
        
        if "notes" in timeline[note_tick]:
          timeline[note_tick]["notes"].append(note)
        else:
          timeline[note_tick]["notes"] = [note]
    
    #Time signatures
    for time_signature in self.time_signatures:
      time_signature_tick = self.midi.time_to_tick(time_signature.time)
      timeline[time_signature_tick]["time_signature"] = time_signature
      
    return timeline

  def gen_tab(self):
    """Generates the tab data and the fingerings."""
    
    tab = {}
    
    tab["tuning"] = [string.pitch for string in self.tuning.strings]
    
    tab["measures"] = []

    notes_vocabulary = []
    notes_sequence = []
    
    fingerings_vocabulary = []

    emission_matrix = np.array([])
    initial_probabilities = None
    

    for measure in self.measures:
      res_measure = {"events":[]}

      measure_events = measure.timeline

      for event_tick, event_types in measure_events.items():        
        event = {
          "time": self.midi.tick_to_time(int(event_tick)),
          "time_ticks": int(event_tick),
          "measure_timing": (event_tick - measure.measure_start)/measure.duration_ticks
        }
        
        if "time_signature" in event_types:
          ts = event_types["time_signature"]
          event["time_signature_change"] = [ts.numerator, ts.denominator]

        if "notes" in event_types: #if notes contains one or more notes at a specific timing
          event["notes"] = [] #Signals there are notes in this event
          
          notes = event_types["notes"]
          
          notes_pitches = tuple(set([note.pitch for note in notes]))
          notes = [Note(pitch) for pitch in notes_pitches]
          
          notes = self.fretboard.fix_oob_notes(notes, preserve_highest_note=False)
          
          note_options = self.fretboard.get_note_options(notes)
          
          if notes_pitches not in notes_vocabulary:
            fingering_options = self.fretboard.get_possible_fingerings(note_options)
            
            if len(fingering_options) > 0:   
              notes_vocabulary.append(notes_pitches)
              
              fingerings_vocabulary += fingering_options 
                            
              if initial_probabilities is None:
                isolated_difficulties = [compute_isolated_path_difficulty(self.fretboard.G, path, self.tuning) for path in fingering_options]
                initial_probabilities = difficulties_to_probabilities(isolated_difficulties)
              
              emission_matrix = expand_emission_matrix(emission_matrix, fingering_options)
            
          if notes_pitches in notes_vocabulary:
            notes_sequence.append(notes_vocabulary.index(notes_pitches))
          else:
            notes_sequence.append(-1)
            
        res_measure["events"].append(event)

      tab["measures"].append(res_measure)
            
    transition_matrix = build_transition_matrix(self.fretboard.G, fingerings_vocabulary, self.weights, self.tuning)
    
    initial_probabilities = np.hstack((initial_probabilities, np.zeros(len(transition_matrix) - len(initial_probabilities))))
    
    sequence_indices = viterbi(notes_sequence, transition_matrix, emission_matrix, initial_probabilities)

    final_sequence = np.array(fingerings_vocabulary, dtype=object)[sequence_indices]
    
    tab = self.populate_tab_notes(tab, final_sequence)
    
    
    return tab

  def populate_tab_notes(self, tab, sequence):
    """Populates the tab template with notes and their fingerings.

    Args:
        tab (dict): The tab template without notes
        sequence (list): Sequence of notes and fingerings to be used

    Returns:
        dict: The final tab with notes and fingerings
    """
    ievent = 0
    for measure in tab["measures"]:
      for event in measure["events"]:
        if "notes" not in event:
          continue
        
        for path_note in sequence[ievent]:
          string, fret = self.fretboard.G.nodes[path_note]["pos"]   
          event["notes"].append({
            "degree": path_note.degree,
            "octave": path_note.octave,
            "string": string,
            "fret": fret
            })
        ievent += 1
        
    return tab

  def to_string(self):
    """Generates the text for the ascii tabs.

    Returns:
        list: List containing tab text for each guitar string
    """
    res = []
    for string in self.tuning.strings:
      header = string.degree
      header += "||" if len(header)>1 else " ||"
      res.append(header)

    for measure in self.tab["measures"]:
      for ievent, event in enumerate(measure["events"]):
        if "notes" in event:
          for note in event["notes"]:
            string, fret = note["string"], note["fret"]
            res[string] += str(fret)

          next_event_timing = measure["events"][ievent + 1]["measure_timing"] if ievent < len(measure["events"]) - 1 else 1.0
          dashes_to_add = max(1, math.floor((next_event_timing - event["measure_timing"]) * 16))

          res = fill_measure_str(res)

          for istring in range(self.nstrings):
            res[istring] += "-" * dashes_to_add

      for istring in range(self.nstrings):
        res[istring] += "|"

    return res

  def to_json(self):
    """Exports the tab to a json file."""
    if self.tab is None:
      return

    json_object = json.dumps(self.tab, indent=4)

    with open(os.path.join("json", self.name + ".json"), "w") as outfile:
        outfile.write(json_object)

  def to_ascii(self):
    """Exports the tab to a text file."""
    if self.tab is None:
      return

    notes_str = self.to_string()

    output_dir = "./tabs" if self.output_dir is None else self.output_dir
    with open(Path(output_dir, self.name).with_suffix(".txt"),"w") as file:
      for string_notes in notes_str:
        file.write(string_notes + "\n")

  def __repr__(self):
    """Used to print out the tab.

    Returns:
        str: String representation of the tab.
    """
    return self.tab