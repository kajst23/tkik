import re

PITCH_MAP = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 
    'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 
    'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
}

class MelodyType:
    pass

class Integer(MelodyType):
    def __init__(self, value):
        self.value = int(value)
        
    def __repr__(self):
        return f"Integer({self.value})"

class Note(MelodyType):
    # Domyślna długość to 4 (ćwierćnuta)
    def __init__(self, pitch: str, octave, duration=4):
        self.pitch = str(pitch)
        self.octave = int(octave)
        self.duration = float(duration)

    def to_midi(self) -> int:
        return (self.octave + 1) * 12 + PITCH_MAP[self.pitch]

    def transpose(self, half_steps: int):
        current_midi = self.to_midi()
        new_midi = current_midi + int(half_steps)
        self.octave = (new_midi // 12) - 1
        note_index = new_midi % 12
        # Pobieranie pierwszej pasującej nazwy z mapy dla danego indeksu MIDI
        self.pitch = [k for k, v in PITCH_MAP.items() if v == note_index][0]

    def __repr__(self):
        # Formatowanie estetyczne (np. 4.0 wyświetli jako 4)
        dur = int(self.duration) if self.duration.is_integer() else self.duration
        return f"Note({self.pitch}{self.octave}:{dur})"

class Chord(MelodyType):
    def __init__(self, pitches: list, duration=4):
        self.duration = float(duration)
        # Tworzenie obiektów Note na podstawie przekazanych słowników
        self.notes = [Note(p["pitch"], p["octave"], self.duration) for p in pitches]

    def transpose(self, half_steps: int):
        for note in self.notes:
            note.transpose(half_steps)

    def __repr__(self):
        dur = int(self.duration) if self.duration.is_integer() else self.duration
        return f"Chord({self.notes}, duration={dur})"

class Rest(MelodyType):
    def __init__(self, duration=4):
        self.duration = float(duration)
        
    def __repr__(self):
        dur = int(self.duration) if self.duration.is_integer() else self.duration
        return f"Rest(P:{dur})"

class Sequence(MelodyType):
    def __init__(self, elements: list):
        self.elements = elements
        
    def __repr__(self):
        return f"Sequence({self.elements})"