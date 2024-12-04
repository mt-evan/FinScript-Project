from textx import metamodel_from_file
import re
import sys

# Load the meta-model
finscript_mm = metamodel_from_file('FinScript.tx')

class FinScriptInterpreter:
    def __init__(self):
        self.state = {}

    def math_parser(self, expr):
    # Replace FinScript operators with Python equivalents
        expr = expr.replace("||", " or ").replace("&&", " and ")
        expr = expr.replace("true", "True").replace("false", "False")
        expr = expr.replace("!", " not ")

        # Tokenize the expression
        tokens = re.findall(r'\d+|\w+|[+\-*/%()=<>&!|]|==|<=|>=|!=', expr)
        for i, token in enumerate(tokens):
            if token in self.state:
                tokens[i] = str(self.state[token])

        # Reassemble the tokens into an evaluable expression
        evaluated_expr = " ".join(tokens)
        evaluated_expr = evaluated_expr.replace(" = = ", " == ").replace("! = ", " != ")
        try:
            result = eval(evaluated_expr)
        except Exception as e:
            print(f"Error evaluating expression '{evaluated_expr}': {e}")
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
