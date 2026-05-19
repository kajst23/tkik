from midiutil import MIDIFile

PITCH_MAP = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
    'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
}

class MidiGenerator:
    def __init__(self, events):
        self.events = events
        self.midi = MIDIFile(1)  # One track
        self.track = 0
        self.channel = 0
        self.time = 0.0  # Absolute time in beats
        self.tempo = 120
        self.midi.addTempo(self.track, self.time, self.tempo)

    def _pitch_to_midi_num(self, pitch, octave):
        return (octave + 1) * 12 + PITCH_MAP[pitch]

    def generate(self):
        for event in self.events:
            if event["type"] == "set_param":
                if event["name"] == "TEMPO":
                    self.tempo = event["value"]
                    self.midi.addTempo(self.track, self.time, self.tempo)
                elif event["name"] == "INSTRUMENT":
                    self.midi.addProgramChange(self.track, self.channel, self.time, event["value"] - 1)
            
            elif event["type"] == "note":
                midi_pitch = self._pitch_to_midi_num(event["pitch"], event["octave"])
                duration = event["duration"]
                duration_in_beats = 4.0 / duration
                
                self.midi.addNote(self.track, self.channel, midi_pitch, self.time, duration_in_beats, 100)
                self.time += duration_in_beats

            elif event["type"] == "chord":
                duration = event["duration"]
                duration_in_beats = 4.0 / duration
                
                for p in event["pitches"]:
                    midi_pitch = self._pitch_to_midi_num(p["pitch"], p["octave"])
                    self.midi.addNote(self.track, self.channel, midi_pitch, self.time, duration_in_beats, 100)
                
                self.time += duration_in_beats

            elif event["type"] == "rest":
                duration = event["duration"]
                duration_in_beats = 4.0 / duration
                self.time += duration_in_beats

    def save(self, filepath):
        with open(filepath, "wb") as output_file:
            self.midi.writeFile(output_file)
