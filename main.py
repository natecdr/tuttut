import pretty_midi
from tab import Tab
from theory import Tuning
import matplotlib.pyplot as plt

f = pretty_midi.PrettyMIDI("./midis/fur_elise.mid", resolution=24)
print("Instruments :", f.instruments)
print("Time sigs :", f.time_signature_changes)

tab = Tab("fur_elise", Tuning(), f)

tab.populate()
tab.to_file()