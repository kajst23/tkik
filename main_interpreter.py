import argparse
import sys
from lark import Lark, LarkError
from lark.exceptions import UnexpectedCharacters, UnexpectedToken
from compiler import MelodyTransformer
from interpreter import MelodyInterpreter

def main():
    parser = argparse.ArgumentParser(description="Realtime Live Interpreter")
    parser.add_argument("--input", default="song.music")
    args = parser.parse_args()

    # 1. Wczytanie gramatyki
    try:
        with open("grammar.lark", "r", encoding="utf-8") as f:
            grammar = f.read()
    except FileNotFoundError:
        print("[-] BŁĄD: Nie znaleziono pliku 'grammar.lark'.")
        sys.exit(1)

    lark_parser = Lark(grammar, parser="lalr", start="program")

    # 2. Wczytanie pliku źródłowego
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            src = f.read()
    except FileNotFoundError:
        print(f"[-] BŁĄD: Brak pliku wejściowego '{args.input}'.")
        sys.exit(1)

    # 3. Analiza składniowa (Parsowanie z WŁASNYMI OPISAMI)
    try:
        tree = lark_parser.parse(src)
    except UnexpectedCharacters as e:
        print("\n" + "="*50)
        print(f"❌ [BŁĄD LEKSYKALNY] Znaleziono nieznany znak!")
        print(f"📍 Miejsce: Linia {e.line}, Kolumna {e.column}")
        print(f"🔍 Znak, który wywołał błąd: '{e.char}'")
        print("💡 Wskazówka: Sprawdź, czy nie użyto polskich znaków (np. ą, ł, ź) poza komentarzami.")
        print("="*50 + "\n")
        sys.exit(1)
    except UnexpectedToken as e:
        print("\n" + "="*50)
        print(f"❌ [BŁĄD SKŁADNIOWY] Nieoczekiwany element w kodzie!")
        print(f"📍 Miejsce: Linia {e.line}, Kolumna {e.column}")
        print(f"🔍 Napotkano: '{e.token.value}'")
        
        # Lark przechowuje oczekiwane tokeny w e.expected
        expected = ", ".join(e.expected)
        print(f"🎯 Oczekiwano jednego z: {expected}")
        print("💡 Wskazówka: Sprawdź czy nie brakuje przecinka, nawiasu zamykającego ']' lub znaku równe '='.")
        print("="*50 + "\n")
        sys.exit(1)
    except LarkError as e:
        # Awaryjne przechwycenie innych błędów parsera
        print("\n❌ [KRYTYCZNY BŁĄD PARSERA]")
        print(e)
        sys.exit(1)

    # 4. Transformacja AST i semantyka
    try:
        transformer = MelodyTransformer()
        ast_processed = transformer.transform(tree)
    except Exception as e:
        print("\n" + "="*50)
        print(f"❌ [BŁĄD SEMANTYCZNY] Logika utworu zawiera błąd:")
        print(f"🔍 Szczegóły: {e}")
        print("="*50 + "\n")
        sys.exit(1)

    # 5. Uruchomienie odtwarzania
    interpreter = MelodyInterpreter()
    try:
        interpreter.run(ast_processed)
    except KeyboardInterrupt:
        print("\n[!] Odtwarzanie przerwane przez użytkownika.")
    except Exception as e:
        print(f"\n❌ [BŁĄD WYKONANIA (RUNTIME)]: {e}")

if __name__ == "__main__":
    main()