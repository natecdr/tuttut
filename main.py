import pretty_midi
from tab import Tab
from theory import Tuning

f = pretty_midi.PrettyMIDI("./midis/twinkle.mid", resolution=24)

tab = Tab("twinkle", Tuning(), f)

tab.populate()
tab.to_file()