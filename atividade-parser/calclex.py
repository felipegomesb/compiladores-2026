# ------------------------------------------------------------
# calclex.py
#
# tokenizer for a simple expression evaluator for
# numbers and +,-,*,/
# ------------------------------------------------------------
import ply.lex as lex

# List of token names.   This is always required
tokens = (
   'NUMBER',
   'PLUS',
   'MINUS',
   'TIMES',
   'DIVIDE',
   'LPAREN',
   'RPAREN',
   'AND', 
   'OR',
   'NOT'
)

# Regular expression rules for simple tokens
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_OR      = r'\|\|'
t_AND     = r'\&\&'
t_NOT     = r'!'

# A regular expression rule with some action code
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)    
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

# ------------------------------------------------------------
# EXECUÇÃO E TESTES
# ------------------------------------------------------------
if __name__ == '__main__':

    data = "3 + 5 * (10 - 2) && !0 || 14"

    print(f"Entrada de teste: {data}\n")
    print(f"{'TOKEN':<10} | {'VALOR':<10} | {'LINHA':<6} | {'POSIÇÃO':<8}")
    print("-" * 42)

    lexer.input(data)

    for tok in lexer:
        print(f"{tok.type:<10} | {str(tok.value):<10} | {tok.lineno:<6} | {tok.lexpos:<8}")

