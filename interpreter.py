import time
import mido
from runtime_types import Note, Chord, Rest, Sequence

class MelodyInterpreter:
    def __init__(self):
        self.tempo = 120
        self.gate = 0.85 
        self.outport = None
        
        print("[*] Szukanie dostepnych wyjsc audio/MIDI...")
        outputs = mido.get_output_names()
        
        if outputs:
            try:
                self.outport = mido.open_output(outputs[0])
                print(f"[+] Polaczono z urzadzeniem dzwiekowym: {outputs[0]}")
            except OSError:
                print("[-] Nie udalo sie otworzyc domyslnego portu.")
        
        if not self.outport:
            try:
                self.outport = mido.open_output('MelodyLang Synth', virtual=True)
                print("[+] Utworzono wirtualny port MIDI: 'MelodyLang Synth'")
            except OSError:
                print("[!] OSTRZEZENIE: Brak urzadzen audio. Tryb tekstowy (MUTE).")

    def run(self, ast):
        try:
            for statement in ast:
                self.execute(statement)
        except KeyboardInterrupt:
            print("\n[-] Odtwarzanie przerwane przez uzytkownika (Ctrl+C).")
        except Exception as e:
            print(f"\n[BLAD RUNTIME] Krytyczny blad interpretera: {e}")
        finally:
            if self.outport:
                print("[*] Resetowanie i zamykanie portu MIDI...")
                try:
                    self.outport.reset() 
                except AttributeError:
                    pass 
                self.outport.close()

    def execute(self, stmt):
        if not stmt:
            return
        
        if isinstance(stmt, list):
            for s in stmt:
                self.execute(s)
            return

        if not isinstance(stmt, dict):
            raise TypeError(f"Nieoczekiwana struktura w AST. Oczekiwano slownika, otrzymano: {type(stmt)}")

        stmt_type = stmt.get("type")

        if stmt_type == "set_param":
            if stmt.get("name") == "TEMPO":
                val = stmt.get("value", 120)
                if val <= 0:
                    raise ValueError(f"Tempo musi byc wieksze od 0! Podano: {val}")
                self.tempo = val
                print(f"[*] [TEMPO] Zmiana tempa na: {self.tempo} BPM")

        elif stmt_type == "track":
            print(f"[*] [TRACK] Rozpoczynam odtwarzanie sciezki: {stmt.get('name', 'Nieznana')}")
            self.execute(stmt.get("body", []))

        elif stmt_type == "play":
            val = stmt.get("value")
            times = stmt.get("times", 1)
            
            if not isinstance(times, int) or times < 1:
                raise ValueError(f"Parametr LOOP (times) musi byc liczba calkowita wieksza od 0. Podano: {times}")
                
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
        else:
            raise TypeError(f"Nieznany typ wartosci do odtworzenia: {type(val)}")

    def calculate_duration(self, duration_type) -> float:
        try:
            dur_val = float(duration_type)
            if dur_val <= 0:
                raise ValueError(f"Dlugosc nuty musi byc wieksza od 0! Podano: {duration_type}")
            
            # NOWY SYSTEM ZGODNY ZE STANDARDEM MUZYCZNYM
            # 1 = cala nuta, 2 = polnuta, 4 = cwiercnuta, 8 = osemka
            beats = 4.0 / dur_val
        except (ValueError, TypeError):
            raise ValueError(f"Nie udalo sie obliczyc czasu trwania. Niewlasciwa wartosc rytmiczna: {duration_type}")
            
        if self.tempo <= 0:
            raise ValueError("Brak zdefiniowanego tempa (lub tempo <= 0).")
            
        return beats * (60.0 / self.tempo)

    def validate_midi_range(self, midi_num):
        if not (0 <= midi_num <= 127):
            raise ValueError(f"Zbyt wysoki/niski dzwiek! Wartosc MIDI ({midi_num}) jest poza bezpiecznym zakresem 0-127.")
        return midi_num

    def play_note(self, note: Note):
        total_duration = self.calculate_duration(note.duration)
        sound_duration = total_duration * self.gate
        rest_duration = total_duration - sound_duration
        
        midi_num = self.validate_midi_range(note.to_midi())
        print(f"  -> Gram nute: {note.pitch}{note.octave} (MIDI {midi_num}) przez {total_duration:.2f}s")
        
        if self.outport:
            self.outport.send(mido.Message('note_on', note=midi_num, velocity=105))
            time.sleep(sound_duration)
            self.outport.send(mido.Message('note_off', note=midi_num, velocity=0))
            time.sleep(rest_duration)
        else:
            time.sleep(total_duration)

    def play_chord(self, chord: Chord):
        total_duration = self.calculate_duration(chord.duration)
        sound_duration = total_duration * self.gate
        rest_duration = total_duration - sound_duration
        
        print(f"  -> Gram akord ({total_duration:.2f}s): {[f'{n.pitch}{n.octave}' for n in chord.notes]}")
        
        # Weryfikacja wszystkich nut przed odtworzeniem
        midi_nums = [self.validate_midi_range(n.to_midi()) for n in chord.notes]
        
        if self.outport:
            for midi_num in midi_nums:
                self.outport.send(mido.Message('note_on', note=midi_num, velocity=95))
            time.sleep(sound_duration)
            for midi_num in midi_nums:
                self.outport.send(mido.Message('note_off', note=midi_num, velocity=0))
            time.sleep(rest_duration)
        else:
            time.sleep(total_duration)

    def play_rest(self, rest: Rest):
        duration_sec = self.calculate_duration(rest.duration)
        print(f"  -> [PAUZA] Odczekanie {duration_sec:.2f}s")
        time.sleep(duration_sec)