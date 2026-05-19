import re

PITCH_MAP = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}

class MelodyType:
    pass

class Integer(MelodyType):
    def __init__(self, value: int):
        self.value = value
    def __repr__(self):
        return f"Integer({self.value})"

class Note(MelodyType):
    def __init__(self, pitch: str, octave: int, duration: int = 4):
        self.pitch = pitch
        self.octave = octave
        self.duration = duration

    def to_midi(self) -> int:
        return (self.octave + 1) * 12 + PITCH_MAP[self.pitch]

    def transpose(self, half_steps: int):
        current_midi = self.to_midi()
        new_midi = current_midi + half_steps
        self.octave = (new_midi // 12) - 1
        note_index = new_midi % 12
        self.pitch = [k for k, v in PITCH_MAP.items() if v == note_index][0]

    def __repr__(self):
        return f"Note({self.pitch}{self.octave}:{self.duration})"

class Chord(MelodyType):
    def __init__(self, pitches: list[dict], duration: int = 4):
        self.notes = [Note(p["pitch"], p["octave"], duration) for p in pitches]
        self.duration = duration

    def transpose(self, half_steps: int):
        for note in self.notes:
            note.transpose(half_steps)

    def __repr__(self):
        return f"Chord({self.notes}, duration={self.duration})"

class Rest(MelodyType):
    def __init__(self, duration: int = 4):
        self.duration = duration
    def __repr__(self):
        return f"Rest(:{self.duration})"

class Sequence(MelodyType):
    def __init__(self, elements: list):
        self.elements = elements
    def __repr__(self):
        return f"Sequence({self.elements})"
