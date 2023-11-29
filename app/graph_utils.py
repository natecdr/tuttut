import numpy as np
import math
import networkx as nx
import matplotlib.pyplot as plt
import itertools

from app.theory import *
from app.midi_utils import transpose_note, remove_duplicate_notes, sort_notes_by_pitch

def distance_between(p1, p2):
  """Computes the distance between two points. 
  Distance between 2 strings is assumed to be 1/6.

  Args:
      x (tuple): Source point
      y (tuple): Destination point

  Returns:
      float: Distance between the two points
  """
  p1 = (p1[0]/6, p1[1])
  p2 = (p2[0]/6, p2[1])
  return math.dist(p1,p2)

def get_fret_distance(nfret, scale_length = 650):
  """Returns the distance of the fret from the nut.

  Args:
      nfret (int): Number of the fret
      scale_length (int, optional): Scale length of the guitar (Distance beteen the nut and the bridge). Defaults to 650.

  Returns:
      float: Distance of the fret from the nut
  """
  res = 0
  for i in range(nfret):
    fret_height = scale_length / 17.817
    res += fret_height
    scale_length -= fret_height

  return res

def get_notes_in_graph(G, note):
  """Get all nodes that correspond to a specific note in a graph.

  Args:
      G (networkx.Graph): Fretboard graph
      note (Note): Note to find on the fretboard

  Returns:
      list: List of nodes thar play the specified note
  """
  nodes = list(G.nodes)

  return [node for node in nodes if node == note]

def build_path_graph(G, note_arrays):
  """Returns a path graph corresponding to all possible notes of a chord.

  Args:
      G (networkx.Graph): Fretboard graph
      note_arrays (list): List of possible positions for the notes

  Returns:
      networkx.DiGraph: Path graph for all possible position
  """
  res = nx.DiGraph()

  for x, note_array in enumerate(note_arrays):
    for y, possible_note in enumerate(note_array):
      res.add_node(possible_note, pos = (x, y))

  for idx, note_array in enumerate(note_arrays[:-1]): #Go through every array except the last
    for possible_note in note_array:
      for possible_target_note in note_arrays[idx+1]:
        distance = G[possible_note][possible_target_note]["distance"]
        if is_edge_possible(possible_note, possible_target_note, G):
          res.add_edge(possible_note, possible_target_note, distance = distance)

  return res 

def is_edge_possible(possible_note, possible_target_note, G):
  """Checks if a connection is possible between 2 nodes

  Args:
      possible_note (Note): Source note
      possible_target_note (Note): Target note
      G (networkx.Graph): Fretboard graph

  Returns:
      bool: Possibility of the connection
  """
  is_distance_possible = G[possible_note][possible_target_note]["distance"] < 6
  is_different_string = G.nodes[possible_note]["pos"][0] != G.nodes[possible_target_note]["pos"][0]
  return is_distance_possible and is_different_string

def find_all_paths(G, note_arrays): 
  """Returns all possible paths in a path graph

  Args:
      G (networkx.Graph): Fretboard graph
      note_arrays (list): List of possible positions for the notes

  Returns:
      list: List of paths
  """
  paths = []
  
  if len(note_arrays) == 1:
    return [(note,) for note in note_arrays[0]]

  for note_arrays_permutation in list(itertools.permutations(note_arrays)):
    path_graph = build_path_graph(G, note_arrays_permutation)
    # display_path_graph(path_graph)
    for possible_source_node in note_arrays_permutation[0]:
      permutation_paths = nx.all_simple_paths(path_graph, possible_source_node, target=note_arrays_permutation[-1])
      for path in permutation_paths:
        if not is_path_already_checked(paths, path) and is_path_possible(G, path, note_arrays_permutation):
          paths.append(tuple(path))
            
  return paths

def is_path_already_checked(paths, current_path):
  """Checks if paths is already present in explored paths, whatever the order. 

  Args:
      paths (list): List of paths that have been already explored
      current_path (tuple): Path to check

  Returns:
      bool: If the path has already been checked
  """
  for path in paths:
    if set(path) == set(current_path):
      return True
  
  return False

def is_path_possible(G, path, note_arrays):
  """Checks if path is possible and playable.

  Args:
      G (networkx.Graph): Fretboard graph
      path (tuple): Notes path
      note_arrays (list): List of possible positions for the notes

  Returns:
      bool: If the path is possible and playable
  """
  #No 2 fingers on a single string
  plucked_strings = [G.nodes[note]["pos"][0] for note in path]
  one_per_string = len(plucked_strings) == len(set(plucked_strings))

  #No more than 5 fret span
  used_frets = [G.nodes[note]["pos"][1] for note in path if G.nodes[note]["pos"][1] != 0]
  max_fret_span = (max(used_frets) - min(used_frets)) < 5 if len(used_frets) > 0 else True

  #Path doesn't visit more nodes than necessary
  right_length = len(path) <= len(note_arrays)

  return one_per_string and max_fret_span and right_length

