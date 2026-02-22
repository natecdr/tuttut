import math
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from tuttut.logic.difficulty import compute_path_difficulty, precompute_fingering_stats, get_dheight_score, laplace_distro

MAX_EDGE_DISTANCE = 6    # Maximum fretboard distance between two notes to form a valid edge


def _distance_between(p1, p2, nstrings):
    """Computes the fretboard distance between two (string, fret) positions.

    Open string targets (fret=0) always return 0, matching the original graph convention
    where open-string nodes were always considered reachable.

    Args:
        p1 (tuple): Source (string_index, fret_index)
        p2 (tuple): Target (string_index, fret_index)
        nstrings (int): Total number of strings, used to normalise string spacing

    Returns:
        float: Fretboard distance
    """
    if p2[1] == 0:
        return 0
    return math.dist((p1[0] / nstrings, p1[1]), (p2[0] / nstrings, p2[1]))


def build_path_graph(positions, note_arrays, nstrings):
    """Returns a path graph corresponding to all possible positions for the notes of a chord.

    Args:
        positions (dict): Mapping from fretboard node to (string, fret) position tuple
        note_arrays (list): List of possible positions for each note
        nstrings (int): Total number of strings on the instrument

    Returns:
        networkx.DiGraph: Path graph for all possible positions
    """
    res = nx.DiGraph()

    for x, note_array in enumerate(note_arrays):
        for y, possible_note in enumerate(note_array):
            res.add_node(possible_note, pos=(x, y))

    for idx, note_array in enumerate(note_arrays[:-1]):
        for possible_note in note_array:
            for possible_target_note in note_arrays[idx + 1]:
                distance = _distance_between(positions[possible_note], positions[possible_target_note], nstrings)
                if is_edge_possible(possible_note, possible_target_note, positions, distance):
                    res.add_edge(possible_note, possible_target_note, distance=distance)

    return res


def is_edge_possible(note, target, positions, distance):
    """Checks if a connection is possible between two fretboard nodes.

    Args:
        note (Note): Source note
        target (Note): Target note
        positions (dict): Mapping from fretboard node to (string, fret) position tuple
        distance (float): Pre-computed fretboard distance between the two nodes

    Returns:
        bool: Whether the connection is valid
    """
    return distance < MAX_EDGE_DISTANCE and positions[note][0] != positions[target][0]


def is_path_already_checked(paths, current_path):
    """Checks if a path is already present in the explored set, regardless of order.

    Args:
        paths (list): Already-explored paths
        current_path (tuple): Path to check

    Returns:
        bool: True if the path has already been explored
    """
    current_set = set(current_path)
    return any(set(path) == current_set for path in paths)


def display_path_graph(path_graph, show_distances=True, show_names=True):
    """Displays the path graph on a matplotlib plot.

    Args:
        path_graph (networkx.DiGraph): Path graph
        show_distances (bool): Whether to show edge distances. Defaults to True.
        show_names (bool): Whether to show note names. Defaults to True.
    """
    pos = nx.get_node_attributes(path_graph, "pos")
    nx.draw(path_graph, pos, with_labels=show_names)

    if show_distances:
        edge_labels = nx.get_edge_attributes(path_graph, "distance")
        for label in edge_labels:
            edge_labels[label] = round(edge_labels[label], 2)
        nx.draw_networkx_edge_labels(path_graph, pos, edge_labels=edge_labels, label_pos=0.6)

    plt.show()


