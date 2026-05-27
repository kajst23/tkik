import re
from lark import Transformer
from runtime_types import Integer, Note, Chord, Rest, Sequence

class MelodyTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self.symbol_table = {}

    def program(self, items):
        return [item for item in items if item is not None and getattr(item, 'get', lambda x: None)('type') != 'assignment']

    def set_param(self, items):
        return {"type": "set_param", "name": str(items[0]), "value": int(items[1])}

    def assignment(self, items):
        var_name = str(items[0])
        val = items[1]
        self.symbol_table[var_name] = val
        return {"type": "assignment", "name": var_name, "value": val}

    def track_def(self, items):
        track_name = str(items[0])
        body = []
        for b in items[1:]:
            if isinstance(b, list):
                body.extend(b)
            else:
                body.append(b)
        return {"type": "track", "name": track_name, "body": body}

    def loop_block(self, items):
        iterations = int(items[0])
        body = items[1:]
        flat_body = []
        for b in body:
            if isinstance(b, list):
                flat_body.extend(b)
            else:
                flat_body.append(b)
        
        unrolled = []
        for _ in range(iterations):
            unrolled.extend(flat_body)
        return unrolled

    def play_func(self, items):
        expr_val = items[0]
        times = int(items[1]) if len(items) > 1 else 1
        return {"type": "play", "value": expr_val, "times": times}

    def int_expr(self, items):
        # Sprawdzamy czy pierwszy element to znak minusa
        if len(items) == 2 and str(items[0]) == "-":
            val = -int(items[1])
        # Awaryjnie, gdyby Lark przekazał to jako jeden scalony ciąg tekstowy (np. "-12")
        elif len(items) == 1 and str(items[0]).startswith("-"):
            val = int(str(items[0]))
        else:
            val = int(items[0])
            
        return Integer(val)
    
    def note_expr(self, items):
        return items[0]

    def chord_expr(self, items):
        return items[0]

    def rest_expr(self, items):
        return items[0]

    def seq_expr(self, items):
        return items[0]

    def macro_expr(self, items):
        return items[0]

    def var_reference(self, items):
        var_name = str(items[0])
        if var_name not in self.symbol_table:
            raise ValueError(f"Semantic Error: Użycie niezdefiniowanej zmiennej '{var_name}'")
        return self.symbol_table[var_name]

    def sequence(self, items):
        flat_elements = []
        for item in items:
            if isinstance(item, Sequence):
                flat_elements.extend(item.elements)
            else:
                flat_elements.append(item)
        return Sequence(flat_elements)

    def note(self, items):
        raw_pitch = str(items[0])
        match = re.match(r"([A-G][b#]?)([0-9]?)", raw_pitch)
        pitch = match.group(1)
        octave = int(match.group(2)) if match.group(2) else 4
        duration = items[1] if len(items) > 1 and items[1] is not None else 4
        return Note(pitch, octave, duration)

    def chord(self, items):
        duration = 4
        pitches = []
        for item in items:
            if isinstance(item, int):
                duration = item
            elif item is not None:
                match = re.match(r"([A-G][b#]?)([0-9]?)", str(item))
                p = match.group(1)
                o = int(match.group(2)) if match.group(2) else 4
                pitches.append({"pitch": p, "octave": o})
        return Chord(pitches, duration)

    def rest(self, items):
        duration = 4
        for item in items:
            if item is not None:
                # Ignorujemy sam znak pauzy 'P'
                if str(item) == 'P':
                    continue
                # Jeśli to obiekt Integer z systemu typów lub Token, wyciągamy wartość liczbową
                if hasattr(item, 'value'):
                    duration = int(item.value)
                else:
                    try:
                        duration = int(str(item))
                    except ValueError:
                        continue
        return Rest(duration)
    

    def duration(self, items):
        return int(items[0])

    def macro_call(self, items):
        macro_name = str(items[0]).upper()
        args = items[1:]

        if macro_name == "TRANSPOSE":
            target = args[0]
            steps = args[1].value
            import copy
            if isinstance(target, Sequence):
                new_elems = []
                for el in target.elements:
                    if hasattr(el, 'transpose'):
                        cloned = copy.deepcopy(el)
                        cloned.transpose(steps)
                        new_elems.append(cloned)
                    else:
                        new_elems.append(el)
                return Sequence(new_elems)
            elif hasattr(target, 'transpose'):
                cloned = copy.deepcopy(target)
                cloned.transpose(steps)
                return cloned
            return target

        elif macro_name == "REVERSE":
            target = args[0]
            if isinstance(target, Sequence):
                return Sequence(list(reversed(target.elements)))
            return target

        else:
            raise ValueError(f"Runtime Error: Nieznane makro '{macro_name}'")
