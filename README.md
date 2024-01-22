<p align="center">
	<img src="https://i.ibb.co/FYPcVrK/tuttut.png" alt="Tuttut" height="200" border="0"/>
</p>
Converts MIDI files to guitar tabs.<br />
It can handle any tuning for any number of strings, and will do the arrangement accordingly.

## Using the tool

<p align="center">
	<img src="https://i.ibb.co/L8JKc35/Screenshot-from-2024-01-22-16-09-27.png" alt="Tuttut" height="200" border="0"/>
</p>

First, clone the repo.

Then, place your midi files in the *midis* folder.

Select the MIDI file you wish to convert.
Select the folder in which the tab will be exported.

Done!

## Expected results

This is the kind of result you are expecting to get :

```text
E ||----------3----3----|5----5----3--------|1----1----0----0----|-------------------|3----3----1----1----|0----0-------------|3----3----1----1----|0----0-------------|----------3----3----|5----5----3--------|1----1----0----0----|-------------------|
B ||1----1----1---------|-------------------|--------------------|3----3-------------|--------------------|----------3--------|1-------------------|----------3--------|1----1----1---------|-------------------|--------------------|3----3-------------|
G ||--------------------|5---------5--------|2---------0---------|0---------5--------|5---------2---------|0---------0--------|----------2---------|0---------0--------|--------------------|5---------5--------|2---------0---------|0---------5--------|
D ||2-------------------|-------------------|--------------------|----------2--------|--------------------|-------------------|--------------------|-------------------|2-------------------|-------------------|--------------------|----------2--------|
A ||3---------3---------|----------3--------|----------3---------|----------3--------|3-------------------|-------------------|3-------------------|-------------------|3---------3---------|----------3--------|----------3---------|----------3--------|
E ||--------------------|1------------------|1-------------------|3------------------|----------1---------|3---------3--------|----------1---------|3---------3--------|--------------------|1------------------|1-------------------|3------------------|

```
 This is the generated tab for a twinkle twinkle little star midi.
 
## Limitations
The algorithm tries to approximate as well as possible the way a human would arrange and play pieces. However, it may sometimes not be perfect and the final tab may need some tweaking.

The tool can't handle complicated multi-channel MIDI files, but it's not what it's made for.

Slides, Hammer-on, Pull-offs and other advanced techniques are not modeled.

# Behind the tool

## Glossary

Fingering : Finger positions used by a guitar player to play a note or multiple notes.

Chord : Multiple notes played simultaneously.

## Why the problem is interesting 

The problem of generating guitar tablatures is not trivial because a single note can be played at multiple distinct positions on a guitar. Pressing a different fret on a different string can generate a sound that has the same frequency. A tablature essentially dictates the player the best finger positions to use to play a sequence of notes.
The problem would be easy if a note could only be played on one position, it would be enough just to indicate the notes one by one and there would be no ambiguity on the way to play them, but it's not that simple.

For example, you must take into account the notes played before to choose the finger positions that will minimize the difficulty of transitioning between two fingerings for the player. Typically, the positions must be as close to each other as possible.
Another example : if you want to play a chord - multiple notes simultaneously - there are dozens of combinations of possible fingerings to play that chord. You want to find the optimal fingerings to play these chords.
This problem is referred to as the fingering problem.

*All the possible fingerings to play a C :*
![All the possible fingerings to play a C](https://i.imgur.com/6WWheRR.png)

## How it works

The sequence of notes and fingerings is modeled as a Hidden Markov Model (HMM), with the fingerings being the hidden states and the notes being the observed states.

Our goal is to predict the most likely sequence of hidden states using the sequence of observed states.\
To find that sequence, we can make use of the Viterbi algorithm. This algorithm outputs the most likely sequence of hidden states using the sequence of observed states, the transition probabilities and the emission probabilities of the model.

Transition probabilities are the probabilities to go from one hidden state to some other hidden state. In our case, it's the probability to transition from a fingering to some other one.\
Emission probabilities are the probabilities to get an observed state given a hidden state. In our case, it can be seen as the probability that a certain set of notes will be heard given a certain fingering. 

These probabilities are stored in a transition matrix and an emission matrix.
To build these matrices, we first explore the MIDI file chronologically. For each note or chord that we encounter in the file, we will compute all the fingerings that will produce these notes.

The guitar fretboard is modeled as a complete graph, in the graph theory sense. The nodes correspond to the frets of for each string and the edges represent the distance between the nodes. Being a complete graph, all the nodes are connected by an edge to each other.
This graph is what enables us to find all the ways that a set of notes can be played, using a simple depth-first search algorithm.

In order to compute the transition probabilities between the fingerings, we use a difficulty metric that is defined as :
![DIfficulty metric](https://i.imgur.com/dpe6lDJ.png)

This metric is obviously not perfect. There are numerous other parameters to take into account, but it includes the most intuitive features.

For each of the possible fingerings for a set of notes, we compute all the difficulties transitioning from one fingering to all the others, and we transform these difficulties into probabilities i.e the transitions with the highest difficulties will have the lowest probabilites.\
That is how we populate the transition matrix. It's a 2D matrix containing all the probabilities to transition from one fingering to another.

*Example of how a transition matrix might look like, values are inaccurate and the matrix may be way bigger :*
<img src="https://i.imgur.com/0slagAT.png" height="400" />

While exploring the notes, we also populate the emission matrix with 0's and 1's which correspond to the probabilites that a fingering produce a set of notes. It just does or doesn't.

*Example of how an emission matrix might look like, the matrix may be way bigger :*\
<img src="https://i.imgur.com/Iq84EGD.png" height="400" />

We then use those created matrices and feed them into the viterbi algorithm along with the observed sequence of notes to get the most likely sequence of fingerings to play those notes.
