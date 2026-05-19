# MelodyLang - Kompilator Języka Muzycznego (Transpiler źródło-MIDI)

**Przedmiot:** Techniki Kompilacji i Konfiguracji (TKiK)
**ZESPÓŁ:**
- Kajetan Skitał (kskital@student.agh.edu.pl)

## Opis projektu

Projekt **MelodyLang** to kompleksowy kompilator zbudowany w oparciu o specyfikację DSL (Domain Specific Language) dedykowanego do zapisu i sekwencjonowania utworów muzycznych. Kompilator przetwarza pliki z rozszerzeniem `.music`, przeprowadzając analizę leksykalną i syntaktyczną (z wykorzystaniem biblioteki **Lark**), w celu wygenerowania w pełni funkcjonalnego pliku binarnego MIDI (`.mid`).

Projekt został rozbudowany o bezpośredni interpreter czasu rzeczywistego (bez generowania plików pośrednich .mid), silne typowanie dynamiczne oraz metaprogramowanie przy użyciu makr muzycznych (`@TRANSPOSE`, `@REVERSE`).

Kompilator wspiera:
- Definiowanie struktur blokowych utworów
- Zmienne i operacje podstawiania
- Metaprogramowanie sekwencji muzycznych (pętle, rozwijanie pętli w locie)
- Polimorficzne typy danych takie jak nuty obok całych akordów

## Spis Tokenów

W procesie skanowania tekst wejściowy rozbijany jest na tokeny zaprezentowane w poniższej tabeli:

| Token         | Wzorzec (Regex / String)             | Opis                                                                  |
| ------------- | ------------------------------------ | --------------------------------------------------------------------- |
| `TRACK`       | `"TRACK"`                            | Rozpoczęcie definicji domyślnej ścieżki w utworze.                    |
| `SET`         | `"SET"`                              | Słowo kluczowe służące do ustawiania parametrów globalnych.           |
| `LOOP`        | `"LOOP"`                             | Słowo kluczowe pętli powtarzającej sekwencje muzyczne.                |
| `PLAY`        | `"PLAY"`                             | Wywołanie funkcji odpowiedzialnej za odtworzenie struktur lub zmiennych.|
| `CNAME`       | `/[a-zA-Z_][a-zA-Z0-9_]*/`           | Identyfikator dla nazw zmiennych oraz ścieżek dźwiękowych.            |
| `INT`         | `/[0-9]+/`                           | Wartość liczbowa (tempo, powtórzenia, czas trwania).                  |
| `NOTE_PITCH`  | `/[A-G][b#]?[0-9]?/`                 | Reprezentacja nuty wraz z oktawą (np. C4, F#3, Bb5).                  |
| `REST_CHAR`   | `/P/`                                | Znak pauzy muzycznej.                                                 |

## Architektura Translatora i Interpretera

Rozwinięty potok kompilacji dzieli się na trzy fazy:

1. **Skaner i Parser (LARK)** - `grammar.lark` stanowi rdzeń definiujący parsowanie kodu wejściowego do formy bezkontekstowego drzewa (Parse Tree).
2. **AST Transformer** - `compiler.py` nadpisuje wygenerowane węzły drzewa, wdrażając system typów (`runtime_types.py`) oraz ewaluację makr, ujednolicając wszystko do potężnej struktury gotowej dla wybranego Backend'u. Logika ta również waliduje występowanie symboli (weryfikacja semantyczna).
3. **Generator MIDI lub Live Interpreter**:
   - **MidiGenerator** (`midi_gen.py` / `main.py`) - Iteruje po instrukcjach i konwertuje struktury notacyjne na finalny, binarny plik muzyczny `.mid`.
   - **MelodyInterpreter** (`interpreter.py` / `main_interpreter.py`) - Przetwarza obiekty w locie i odtwarza dźwięki w czasie rzeczywistym poprzez systemowy port MIDI.

## Instrukcja uruchomienia

### Wymagane moduły:
Aby zainstalować wszystkie wymagane moduły, użyj komendy:
```bash
pip install lark midiutil mido python-rtmidiUruchomienie tradycyjne (Transpiler do pliku MIDI):
Aby skompilować plik z kodem (domyślnie użyje example.music i wygeneruje output.mid), użyj:

python main.py --input example.music --output output.mid

Uruchomienie nowego Live Interpretera (Odtwarzanie w locie):
Aby odtworzyć utwór wykorzystujący zaawansowany system typów i makra bezpośrednio na żywo, użyj:

python main_interpreter.py --input song.music
