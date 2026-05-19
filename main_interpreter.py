import argparse
import sys
from lark import Lark, LarkError
from compiler import MelodyTransformer
from interpreter import MelodyInterpreter

def main():
    parser = argparse.ArgumentParser(description="Realtime Live Interpreter")
    parser.add_argument("--input", default="song.music")
    args = parser.parse_args()

    with open("grammar.lark", "r", encoding="utf-8") as f:
        grammar = f.read()

    lark_parser = Lark(grammar, parser="lalr", start="program")

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            src = f.read()
    except FileNotFoundError:
        print(f"[-] Brak pliku {args.input}")
        sys.exit(1)

    try:
        tree = lark_parser.parse(src)
    except LarkError as e:
        print(f"[-] Parser Error:\n{e}")
        sys.exit(1)

    try:
        transformer = MelodyTransformer()
        ast_processed = transformer.transform(tree)
    except Exception as e:
        print(f"[-] Semantic Error:\n{e}")
        sys.exit(1)

    interpreter = MelodyInterpreter()
    try:
        interpreter.run(ast_processed)
    except KeyboardInterrupt:
        print("\n[!] Przerwano.")

if __name__ == "__main__":
    main()
