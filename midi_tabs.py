import pretty_midi
from app.tab import Tab
from app.theory import Tuning
import argparse

def init_parser():
    parser = argparse.ArgumentParser(description="MIDI to Guitar Tabs convertor")
    parser.add_argument("source", metavar="src", type=str, help = "Name of the MIDI file to convert")
    return parser

if __name__ == "__main__":
  parser = init_parser()
  args = parser.parse_args()
  file = args.source

  try:
    f = pretty_midi.PrettyMIDI("./midis/" + file, resolution=24)
    tab = Tab(file[:-4], Tuning(), f)
    tab.populate()
    tab.to_file()
  except Exception as e:
    print(str(e))
    print("There was an error. You might want to try another MIDI file. The tool tends to struggle with more complicated multi-channel MIDI files.")