def compute_path_difficulty(G, path, previous_path, weights):
  """Computes the difficulty of a path.

  Args:
      G (networkx.Graph): Fretboard graph
      path (tuple): Path to compute the difficulty for
      previous_path (tuple): Previous played path

  Returns:
      float: Difficulty metric of a path
  """
  height = get_height(G, path, previous_path)
  previous_height = get_height(G, previous_path) if len(previous_path) > 0 else 0

  dheight = np.abs(height-previous_height)

  length = get_path_length(G, path)
  
  n_changed_strings = get_n_changed_strings(G, path, previous_path)
  
  easiness = laplace_distro(dheight, b=weights["b"]) * 1/(1+height * weights["height"]) * 1/(1+length * weights["length"]) * 1/(1+n_changed_strings * weights["n_changed_strings"])
  
  return 1/easiness

def compute_isolated_path_difficulty(G, path):
  """Computes the difficulty of a path not taking into account the previous one played.

  Args:
      G (networkx.Graph): Fretboard graph
      path (tuple): Path to compute the difficulty for
      previous_path (tuple): Previous played path

  Returns:
      float: Difficulty metric of a path
  """
  height = get_height(G, path)
  
  length = get_path_length(G, path)
  
  easiness = 1/(1+height) * 1/(1+length)
  
  return 1/easiness

def laplace_distro(x, b, mu=0.0):
  """Returns the y value for x on a laplace distribution.

  Args:
      x (float): X
      b (float): b parameter for Laplace distribution
      mu (float, optional): mu parameter for Laplace distribution. Defaults to 0.

  Returns:
      _type_: _description_
  """
  return (1/(2*b))*math.exp(-abs(x-mu)/(b))

def get_nfingers(G, path):
  """Returns the number of fingers needed for a path.

  Args:
      G (networkx.Graph): Fretboard graph
      path (tuple): Path to compute the number of fingers for

  Returns:
      int: Number of fingers
  """
  count = 0
  for note in path:
    ifret = G.nodes[note]["pos"][1]
    if ifret != 0:
      count += 1
    
  return count

def get_n_changed_strings(G, path, previous_path):
  """Returns the number of strings that have changed compared to the previous shape.

  Args:
      G (networkx.Graph): Fretboard graph
      path (tuple): Path to compute the number of changed strings for
      previous_path (tuple): Previous played path

  Returns:
      int: Number of changed strings
  """
  used_strings = set([G.nodes[note]["pos"][0] for note in path])
  previous_used_strings = set([G.nodes[note]["pos"][0] for note in previous_path])

  n_changed_strings = len(path) - len(set(used_strings).intersection(previous_used_strings))

  return n_changed_strings

def get_height(G, path, previous_path=None):
  """Returns the average height on the fretboard of gighest and lowest notes in the path.

  Args:
      G (networkx.Graph): Fretboard graph
      path (tuple): Path to compute the height for
      previous_path (tuple, optional): Previous played path. Defaults to None.

  Returns:
      float: Height of the path if possible, height of the previous path instead
  """
  y = [G.nodes[note]["pos"][1] for note in path if G.nodes[note]["pos"][1] != 0]

  if len(y) > 0:
    return (max(y) + min(y))/2
    # return min(y)
  elif previous_path is None:
    return 0
  else:
    return get_height(G, previous_path)

def get_path_length(G, path):
  """Returns the total length of a path.
  
  Corresponds to the sum of all the distances between the notes.

  Args:
      G (networkx.Graph): Fretboard graph
      path (tuple): Path to compute the length for

  Returns:
      float: Length of the path
  """
  res = 0
  for i in range(len(path)-1):
    res += G[path[i]][path[i+1]]["distance"]
  return res
  
def display_path_graph(path_graph, show_distances=True, show_names=True):
  """Displays the path graph on a plt plot.

  Args:
      path_graph (networkx.DiGraph): Path graph
      show_distances (bool, optional): If the distances should be shown on the graph. Defaults to True.
      show_names (bool, optional): If the note names should be shown on the graph. Defaults to True.
  """
  pos=nx.get_node_attributes(path_graph,'pos')
  nx.draw(path_graph, pos, with_labels=show_names)

  if show_distances:
    edge_labels = nx.get_edge_attributes(path_graph,'distance')

    for label in edge_labels:
      edge_labels[label] = round(edge_labels[label], 2)
    nx.draw_networkx_edge_labels(path_graph, pos, edge_labels = edge_labels, label_pos = 0.6)

  plt.show()
  
