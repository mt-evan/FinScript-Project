from textx import metamodel_from_file
import re
import sys

# Load the meta-model
finscript_mm = metamodel_from_file('FinScript.tx')

class FinScriptInterpreter:
    def __init__(self):
        self.state = {}

    def math_parser(self, expr):
        # Replace logical operators and boolean values
        expr = expr.replace("||", " or ")
        expr = expr.replace("&&", " and ")
        expr = re.sub(r'(?<!!=)!', ' not ', expr) # Replace standalone '!' with ' not '
        expr = expr.replace("true", "True").replace("false", "False")

        # Tokenize the expression while keeping multi-character operators intact
        tokens = re.findall(r'\d+\.\d+|\d+|[a-zA-Z_][a-zA-Z0-9_]*|==|!=|<=|>=|[+\-*/%()=<>&!|]', expr)

        # Replace variables with their values from the state
        for i, token in enumerate(tokens):
            if token in self.state:
                tokens[i] = str(self.state[token])
            elif re.match(r'[a-zA-Z_][a-zA0-9_]*', token) and token not in ['and', 'or', 'not', 'True', 'False']:  # If it's a variable not in state and not a keyword like "and" or "or"
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
            result = None  # Initialize the result to track control flow statements

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
                    result = self.interpret(s.thenBody)
                else:
                    executed_elif = False
                    for elif_clause in s.elifClauses:
                        elif_condition_result = self.math_parser(str(elif_clause.condition))
                        if elif_condition_result:
                            result = self.interpret(elif_clause.body)
                            executed_elif = True
                            break
                    if not executed_elif and s.elseBody:
                        result = self.interpret(s.elseBody)
                        
                # Handle results from nested statements
                if result == "break" or result == "continue":
                    return result

            # For Loop
            elif s.__class__.__name__ == "ForLoop":
                start = self.math_parser(str(s.start))
                end = self.math_parser(str(s.end))
                if s.var in self.state:
                    print(f"Variable '{s.var}' already declared")
                    sys.exit(1)
                for i in range(start, end + 1):
                    self.state[s.var] = i
                    should_break = False
                    should_continue = False
                    for statement in s.body:
                        if isinstance(statement, str):
                            if statement == "break":
                                should_break = True
                                break
                            elif statement == "continue":
                                should_continue = True
                                break
                        result = self.interpret([statement])
                        if result == "break":
                            should_break = True
                            break
                        elif result == "continue":
                            should_continue = True
                            break
                    
                    if should_break:
                        break  # Exit the outer loop if break is encountered
                    if should_continue:
                        continue  # Skip the rest of the current iteration and continue the loop

                del self.state[s.var]  # Remove loop variable after the loop

            # While Loop
            elif s.__class__.__name__ == "WhileLoop":
                while self.math_parser(str(s.condition)):
                    should_break = False
                    should_continue = False
                    for statement in s.body:
                        if isinstance(statement, str):
                            if statement == "break":
                                should_break = True
                                break
                            elif statement == "continue":
                                should_continue = True
                                break
                        result = self.interpret([statement])
                        if result == "break":
                            should_break = True
                            break
                        elif result == "continue":
                            should_continue = True
                            break
                    
                    if should_break:
                        break  # Exit the while loop if break is encountered
                    if should_continue:
                        continue  # Skip the rest of the current iteration and continue the loop

            # Break and Continue
            if isinstance(s, str):
                if s == "break":
                    return "break"
                elif s == "continue":
                    return "continue"
        
        return None  # Indicates normal execution, no special control flow actions


# Test Program
finscript_model = finscript_mm.model_from_file('sandbox.fin')
interpreter = FinScriptInterpreter()
interpreter.interpret(finscript_model)
