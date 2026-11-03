import pretty_midi
from tuttut.logic.tab import Tab
from tuttut.logic.theory import Tuning
import argparse
import traceback
import numpy as np
from pathlib import Path
np.seterr(divide="ignore")

def init_parser():
	"""Initializes the argument parser for execution.

	Returns:
			argparse.ArgumentParser: The parser object
	"""
	parser = argparse.ArgumentParser(description="MIDI to Guitar Tabs convertor")
	parser.add_argument("source", metavar="source", type=Path, help = "Name of the MIDI file to convert")
	parser.add_argument("output_dir", metavar="destination", type=Path, help = "Output directory")
	return parser

def main():
	parser = init_parser()
	args = parser.parse_args()
	
	source = args.source
	if source.suffix.lower() not in (".mid", ".midi"):
		parser.error(f"{source.name} must end with .mid or .midi")
	if not source.is_file():
		parser.error(f"file not found: {source}")

	try:
		midi = pretty_midi.PrettyMIDI(source.as_posix())
		tab = Tab(source.stem, Tuning(), midi, output_dir = args.output_dir)
		tab.to_ascii()
		print(f"Tab written to {args.output_dir / (source.stem + '.txt')}")
		
	except Exception as e:
		traceback.print_exc()
		print("There was an error. You might want to try another MIDI file. The tool tends to struggle with more complicated multi-channel MIDI files.")
		raise SystemExit(1)

if __name__ == "__main__":
	main()