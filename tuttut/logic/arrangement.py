from logic.midi_utils import *
from logic.theory import Note

class Arrangement():
    def __init__(self, notes, tuning):
        self.notes = notes
        self.tuning = tuning
        
    def fit_notes_to_tuning(self):
        pitch_bounds = [note.pitch for note in self.tuning.get_bounds()]
        
        notes_pitches = [note.pitch for note in self.notes]
        
        for i in range(len(notes_pitches)):
            notes_pitches[i] = self.fit_note_to_tuning(notes_pitches[i], pitch_bounds)
                
        self.notes = [Note(pitch) for pitch in notes_pitches]
        
    def fit_note_to_tuning(self, pitch, pitch_bounds):
        while pitch < pitch_bounds[0]:
            pitch += 12
                
        while pitch > pitch_bounds[1]:
            pitch -= 12
        
        return pitch
    
    
        