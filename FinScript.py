from textx import metamodel_from_file
import re
import sys

# Load the meta-model
finscript_mm = metamodel_from_file('FinScript.tx')

# Interpreter Class
class FinScriptInterpreter:
    def __init__(self):
        self.state = {}

    def math_parser(self, expr):
        
        
        # Replace boolean operators and literals with Python equivalents
        expr = expr.replace("||", " or ").replace("&&", " and ")
        expr = expr.replace("true", "True").replace("false", "False")

        
        
        # Tokenize the expression properly (handle comparison operators)
        tokens = re.findall(r'\d+|\w+|[+\-*/()=<>&!|]|==|<=|>=|!=', expr)

        # Replace variable names with their values from the state
        for i, token in enumerate(tokens):
            if token in self.state:  # If the token is a variable
                tokens[i] = str(self.state[token])  # Replace with its value

        # Join the tokens back into a string expression with correct spacing
        evaluated_expr = " ".join(tokens)
        evaluated_expr = evaluated_expr.replace(" = = ", " == ").replace("! = ", " != ")    
        
        try:
            # Evaluate the resulting mathematical/boolean expression
            result = eval(evaluated_expr)
        except Exception as e:
            print(f"Error evaluating expression '{evaluated_expr}': {e}")
            sys.exit(1)

        return result

    def interpret(self, model):
        for s in model.statements:
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

            # Reassignment (using <- operator for assignment)
            elif s.__class__.__name__ == "Reassignment":
                if s.var not in self.state:
                    print(f"Variable '{s.var}' not declared")
                    sys.exit(1)
                value_to_store = self.math_parser(str(s.expr))
                self.state[s.var] = value_to_store

# Test Program
finscript_model = finscript_mm.model_from_file('sandbox.fin')
interpreter = FinScriptInterpreter()
interpreter.interpret(finscript_model)
