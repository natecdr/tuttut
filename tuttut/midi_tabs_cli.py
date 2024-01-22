import pretty_midi
from tuttut.logic.tab import Tab
from tuttut.logic.theory import Tuning
import argparse
import traceback
from time import time
import numpy as np
from pathlib import Path
np.seterr(divide="ignore")

def init_parser():
  """Initializes the argument parser for execution.

  Returns:
      argparse.ArgumentParser: The parser object
  """
  parser = argparse.ArgumentParser(description="MIDI to Guitar Tabs convertor")
  parser.add_argument("source", metavar="src", type=Path, help = "Name of the MIDI file to convert")
  return parser

if __name__ == "__main__":
  parser = init_parser()
  args = parser.parse_args()

  file = args.source.with_suffix(".mid")
  weights = {'b': 1, 'height': 1, 'length': 1, 'n_changed_strings': 1}

  try:
    start = time()
    f = pretty_midi.PrettyMIDI(Path("./midis", file).as_posix())
    tab = Tab(file.stem, Tuning(), f, weights=weights)
    # tab = Tab(file.stem, Tuning([Note(69), Note(64), Note(60), Note(67)]), f, weights=weights)
    tab.to_ascii()
    tab.to_json()
    print("Time :", time() - start)

  except Exception as e:
    print(traceback.print_exc())
    print("There was an error. You might want to try another MIDI file. The tool tends to struggle with more complicated multi-channel MIDI files.")