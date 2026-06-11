import argparse
import sys
from lark import Lark, LarkError
from lark.exceptions import UnexpectedCharacters, UnexpectedToken
from compiler import MelodyTransformer

from midi_gen import MidiGenerator 

def main():
    parser = argparse.ArgumentParser(description="Kompilator MelodyLang do pliku MIDI")
    parser.add_argument("--input", required=True, help="Plik wejściowy .music")
    parser.add_argument("--output", default="output.mid", help="Plik wyjściowy .mid")
    args = parser.parse_args()

    print("[*] Wczytywanie gramatyki z grammar.lark...")
    try:
        with open("grammar.lark", "r", encoding="utf-8") as f:
            grammar = f.read()
    except FileNotFoundError:
        print("[-] BŁĄD: Nie znaleziono pliku 'grammar.lark'.")
        sys.exit(1)

    lark_parser = Lark(grammar, parser="lalr", start="program")

    print(f"[*] Parsowanie kodu źródłowego: {args.input}...")
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            src = f.read()
    except FileNotFoundError:
        print(f"[-] BŁĄD: Brak pliku wejściowego '{args.input}'.")
        sys.exit(1)

    try:
        tree = lark_parser.parse(src)
    except UnexpectedCharacters as e:
        print("\n" + "="*50)
        print(f"[-] [BŁĄD LEKSYKALNY] Znaleziono nieznany znak!")
        print(f"[*] Miejsce: Linia {e.line}, Kolumna {e.column}")
        print(f"[*] Znak, który wywołał błąd: '{e.char}'")
        print("[!] Wskazówka: Sprawdź, czy nie użyto polskich znaków (np. ą, ł, ź) poza komentarzami.")
        print("="*50 + "\n")
        sys.exit(1)
    except UnexpectedToken as e:
        print("\n" + "="*50)
        print(f"[-] [BŁĄD SKŁADNIOWY] Nieoczekiwany element w kodzie!")
        print(f"[*] Miejsce: Linia {e.line}, Kolumna {e.column}")
        print(f"[*] Napotkano: '{e.token.value}'")
        expected = ", ".join(e.expected)
        print(f"[*] Oczekiwano jednego z: {expected}")
        print("[!] Wskazówka: Sprawdź czy nie brakuje przecinka, nawiasu zamykającego ']' lub znaku równe '='.")
        print("="*50 + "\n")
        sys.exit(1)
    except LarkError as e:
        print("\n[-] [KRYTYCZNY BŁĄD PARSERA]")
        print(e)
        sys.exit(1)

    try:
        transformer = MelodyTransformer()
        ast_processed = transformer.transform(tree)
    except Exception as e:
        print("\n" + "="*50)
        print(f"[-] [BŁĄD SEMANTYCZNY] Logika utworu zawiera błąd:")
        print(f"[*] Szczegóły: {e}")
        print("="*50 + "\n")
        sys.exit(1)

    print(f"[*] Generowanie pliku MIDI: {args.output}...")
    try:
        generator = MidiGenerator(ast_processed)
        generator.generate()
        generator.save(args.output)
        print(f"[+] Gotowe! Plik zapisano jako {args.output}")
    except Exception as e:
        print(f"\n[-] [BŁĄD GENERATORA MIDI]: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()