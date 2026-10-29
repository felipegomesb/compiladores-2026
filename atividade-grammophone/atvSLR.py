"""
Parser SLR(1) para expressões aritméticas e atribuições.

Simula um autômato com pilha dirigido pela tabela action-goto gerada pelo
Grammophone (Tabela 1 da Aula 11), reproduzindo o formato da Figura 1.

Uso:
    python parser_slr1.py entrada.exp
    python parser_slr1.py entrada.exp --quiet   (somente Accepted/Rejected)

Gramática (numeração das regras = Grammophone):
     1: S -> E
     2: S -> V = E
     3: E -> E + T
     4: T -> T * F
     5: F -> ( E )
     6: E -> E - T
     7: E -> T
     8: T -> T / F
     9: T -> F
    10: F -> V
    11: V -> id
    12: F -> num
"""

import re
import sys

RULES = {
    1: ("S", 1, "S -> E"),
    2: ("S", 3, "S -> V = E"),
    3: ("E", 3, "E -> E + T"),
    4: ("T", 3, "T -> T * F"),
    5: ("F", 3, "F -> ( E )"),
    6: ("E", 3, "E -> E - T"),
    7: ("E", 1, "E -> T"),
    8: ("T", 3, "T -> T / F"),
    9: ("T", 1, "T -> F"),
    10: ("F", 1, "F -> V"),
    11: ("V", 1, "V -> id"),
    12: ("F", 1, "F -> num"),
}


# Tabela ACTION: ACTION[estado][terminal] = ("s", n) | ("r", k) | ("acc",)
ACTION = {}
GOTO = {}


def _reduce_on(state, rule, terminals):
    for t in terminals:
        ACTION.setdefault(state, {})[t] = ("r", rule)


def _shift(state, terminal, target):
    ACTION.setdefault(state, {})[terminal] = ("s", target)


# Conjuntos de lookahead (FOLLOW) usados nas reduções
F_ALL = ["+", "*", ")", "-", "/", "$"]             # FOLLOW(F), FOLLOW(T) completos
F_E = ["+", ")", "-", "$"]                         # FOLLOW(E)
F_V = ["=", "+", "*", ")", "-", "/", "$"]          # FOLLOW(V)


def _shift_operands(state):
    _shift(state, "(", 7)
    _shift(state, "id", 5)
    _shift(state, "num", 8)


# Estados go to

# Estado 0
_shift_operands(0)
GOTO[0] = {"S": 1, "E": 2, "V": 3, "T": 4, "F": 6}
# Estado 1
ACTION[1] = {"$": ("acc",)}
# Estado 2
_shift(2, "+", 9)
_shift(2, "-", 10)
_reduce_on(2, 1, ["$"])
# Estado 3
_shift(3, "=", 11)
_reduce_on(3, 10, F_ALL)
# Estado 4
_shift(4, "*", 12)
_shift(4, "/", 13)
_reduce_on(4, 7, F_E)
# Estado 5
_reduce_on(5, 11, F_V)
# Estado 6
_reduce_on(6, 9, F_ALL)
# Estado 7
_shift_operands(7)
GOTO[7] = {"E": 14, "V": 15, "T": 4, "F": 6}
# Estado 8
_reduce_on(8, 12, F_ALL)
# Estado 9
_shift_operands(9)
GOTO[9] = {"V": 15, "T": 16, "F": 6}
# Estado 10
_shift_operands(10)
GOTO[10] = {"V": 15, "T": 17, "F": 6}
# Estado 11
_shift_operands(11)
GOTO[11] = {"E": 18, "V": 15, "T": 4, "F": 6}
# Estado 12
_shift_operands(12)
GOTO[12] = {"V": 15, "F": 19}
# Estado 13
_shift_operands(13)
GOTO[13] = {"V": 15, "F": 20}
# Estado 14
_shift(14, "+", 9)
_shift(14, ")", 21)
_shift(14, "-", 10)
# Estado 15
_reduce_on(15, 10, F_ALL)
# Estado 16
_shift(16, "*", 12)
_shift(16, "/", 13)
_reduce_on(16, 3, F_E)
# Estado 17
_shift(17, "*", 12)
_shift(17, "/", 13)
_reduce_on(17, 6, F_E)
# Estado 18
_shift(18, "+", 9)
_shift(18, "-", 10)
_reduce_on(18, 2, ["$"])
# Estados 19, 20, 21
_reduce_on(19, 4, F_ALL)
_reduce_on(20, 8, F_ALL)
_reduce_on(21, 5, F_ALL)

