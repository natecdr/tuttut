// String constants
STATE_READY = 'STATE_READY';
STATE_WORKING = 'STATE_WORKING';
STATE_COMPLETE = 'STATE_COMPLETE';
STATE_NOT_READY = 'STATE_NOT_READY';

const presets = {
    guitar : {
        degrees : ["E", "B", "G", "D", "A", "E"],
        octaves : [4, 3, 3, 3, 2, 2]
    },
    ukulele : {
        degrees : ["A", "E", "C", "G"],
        octaves : [4, 4, 4, 4] 
    },
    bass : {
        degrees : ["G", "D", "A", "E"],
        octaves : [2, 2, 1, 1]
    }
}