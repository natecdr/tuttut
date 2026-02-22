import math
import numpy as np

MAX_FRET_DISTANCE = 10   # Approximate upper bound for normalized path length
SPAN_NORMALIZATION = 5   # Maximum expected fret span, used to normalize span score to [0, 1]


def compute_path_difficulty(positions, path, previous_path, weights, tuning):
    """Computes the difficulty of a path.

    Args:
        positions (dict): Mapping from fretboard node to (string, fret) position tuple
        path (tuple): Path to compute the difficulty for
        previous_path (tuple): Previous played path
        weights (dict): Difficulty component weights
        tuning (Tuning): Instrument tuning

    Returns:
        float: Difficulty metric of a path
    """
    raw_height = get_raw_height(positions, path, previous_path)
    previous_raw_height = get_raw_height(positions, previous_path) if len(previous_path) > 0 else 0

    height = get_height_score(raw_height, tuning)
    dheight = get_dheight_score(raw_height, previous_raw_height, tuning)
    span = get_path_span(positions, path)
    n_changed_strings = get_n_changed_strings(positions, path, previous_path, tuning)

    easiness = (
        laplace_distro(dheight, b=weights["b"])
        * 1 / (1 + height * weights["height"])
        * 1 / (1 + span * weights["length"])
        * 1 / (1 + n_changed_strings * weights["n_changed_strings"])
    )

    return 1 / easiness


def compute_isolated_path_difficulty(positions, path, tuning):
    """Computes the difficulty of a path without considering the previous one.

    Args:
        positions (dict): Mapping from fretboard node to (string, fret) position tuple
        path (tuple): Path to compute the difficulty for
        tuning (Tuning): Instrument tuning

    Returns:
        float: Difficulty metric of a path
    """
    raw_height = get_raw_height(positions, path)

    height = get_height_score(raw_height, tuning)
    span = get_path_span(positions, path)
    easiness = 1 / (1 + height) * 1 / (1 + span)
    return 1 / easiness


def laplace_distro(x, b, mu=0.0):
    """Returns the y value for x on a Laplace distribution.

    Args:
        x (float): X
        b (float): Scale parameter
        mu (float, optional): Location parameter. Defaults to 0.

    Returns:
        float: Laplace distribution value at x
    """
    return (1 / (2 * b)) * math.exp(-abs(x - mu) / b)


def get_nfingers(positions, path):
    """Returns the number of fingers needed for a path.

    Args:
        positions (dict): Mapping from fretboard node to (string, fret) position tuple
        path (tuple): Path to compute the number of fingers for

    Returns:
        int: Number of fingers
    """
    return sum(1 for note in path if positions[note][1] != 0)


def get_n_changed_strings(positions, path, previous_path, tuning):
    """Returns the normalised count of strings that changed vs the previous shape.

    Args:
        positions (dict): Mapping from fretboard node to (string, fret) position tuple
        path (tuple): Current path
        previous_path (tuple): Previous played path
        tuning (Tuning): Instrument tuning

    Returns:
        float: Normalised changed-string score in [0, 1]
    """
    used_strings = set(positions[note][0] for note in path)
    previous_used_strings = set(
        positions[note][0] for note in previous_path
        if positions[note][1] != 0  # exclude open strings
    )
    n_changed_strings = len(path) - len(used_strings.intersection(previous_used_strings))
    score = n_changed_strings / tuning.nstrings
    assert 0 <= score <= 1
    return score


def get_height_score(raw_height, tuning):
    """Returns the normalised height score for a path (0–1).

    Args:
        G (networkx.Graph): Fretboard graph
        path (tuple): Current path
        tuning (Tuning): Instrument tuning
        previous_path (tuple, optional): Previous played path.

    Returns:
        float: Normalised height score
    """
    height = raw_height / tuning.nfrets
    assert 0 <= height <= 1
    return height


def get_raw_height(positions, path, previous_path=None):
    """Returns the average of the highest and lowest fret positions in a path.

    Falls back to the previous path when all notes are open strings.

    Args:
        positions (dict): Mapping from fretboard node to (string, fret) position tuple
        path (tuple): Current path
        previous_path (tuple, optional): Previous played path.

    Returns:
        float: Raw height value
    """
    y = [positions[note][1] for note in path if positions[note][1] != 0]
    if len(y) > 0:
        return (max(y) + min(y)) / 2
    elif previous_path is None:
        return 0
    else:
        return get_raw_height(positions, previous_path)


def get_dheight_score(height, previous_height, tuning):
    """Returns the normalised position shift between two consecutive fingering heights.

    Args:
        height (float): Current fingering raw height
        previous_height (float): Previous fingering raw height
        tuning (Tuning): Instrument tuning

    Returns:
        float: Normalised delta-height score in [0, 1]
    """
    dheight = np.abs(height - previous_height) / tuning.nfrets
    assert 0 <= dheight <= 1
    return dheight


def get_path_length(G, path):
    """Returns the normalised total edge-distance of a path.

    Args:
        G (networkx.Graph): Fretboard graph
        path (tuple): Path to compute the length for

    Returns:
        float: Normalised length in [0, 1]
    """
    res = sum(G[path[i]][path[i + 1]]["distance"] for i in range(len(path) - 1))
    length = res / MAX_FRET_DISTANCE
    assert 0 <= length <= 1
    return length


def precompute_fingering_stats(positions, fingerings, tuning):
    """Precomputes per-fingering stats to avoid redundant computation in the transition matrix.

    Args:
        positions (dict): Mapping from fretboard node to (string, fret) position tuple
        fingerings (list): All fingerings to precompute stats for
        tuning (Tuning): Instrument tuning

    Returns:
        list[dict]: One dict per fingering with keys: raw_height, height_score, span_score,
                    all_strings, non_open_strings, n_notes
    """
    stats = []
    for f in fingerings:
        rh = get_raw_height(positions, f)
        stats.append({
            "raw_height": rh,
            "height_score": get_height_score(rh, tuning),
            "span_score": get_path_span(positions, f),
            "all_strings": frozenset(positions[note][0] for note in f),
            "non_open_strings": frozenset(positions[note][0] for note in f if positions[note][1] != 0),
            "n_notes": len(f),
        })
    return stats


def get_path_span(positions, path):
    """Returns the normalised vertical fret span of a path.

    Args:
        positions (dict): Mapping from fretboard node to (string, fret) position tuple
        path (tuple): Path to compute the span for

    Returns:
        float: Normalised span in [0, 1]
    """
    y = [positions[note][1] for note in path if positions[note][1] != 0]
    span = (max(y) - min(y)) / SPAN_NORMALIZATION if len(y) > 0 else 0
    assert 0 <= span <= 1
    return span
