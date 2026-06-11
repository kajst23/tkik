from midiutil import MIDIFile

PITCH_MAP = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
    'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
}

class MidiGenerator:
    def __init__(self, events):
        self.events = events
        # Inicjalizujemy MIDIFile. 
        # UWAGA: midiutil domyślnie ma 96 punktów na ćwierćnutę (ticks per beat).
        self.midi = MIDIFile(1)  
        self.track = 0
        self.channel = 0
        self.time = 0.0  # Czas w ćwierćnutach (beats)
        self.tempo = 120
        self.midi.addTempo(self.track, self.time, self.tempo)

    def _pitch_to_midi_num(self, pitch, octave):
        return (octave + 1) * 12 + PITCH_MAP[pitch]

    def generate(self):
        # Resetujemy czas przed generowaniem, na wypadek wielokrotnego uruchomienia
        self.time = 0.0 
        
        # PPQN (Ticks Per Beat) w Twoim systemie wejściowym.
        # Jeśli 1 ćwierćnuta w Twoich danych wejściowych 'events' ma duration = 12, to PPQN = 12.0 jest OK.
        # Jeśli 1 ćwierćnuta ma duration = 4, zmień na 4.0.
        PPQN = 12.0 

        for event in self.events:
            if event["type"] == "set_param":
                if event["name"] == "TEMPO":
                    self.tempo = event["value"]
                    # Ważne: addTempo w midiutil zawsze oczekuje czasu w "beats" (ćwierćnutach)
                    self.midi.addTempo(self.track, self.time, self.tempo)
                elif event["name"] == "INSTRUMENT":
                    # Program change (zmiana instrumentu) - zakres 0-127
                    self.midi.addProgramChange(self.track, self.channel, self.time, event["value"] - 1)
            
            elif event["type"] == "note":
                midi_pitch = self._pitch_to_midi_num(event["pitch"], event["octave"])
                duration_in_beats = event["duration"] / PPQN
                
                # Dodajemy nutę i przesuwamy czas o jej długość
                self.midi.addNote(self.track, self.channel, midi_pitch, self.time, duration_in_beats, 100)
                self.time += duration_in_beats

            elif event["type"] == "chord":
                duration_in_beats = event["duration"] / PPQN
                
                # Wszystkie nuty w akordzie zaczynają się w tym samym czasie (self.time)
                for p in event["pitches"]:
                    midi_pitch = self._pitch_to_midi_num(p["pitch"], p["octave"])
                    self.midi.addNote(self.track, self.channel, midi_pitch, self.time, duration_in_beats, 100)
                
                # Dopiero po dodaniu WSZYSTKICH nut z akordu przesuwamy czas w przód
                self.time += duration_in_beats

            elif event["type"] == "rest":
                # Pauza po prostu przesuwa czas do przodu, nie generując dźwięku
                duration_in_beats = event["duration"] / PPQN
                self.time += duration_in_beats

    def save(self, filepath):
        with open(filepath, "wb") as output_file:
            self.midi.writeFile(output_file)