def viterbi(V, Tm, Em, initial_distribution = None):
  """Implementation of the Viterbi algorithm.

  Args:
      V (list): Sequence of observations.
      Tm (np.ndarray): Transition matrix
      Em (np.ndarray): Emission matrix
      initial_distribution (list, optional): Initial distribution. Defaults to None.

  Returns:
      list: The most likely sequence of hidden states 
  """
  T = len(V)
  M = Tm.shape[0]

  initial_distribution = initial_distribution if initial_distribution is not None else np.full(M, 1/M)

  omega = np.zeros((T, M))
  omega[0, :] = np.log(initial_distribution * Em[:, V[0]])

  prev = np.zeros((T - 1, M))

  for t in range(1, T):
      for j in range(M):
          # Same as Forward Probability
          probability = omega[t - 1] + np.log(Tm[:, j]) + np.log(Em[j, V[t]])

          # This is our most probable state given previous state at time t (1)
          prev[t - 1, j] = np.argmax(probability)

          # This is the probability of the most probable state (2)
          omega[t, j] = np.max(probability)

  # Path Array
  S = np.zeros(T)

  # Find the most probable last hidden state
  last_state = np.argmax(omega[T - 1, :])

  S[0] = last_state

  backtrack_index = 1
  for i in range(T - 2, -1, -1):
      S[backtrack_index] = prev[i, int(last_state)]
      last_state = prev[i, int(last_state)]
      backtrack_index += 1

  # Flip the path array since we were backtracking
  S = np.flip(S, axis=0)

  return S

def build_transition_matrix(G, fingerings, weights):
  """Builds the transition matrix according to all the present fingerings.

  Args:
      G (networkx.Graph): Fretboard graph
      fingerings (list): All the fingerings that can be used to play a piece.

  Returns:
      np.ndarray: Transition matrix
  """
  transition_matrix = np.zeros((len(fingerings), len(fingerings)))
  for iprevious in range(len(fingerings)):
    difficulties = np.array([1/compute_path_difficulty(G, fingerings[icurrent], fingerings[iprevious], weights)
                            for icurrent in range(len(fingerings))])
    
    transition_matrix[iprevious] = difficulties_to_probabilities(difficulties)
  
  return transition_matrix

def difficulties_to_probabilities(difficulties):
  """Transforms a list of difficulties to a list of probabilities.

  Args:
      difficulties (list): List of difficulties

  Returns:
      list: List of probabilities
  """
  difficulties_total = np.sum(difficulties)
  return np.array([difficulty/difficulties_total for difficulty in difficulties])

def expand_emission_matrix(emission_matrix, all_paths):
  """Expands the emission matrix as new notes come by.

  Args:
      emission_matrix (np.ndarray): Current emission matrix
      all_paths (list): All current paths

  Returns:
      np.ndarray: New updated emission matrix
  """
  if len(emission_matrix) > 0:
    filler = np.zeros((len(all_paths), emission_matrix.shape[1]))
    emission_matrix = np.vstack((emission_matrix, filler))
    column = np.vstack((np.vstack(np.zeros(len(emission_matrix)-len(all_paths))), np.vstack(np.ones(len(all_paths)))))
    emission_matrix = np.hstack((emission_matrix, column))
  else:
    emission_matrix = np.vstack((np.ones(len(all_paths))))

  return emission_matrix
  
def display_notes_on_graph(G, path):
  """Displays notes played on a plt graph.

  Args:
      G (networkx.Graph): Fretboard graph
      path (tuple): Path to display
  """
  pos = nx.get_node_attributes(G,'pos')
  plt.figure(figsize=(2,6))
  nx.draw(G, pos)
  nx.draw(G.subgraph(path), pos = pos, node_color="red")
  plt.show()
  
def display_complete_graph(complete_graph):
  positions = nx.get_node_attributes(complete_graph, "pos")
  nx.draw(complete_graph, pos=positions)
  plt.show()

def get_note_arrays(G, notes):
  """Returns note arrays from a list of theory.Notes"""
  note_arrays =[get_notes_in_graph(G, note) for note in notes]
  note_arrays = [note_array for note_array in note_arrays if len(note_array) > 0]
  
  return note_arrays

def fix_impossible_notes(tuning, notes, preserve_highest_note = False):
  min_possible_pitch, max_possible_pitch = tuning.get_pitch_bounds()
  
  highest_pitch_before = max([note.pitch for note in notes])
  
  highest_pitch_semitones_above_max = max(highest_pitch_before - max_possible_pitch, 0)
  highest_pitch_after = highest_pitch_before - (math.ceil(highest_pitch_semitones_above_max/12) * 12)
  #Highest pitch after processing (n octaves below highest before processing)
  
  res_notes = []
  
  for note in notes:
    n_octaves_to_adjust = 0
    
    if not preserve_highest_note:
      if note.pitch > max_possible_pitch:
        semitones_above_max = max(note.pitch - max_possible_pitch, 0)
        n_octaves_to_adjust = - math.ceil(semitones_above_max/12)
    else:
      if note.pitch > highest_pitch_after:
        semitones_above_max = max(note.pitch - highest_pitch_after, 0)
        n_octaves_to_adjust = - math.ceil(semitones_above_max/12)
    
    if note.pitch < min_possible_pitch:
      semitones_below_min = max(min_possible_pitch - note.pitch, 0)
      n_octaves_to_adjust = math.ceil(semitones_below_min/12)
      
    new_note = transpose_note(note, n_octaves_to_adjust * 12)
    
    if new_note.pitch >= min_possible_pitch and new_note.pitch <= max_possible_pitch:
      res_notes.append(new_note)
  
  return remove_duplicate_notes(res_notes)  
  