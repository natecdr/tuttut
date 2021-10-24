import pretty_midi
from tab import Tab
from theory import Tuning
import matplotlib.pyplot as plt
import networkx as nx

f = pretty_midi.PrettyMIDI("./midis/twinkle.mid", resolution=24)

tab = Tab("twinkle", Tuning(), f)
resolution = f.resolution

tab.populate()
tab.to_file()

G = tab.graph
nx.draw(G, with_labels=True, font_weight='bold')
plt.show()