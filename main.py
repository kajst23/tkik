import argparse
from lark import Lark
from compiler import MelodyTransformer
from midi_gen import MidiGenerator

def main():
    parser = argparse.ArgumentParser(description="Zbuduj plik wykonywalny (.mid) z kodu źródłowego MelodyLang.")
    parser.add_argument("--input", default="example.music", help="Ścieżka do pliku wejściowego (.music)")
    parser.add_argument("--output", default="output.mid", help="Ścieżka do pliku wyjściowego (.mid)")
    args = parser.parse_args()

    print(f"[*] Wczytywanie gramatyki z grammar.lark...")
    with open("grammar.lark", "r", encoding="utf-8") as f:
        grammar = f.read()

    lark_parser = Lark(grammar, parser="lalr", start="program")

    print(f"[*] Parsowanie kodu źródłowego: {args.input}...")
    with open(args.input, "r", encoding="utf-8") as f:
        src = f.read()

    tree = lark_parser.parse(src)
    
    print("[*] Generowanie Drzewa Składniowego (AST) i spłaszczanie...")
    transformer = MelodyTransformer()
    ast_processed = transformer.transform(tree)

    print(f"[*] Transformacja na strumień zdarzeń i zapis MIDI do {args.output}...")
    midi_gen = MidiGenerator(ast_processed)
    midi_gen.generate()
    midi_gen.save(args.output)
    
    print(f"[+] Kompilacja zakończona pomyślnie. Utworzono plik MIDI: {args.output}")

if __name__ == "__main__":
    main()
