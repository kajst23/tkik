import time
import mido
from runtime_types import Note, Chord, Rest, Sequence

class MelodyInterpreter:
    def __init__(self):
        self.tempo = 120
        try:
            self.outport = mido.open_output()
            print("[+] Port MIDI otwarty pomyślnie.")
        except OSError:
            self.outport = None
            print("[!] OSTRZEŻENIE: Brak sprzętowego MIDI. Tryb konsolowy (MUTE).")

    def run(self, ast):
        for statement in ast:
            self.execute(statement)

    def execute(self, stmt):
        if not stmt:
            return
        if isinstance(stmt, list):
            for s in stmt:
                self.execute(s)
            return

        stmt_type = stmt.get("type")

        if stmt_type == "set_param":
            if stmt["name"] == "TEMPO":
                self.tempo = stmt["value"]
                print(f"[*] [TEMPO] {self.tempo} BPM")

        elif stmt_type == "track":
            print(f"[*] [TRACK] Odtwarzanie ścieżki: {stmt['name']}")
            self.execute(stmt["body"])

        elif stmt_type == "play":
            val = stmt["value"]
            times = stmt["times"]
            for _ in range(times):
                self.play_value(val)

    def play_value(self, val):
        if isinstance(val, Sequence):
            for element in val.elements:
                self.play_value(element)
        elif isinstance(val, Note):
            self.play_note(val)
        elif isinstance(val, Chord):
            self.play_chord(val)
        elif isinstance(val, Rest):
            self.play_rest(val)

    def calculate_duration(self, duration_type) -> float:
        beats = 4.0 / duration_type
        return beats * (60.0 / self.tempo)

    def play_note(self, note: Note):
        duration_sec = self.calculate_duration(note.duration)
        midi_num = note.to_midi()
        print(f"  -> Nuta: {note.pitch}{note.octave} ({duration_sec:.2f}s)")
        if self.outport:
            self.outport.send(mido.Message('note_on', note=midi_num, velocity=100))
            time.sleep(duration_sec)
            self.outport.send(mido.Message('note_off', note=midi_num, velocity=0))
        else:
            time.sleep(duration_sec)

    def play_chord(self, chord: Chord):
        duration_sec = self.calculate_duration(chord.duration)
        print(f"  -> Akord ({duration_sec:.2f}s): {[f'{n.pitch}{n.octave}' for n in chord.notes]}")
        if self.outport:
            for note in chord.notes:
                self.outport.send(mido.Message('note_on', note=note.to_midi(), velocity=90))
            time.sleep(duration_sec)
            for note in chord.notes:
                self.outport.send(mido.Message('note_off', note=note.to_midi(), velocity=0))
        else:
            time.sleep(duration_sec)

    def play_rest(self, rest: Rest):
        duration_sec = self.calculate_duration(rest.duration)
        print(f"  -> [PAUZA] ({duration_sec:.2f}s)")
        time.sleep(duration_sec)
