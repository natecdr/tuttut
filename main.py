import pretty_midi
from tab import Tab
from theory import Tuning
import matplotlib.pyplot as plt
import networkx as nx
from utils import get_notes_in_graph
from theory import Note, Degree

f = pretty_midi.PrettyMIDI("./midis/twinkle.mid", resolution=24)

tab = Tab("twinkle", Tuning(), f)
resolution = f.resolution

tab.populate()
tab.to_file()

G = tab.graph
pos=nx.get_node_attributes(G,'pos')
nx.draw(G, pos)
plt.show()
