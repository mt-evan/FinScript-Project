from textx import metamodel_from_file
import re
import sys

# Load the meta-model
finscript_mm = metamodel_from_file('FinScript.tx')

class FinScriptInterpreter:
    def __init__(self):
        self.state = {}

    def math_parser(self, expr):

        # Replace multi-character operators (==, !=, <=, >=) after tokenization
        expr = expr.replace("==", " __EQUAL__ ")
        expr = expr.replace("!=", " __NOT_EQUAL__")
        expr = expr.replace(">=", " __GREATER_EQUAL__ ")
        expr = expr.replace("<=", " __LESSER_EQUAL__ ")

        # Replace logical operators and boolean values
        expr = expr.replace("||", " or ")
        expr = expr.replace("&&", " and ")
        expr = expr.replace("!", " not ")
        expr = expr.replace("true", "True").replace("false", "False")

        # Tokenize the expression first without replacing operators
        tokens = re.findall(r'\d+\.\d+|\d+|[a-zA-Z_][a-zA0-9_]*|[+\-*/%()=<>&!|]|\b(?:==|!=|<=|>=)\b', expr)

        # Replace multi-character operators
        tokens = [token.replace("__EQUAL__", "==")
                  .replace("__NOT_EQUAL__", "!=")
                  .replace("__GREATER_EQUAL__", ">=")
                  .replace("__LESSER_EQUAL__", "<=")
                  for token in tokens]

        # Replace variables with their values from the state
        for i, token in enumerate(tokens):
            if token in self.state:
                tokens[i] = str(self.state[token])
            elif re.match(r'[a-zA-Z_][a-zA-Z0-9_]*', token) and token not in ['and', 'or', 'not', 'True', 'False']:  # If it's a variable not in state and not a keyword like "and" or "or"
                print(f"Error: Variable '{token}' not defined.")  # For debugging

        # Now reassemble the tokens and replace operators correctly
        expr = " ".join(tokens)

        try:
            result = eval(expr)
        except Exception as e:
            print(f"Error evaluating expression '{expr}': {e}")
            sys.exit(1)

        return result


    def interpret(self, model):
        # Ensure the input is iterable
        statements = model if isinstance(model, list) else model.statements

        for s in statements:
            # Output
            if s.__class__.__name__ == "PrintString":
                print(s.content)
            elif s.__class__.__name__ == "Print":
                if s.content in self.state:
                    print(self.state[s.content])
                else:
                    print(f"Variable '{s.content}' not declared")
                    sys.exit(1)

            # Declaration
            elif s.__class__.__name__ == "Declaration":
                if s.var in self.state:
                    print(f"Variable '{s.var}' already declared")
                    sys.exit(1)
                value_to_store = self.math_parser(str(s.expr))
                self.state[s.var] = value_to_store

            # Reassignment
            elif s.__class__.__name__ == "Reassignment":
                if s.var not in self.state:
                    print(f"Variable '{s.var}' not declared")
                    sys.exit(1)
                value_to_store = self.math_parser(str(s.expr))
                self.state[s.var] = value_to_store

            # If Statement
            elif s.__class__.__name__ == "IfStatement":
                condition_result = self.math_parser(str(s.condition))
                if condition_result:
                    self.interpret(s.thenBody)
                else:
                    executed_elif = False
                    for elif_clause in s.elifClauses:
                        elif_condition_result = self.math_parser(str(elif_clause.condition))
                        if elif_condition_result:
                            self.interpret(elif_clause.body)
                            executed_elif = True
                            break
                    if not executed_elif and s.elseBody:
                        self.interpret(s.elseBody)

            # For Loop
            elif s.__class__.__name__ == "ForLoop":
                start = self.math_parser(str(s.start))
                end = self.math_parser(str(s.end))
                if s.var in self.state:
                    print(f"Variable '{s.var}' already declared")
                    sys.exit(1)
                for i in range(start, end + 1):
                    self.state[s.var] = i
                    self.interpret(s.body)
                del self.state[s.var]  # Remove loop variable after the loop

            # While Loop
            elif s.__class__.__name__ == "WhileLoop":
                while self.math_parser(str(s.condition)):
                    self.interpret(s.body)




# Test Program
finscript_model = finscript_mm.model_from_file('sandbox.fin')
interpreter = FinScriptInterpreter()
interpreter.interpret(finscript_model)