def viterbi(V, Tm, Em, initial_distribution=None):
    """Implementation of the Viterbi algorithm.

    Args:
        V (list): Sequence of observations.
        Tm (np.ndarray): Transition matrix
        Em (np.ndarray): Emission matrix
        initial_distribution (list, optional): Initial distribution. Defaults to uniform.

    Returns:
        np.ndarray: Most likely sequence of hidden state indices
    """
    T = len(V)
    M = Tm.shape[0]

    initial_distribution = initial_distribution if initial_distribution is not None else np.full(M, 1 / M)

    log_Tm = np.log(Tm)
    log_Em = np.log(Em)

    omega = np.zeros((T, M))
    omega[0, :] = np.log(initial_distribution) + log_Em[:, V[0]]

    prev = np.zeros((T - 1, M))

    for t in range(1, T):
        # scores[i, j] = omega[t-1][i] + log_Tm[i, j] + log_Em[j, V[t]]
        scores = omega[t - 1, :, np.newaxis] + log_Tm + log_Em[:, V[t]]
        prev[t - 1] = np.argmax(scores, axis=0)
        omega[t] = np.max(scores, axis=0)

    S = np.zeros(T)
    last_state = np.argmax(omega[T - 1, :])
    S[0] = last_state

    backtrack_index = 1
    for i in range(T - 2, -1, -1):
        S[backtrack_index] = prev[i, int(last_state)]
        last_state = prev[i, int(last_state)]
        backtrack_index += 1

    return np.flip(S, axis=0).astype(int)


def _compute_pair_easiness(curr_stats, prev_stats, weights, tuning):
    """Computes the easiness of transitioning from a previous fingering to a current one.

    Args:
        curr_stats (dict): Precomputed stats for the current fingering
        prev_stats (dict): Precomputed stats for the previous fingering
        weights (dict): Difficulty component weights
        tuning (Tuning): Instrument tuning

    Returns:
        float: Easiness value (higher = easier transition)
    """
    curr_rh = curr_stats["raw_height"] if curr_stats["raw_height"] != 0 else prev_stats["raw_height"]
    dheight = get_dheight_score(curr_rh, prev_stats["raw_height"], tuning)
    n_changed = (curr_stats["n_notes"] - len(curr_stats["all_strings"] & prev_stats["non_open_strings"])) / tuning.nstrings

    return (
        laplace_distro(dheight, b=weights["b"])
        * 1 / (1 + curr_stats["height_score"] * weights["height"])
        * 1 / (1 + curr_stats["span_score"] * weights["length"])
        * 1 / (1 + n_changed * weights["n_changed_strings"])
    )


def build_transition_matrix(positions, fingerings, weights, tuning):
    """Builds the transition matrix over all fingerings.

    Args:
        positions (dict): Mapping from fretboard node to (string, fret) position tuple
        fingerings (list): All fingerings that can appear in the piece
        weights (dict): Difficulty component weights
        tuning (Tuning): Instrument tuning

    Returns:
        np.ndarray: Transition matrix of shape (n_fingerings, n_fingerings)
    """
    n = len(fingerings)
    stats = precompute_fingering_stats(positions, fingerings, tuning)
    transition_matrix = np.zeros((n, n))
    for iprevious in range(n):
        easiness = np.array([
            _compute_pair_easiness(stats[icurrent], stats[iprevious], weights, tuning)
            for icurrent in range(n)
        ])
        transition_matrix[iprevious] = difficulties_to_probabilities(easiness)
    return transition_matrix


def difficulties_to_probabilities(difficulties):
    """Normalises a difficulty array into a probability distribution.

    Args:
        difficulties (np.ndarray): Array of difficulty values

    Returns:
        np.ndarray: Normalised probability array
    """
    total = np.sum(difficulties)
    return difficulties / total


def expand_emission_matrix(emission_matrix, all_paths):
    """Expands the emission matrix as new note chords are encountered.

    Args:
        emission_matrix (np.ndarray): Current emission matrix
        all_paths (list): All current fingering paths

    Returns:
        np.ndarray: Updated emission matrix
    """
    if len(emission_matrix) > 0:
        filler = np.zeros((len(all_paths), emission_matrix.shape[1]))
        emission_matrix = np.vstack((emission_matrix, filler))
        column = np.vstack((
            np.vstack(np.zeros(len(emission_matrix) - len(all_paths))),
            np.vstack(np.ones(len(all_paths)))
        ))
        emission_matrix = np.hstack((emission_matrix, column))
    else:
        emission_matrix = np.vstack((np.ones(len(all_paths))))
    return emission_matrix
