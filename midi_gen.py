from midiutil import MIDIFile
from runtime_types import Note, Chord, Rest, Sequence

PITCH_MAP = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
    'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
}


class MidiGenerator:
    def __init__(self, events):
        self.events = events
        self.midi = MIDIFile(1)  
        self.track = 0
        self.channel = 0
        self.time = 0.0 
        self.tempo = 120
        self.midi.addTempo(self.track, self.time, self.tempo)

    def _pitch_to_midi_num(self, pitch, octave):
        return (octave + 1) * 12 + PITCH_MAP[pitch]

    # def generate(self):
    #     self.time = 0.0 
    #     PPQN = 12.0 

    #     for event in self.events:
    #         if event["type"] == "set_param":
    #             if event["name"] == "TEMPO":
    #                 self.tempo = event["value"]
    #                 self.midi.addTempo(self.track, self.time, self.tempo)
    #             elif event["name"] == "INSTRUMENT":
    #                 self.midi.addProgramChange(self.track, self.channel, self.time, event["value"] - 1)
            
    #         elif event["type"] == "note":
    #             midi_pitch = self._pitch_to_midi_num(event["pitch"], event["octave"])
    #             duration_in_beats = event["duration"] / PPQN
                
    #             self.midi.addNote(self.track, self.channel, midi_pitch, self.time, duration_in_beats, 100)
    #             self.time += duration_in_beats

    #         elif event["type"] == "chord":
    #             duration_in_beats = event["duration"] / PPQN
                
    #             for p in event["pitches"]:
    #                 midi_pitch = self._pitch_to_midi_num(p["pitch"], p["octave"])
    #                 self.midi.addNote(self.track, self.channel, midi_pitch, self.time, duration_in_beats, 100)
                
    #             self.time += duration_in_beats

    #         elif event["type"] == "rest":
    #             duration_in_beats = event["duration"] / PPQN
    #             self.time += duration_in_beats

    def generate(self):
        self.time = 0.0 
        PPQN = 12.0 

        def process_node(node):
            # 1. Obsługa słowników z AST (np. track, play, set_param)
            if isinstance(node, dict):
                if node["type"] == "set_param":
                    if node["name"] == "TEMPO":
                        self.tempo = node["value"]
                        self.midi.addTempo(self.track, self.time, self.tempo)
                    elif node["name"] == "INSTRUMENT":
                        self.midi.addProgramChange(self.track, self.channel, self.time, node["value"] - 1)
                
                elif node["type"] == "track":
                    # Kiedy znajdziemy track, wchodzimy do jego ciała
                    for item in node["body"]:
                        process_node(item)
                        
                elif node["type"] == "play":
                    # Instrukcja play - odtwarzamy zadaną ilość razy
                    times = node.get("times", 1)
                    for _ in range(times):
                        process_node(node["value"])

            # 2. Obsługa obiektów muzycznych
            elif isinstance(node, Note):
                midi_pitch = self._pitch_to_midi_num(node.pitch, node.octave)
                duration_in_beats = node.duration / PPQN
                
                self.midi.addNote(self.track, self.channel, midi_pitch, self.time, duration_in_beats, 100)
                self.time += duration_in_beats

            elif isinstance(node, Chord):
                duration_in_beats = node.duration / PPQN
                # Chord ma wewnątrz listę obiektów Note
                for n in node.notes:
                    midi_pitch = self._pitch_to_midi_num(n.pitch, n.octave)
                    self.midi.addNote(self.track, self.channel, midi_pitch, self.time, duration_in_beats, 100)
                
                self.time += duration_in_beats

            elif isinstance(node, Rest):
                duration_in_beats = node.duration / PPQN
                self.time += duration_in_beats

            elif isinstance(node, Sequence):
                for el in node.elements:
                    process_node(el)

        # Uruchomienie rekursji dla każdego elementu na głównej liście
        for event in self.events:
            process_node(event)

    def save(self, filepath):
        with open(filepath, "wb") as output_file:
            self.midi.writeFile(output_file)