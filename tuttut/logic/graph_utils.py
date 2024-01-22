import numpy as np
import math
import networkx as nx
import matplotlib.pyplot as plt
import itertools

from tuttut.logic.theory import *

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

def is_edge_possible(possible_note, possible_target_note, G): ####### Should be in Fretboard but is used by build_path_graph
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

def compute_path_difficulty(G, path, previous_path, weights, tuning):
  """Computes the difficulty of a path.

  Args:
      G (networkx.Graph): Fretboard graph
      path (tuple): Path to compute the difficulty for
      previous_path (tuple): Previous played path

  Returns:
      float: Difficulty metric of a path
  """
  raw_height = get_raw_height(G, path, previous_path)
  previous_raw_height = get_raw_height(G, previous_path) if len(previous_path) > 0 else 0
  
  height = get_height_score(G, path, tuning, previous_path)

  dheight = get_dheight_score(raw_height, previous_raw_height, tuning)

  # length = get_path_length(G, path)
  span = get_path_span(G, path)
  
  n_changed_strings = get_n_changed_strings(G, path, previous_path, tuning)
  
  easiness = laplace_distro(dheight, b=weights["b"]) * 1/(1+height * weights["height"]) * 1/(1+span * weights["length"]) * 1/(1+n_changed_strings * weights["n_changed_strings"])
  
  return 1/easiness

def compute_isolated_path_difficulty(G, path, tuning):
  """Computes the difficulty of a path not taking into account the previous one played.

  Args:
      G (networkx.Graph): Fretboard graph
      path (tuple): Path to compute the difficulty for
      previous_path (tuple): Previous played path

  Returns:
      float: Difficulty metric of a path
  """
  height = get_height_score(G, path, tuning)
  
  span = get_path_span(G, path)
  
  easiness = 1/(1+height) * 1/(1+span)
  
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

def get_n_changed_strings(G, path, previous_path, tuning):
  """Returns the number of strings that have changed compared to the previous shape.

  Args:
      G (networkx.Graph): Fretboard graph
      path (tuple): Path to compute the number of changed strings for
      previous_path (tuple): Previous played path

  Returns:
      int: Number of changed strings
  """
  # used_strings = set([G.nodes[note]["pos"][0] for note in path])
  # previous_used_strings = set([G.nodes[note]["pos"][0] for note in previous_path])
  
  used_strings = set([G.nodes[note]["pos"][0] for note in path])
  previous_used_strings = set([G.nodes[note]["pos"][0] for note in previous_path if G.nodes[note]["pos"][1] != 0]) #Does not take into account open strings
  
  n_changed_strings = len(path) - len(set(used_strings).intersection(previous_used_strings))
  

  n_changed_strings_score = n_changed_strings/tuning.nstrings
  assert 0 <= n_changed_strings_score <= 1
  return n_changed_strings_score

def get_height_score(G, path, tuning, previous_path=None):
  """Returns the height score for calculating difficulty (0-1)

    Args:
        G (networkx.Graph): Fretboard graph
        path (tuple): Path to compute the height for
        previous_path (tuple, optional): Previous played path. Defaults to None.

    Returns:
        float: Height of the path if possible, height of the previous path instead
  """
  height = get_raw_height(G, path, previous_path)/tuning.nfrets
  assert 0 <= height <= 1
  return get_raw_height(G, path, previous_path)/tuning.nfrets
    
def get_raw_height(G, path, previous_path=None):
  """Returns the average height on the fretboard of highest and lowest notes in the path.

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
    return get_raw_height(G, previous_path)
  
def get_dheight_score(height, previous_height, tuning):
  """Returns the score for the distance between previous fingering height and current fingering height

  Args:
      height (int): current fingering height
      previous_height (int): previous fingering height
  """
  dheight = np.abs(height-previous_height)/tuning.nfrets
  assert 0 <= dheight <= 1
  return dheight
    
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
    
  length = res/10 #10 probably the maximum distance between notes
  assert 0 <= length <= 1
  return length

def get_path_span(G, path):
  """Returns the vertical span of a path.

  Args:
      G (networkx.Graph): Fretboard graph
      path (tuple): Path to compute the span for

  Returns:
      float: Span of the path
  """
  
  y = [G.nodes[note]["pos"][1] for note in path if G.nodes[note]["pos"][1] != 0]
  
  span = (max(y) - min(y))/5 if len(y) > 0 else 0
  assert 0 <= span <= 1
  return span
  
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

  return S.astype(int)

def build_transition_matrix(G, fingerings, weights, tuning):
  """Builds the transition matrix according to all the present fingerings.

  Args:
      G (networkx.Graph): Fretboard graph
      fingerings (list): All the fingerings that can be used to play a piece.

  Returns:
      np.ndarray: Transition matrix
  """
  transition_matrix = np.zeros((len(fingerings), len(fingerings)))
  for iprevious in range(len(fingerings)):
    difficulties = np.array([1/compute_path_difficulty(G, fingerings[icurrent], fingerings[iprevious], weights, tuning)
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
  
