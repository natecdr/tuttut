from logic.midi_utils import *
import numpy as np
import math

def get_tab_positions(tab_json):
  positions = []
  for measure in tab_json["measures"]:
      for event in measure["events"]:
        if "notes" in event and len(event["notes"]) > 0:
          event_positions = tuple((note["string"], note["fret"]) for note in event["notes"] if "notes" in event)
          positions.append(event_positions)
  
  return positions

def get_tab_difficulty(tab, weights):
  total_difficulty = 0
  positions = get_tab_positions(tab)
  for i in range(len(positions)):
    total_difficulty += get_position_difficulty(positions[i], positions[i-1] if i > 0 else None, weights)
  return total_difficulty

def get_position_difficulty(position, previous_position, weights):
  position = tuple(pos for pos in position if len(pos) != 0)
  previous_position = tuple(pos for pos in previous_position if len(pos) != 0) if previous_position is not None else None
  
  height = get_height(position, previous_position)

  previous_height = get_height(previous_position) if previous_position is not None else 0
  
  dheight = np.abs(height-previous_height)

  span = get_span(position)

  n_changed_strings = get_n_changed_strings(position, previous_position)
  
  easiness = laplace_distro(dheight, b=weights["b"]) * 1/(1+height * weights["height"]) * 1/(1+span * weights["length"]) * 1/(1+n_changed_strings * weights["n_changed_strings"])
  
  return 1/easiness

def get_height(position, previous_position=None):
  y = [pos[1] for pos in position if pos[1] != 0]

  if len(y) > 0:
    return (max(y) + min(y))/2
  elif previous_position is None:
    return 0
  else:
    return get_height(previous_position)

def get_span(position):
  y = [pos[1] for pos in position]
  
  return max(y) - min(y)

def get_nfingers(position):
  count = 0
  for pos in position:
    ifret = pos[1]
    if ifret != 0:
      count += 1
    
  return count

def get_n_changed_strings(position, previous_position):
  used_strings = set([pos[0] for pos in position])
  previous_used_strings = set([pos[0] for pos in previous_position]) if previous_position is not None else set()

  n_changed_strings = len(position) - len(set(used_strings).intersection(previous_used_strings))

  return n_changed_strings

def laplace_distro(x, b, mu=0.0):
  return (1/(2*b))*math.exp(-abs(x-mu)/(b))