START_STATE = 0


# Analisador léxico simples: gera a sequência de terminais da tabela
TOKEN_RE = re.compile(
    r"\s*(?:(?P<num>\d+(?:\.\d+)?)|(?P<id>[A-Za-z_]\w*)|(?P<op>[=+\-*/()]))"
)


def tokenize(text):
    """Converte o texto em lista de (terminal, lexema). Levanta ValueError se
    houver caractere inválido."""
    tokens = []
    pos = 0
    text = text.rstrip()
    while pos < len(text):
        m = TOKEN_RE.match(text, pos)
        if not m:
            raise ValueError(f"caractere inválido na posição {pos}: {text[pos:].lstrip()[0]!r}")
        if m.group("num") is not None:
            tokens.append(("num", m.group("num")))
        elif m.group("id") is not None:
            tokens.append(("id", m.group("id")))
        else:
            tokens.append((m.group("op"), m.group("op")))
        pos = m.end()
    tokens.append(("$", "$"))
    return tokens



# Autômato com pilha (shift/reduce)
# Analisador sintático
def parse(tokens, verbose=True):
    """Executa o autômato. Retorna True se a cadeia for aceita."""
    # Pilha alternando símbolos e estados, como na Figura 1: $ 0 E 2 + 9 ...
    stack = ["$", START_STATE]
    pos = 0
    step = 1

    if verbose:
        print(f"{'Passo':<6}{'Pilha':<40}{'Entrada':<34}Ação")

    def show(action):
        if verbose:
            pilha = " ".join(str(x) for x in stack)
            entrada = " ".join(t for t, _ in tokens[pos:])
            print(f"{step:<6}{pilha:<40}{entrada:<34}{action}")

    while True:
        state = stack[-1]
        terminal = tokens[pos][0]
        act = ACTION.get(state, {}).get(terminal)

        if act is None:
            show("ERRO")
            esperados = sorted(ACTION.get(state, {}))
            if verbose:
                print(f"Erro sintático: token {tokens[pos][1]!r} inesperado "
                      f"(token nº {pos + 1}). Esperado: {', '.join(esperados)}")
            return False

        if act[0] == "s":
            show(f"carrega {act[1]}")
            stack.extend([terminal, act[1]])
            pos += 1

        elif act[0] == "r":
            lhs, size, text = RULES[act[1]]
            show(f"reduz {text}")
            del stack[len(stack) - 2 * size:]       # desempilha símbolos e estados
            topo = stack[-1]
            stack.extend([lhs, GOTO[topo][lhs]])    # empilha lhs e estado do goto

        else:
            show("aceita")
            return True
        step += 1


def main():
    if len(sys.argv) < 2:
        raise IOError("Use " + sys.argv[0] + " file.exp")
    if sys.argv[1].split(".")[-1] != "exp":
        raise IOError("Not a .exp file!")

    quiet = "--quiet" in sys.argv[2:]

    with open(sys.argv[1], encoding="utf-8") as f:
        input_string = f.read().strip()
    print("Testing:", input_string)

    try:
        tokens = tokenize(input_string)
    except ValueError as e:
        print(f"Erro léxico: {e}")
        print("Rejected")
        sys.exit(1)

    if parse(tokens, verbose=not quiet):
        print("Accepted")
    else:
        print("Rejected")
        sys.exit(1)


if __name__ == "__main__":
    main()