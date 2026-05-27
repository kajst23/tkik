import time
import mido
from runtime_types import Note, Chord, Rest, Sequence

class MelodyInterpreter:
    def __init__(self):
        self.tempo = 120
        self.outport = None
        
        print("[*] Szukanie dostępnych wyjść audio/MIDI...")
        outputs = mido.get_output_names()
        
        if outputs:
            # Wybieramy pierwszy dostępny syntezator (np. Microsoft GS Wavetable na Windows)
            try:
                self.outport = mido.open_output(outputs[0])
                print(f"[+] Połączono z urządzeniem dźwiękowym: {outputs[0]}")
            except OSError:
                print("[-] Nie udało się otworzyć domyślnego portu. Próba otwarcia portu wirtualnego...")
        
        if not self.outport:
            try:
                # Jeśli to Linux/macOS, próba stworzenia wirtualnego portu
                self.outport = mido.open_output('MelodyLang Synth', virtual=True)
                print("[+] Utworzono wirtualny port MIDI: 'MelodyLang Synth'")
            except OSError:
                print("[!] OSTRZEŻENIE: Brak urządzeń audio. Interpreter uruchomi się w trybie tekstowym (MUTE).")

    def run(self, ast):
        for statement in ast:
            self.execute(statement)
        # Zamknięcie portu po zakończeniu utworu
        if self.outport:
            self.outport.close()

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
                print(f"[*] [TEMPO] Zmiana tempa na: {self.tempo} BPM")

        elif stmt_type == "track":
            print(f"[*] [TRACK] Rozpoczynam odtwarzanie ścieżki: {stmt['name']}")
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
        # duration 4 = ćwierćnuta (1 uderzenie) -> 60 / tempo
        beats = 4.0 / duration_type
        return beats * (60.0 / self.tempo)

    def play_note(self, note: Note):
        duration_sec = self.calculate_duration(note.duration)
        midi_num = note.to_midi()
        
        print(f"  -> Gram nutę: {note.pitch}{note.octave} (MIDI {midi_num}) przez {duration_sec:.2f}s")
        
        if self.outport:
            # Wysyłamy sygnał naciśnięcia klawisza (włącz dźwięk)
            self.outport.send(mido.Message('note_on', note=midi_num, velocity=100))
            time.sleep(duration_sec)
            # Wysyłamy sygnał puszczenia klawisza (wyłącz dźwięk)
            self.outport.send(mido.Message('note_off', note=midi_num, velocity=0))
        else:
            time.sleep(duration_sec)

    def play_chord(self, chord: Chord):
        duration_sec = self.calculate_duration(chord.duration)
        print(f"  -> Gram akord ({duration_sec:.2f}s): {[f'{n.pitch}{n.octave}' for n in chord.notes]}")
        
        if self.outport:
            # Włącz wszystkie nuty w akordzie równocześnie
            for note in chord.notes:
                self.outport.send(mido.Message('note_on', note=note.to_midi(), velocity=90))
            
            time.sleep(duration_sec)
            
            # Wyłącz wszystkie nuty w akordzie równocześnie
            for note in chord.notes:
                self.outport.send(mido.Message('note_off', note=note.to_midi(), velocity=0))
        else:
            time.sleep(duration_sec)

    def play_rest(self, rest: Rest):
        duration_sec = self.calculate_duration(rest.duration)
        print(f"  -> [PAUZA] Odczekanie {duration_sec:.2f}s")
        time.sleep(duration_sec)