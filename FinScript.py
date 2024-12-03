from textx import metamodel_from_file
import sys

# Load the meta-model
finscript_mm = metamodel_from_file('FinScript.tx')

# Interpreter Class
class FinScriptInterpreter:
    def __init__(self):
        self.state = {}
        self.keywords = ['let', 'print', 'calculate', 'if', 'then', 'endif', 'True', 'False']

    def interpret(self, model):
        for s in model.statements:
            # Output
            if s.__class__.__name__ == "OutputVar":
                if s.content in self.state:
                    print(self.state[s.content])
                else:
                    print("Variable not found: " + s.content)
                    break
            elif s.__class__.__name__ == "OutputValue":
                print(s.content)

            # Declaration
            elif s.__class__.__name__ == "DeclarationValue":
                self.state[s.name] = s.value
            elif s.__class__.__name__ == "DeclarationVar":
                if s.value in self.state: # Check if RHS variable is in state
                    self.state[s.name] = self.state[s.value]
                else:
                    # Check if it is "True" or "False"
                    if s.value == "True":
                            self.state[s.name] = True
                    elif s.value == "False":
                            self.state[s.name] = False
                    else:
                        print(f"Variable not found: {s.value}")
                        break

            # Reassignment
            elif s.__class__.__name__ == "ReassignmentVar":
                self.state[s.name] = s.value
                if s.value in self.state: # Check if RHS variable is in state
                    self.state[s.name] = self.state[s.value]
                else:
                    # Check if it is "True" or "False"
                    if s.value == "True":
                            self.state[s.name] = True
                    elif s.value == "False":
                            self.state[s.name] = False
                    else:
                        print(f"Variable not found: {s.value}")
                        break
            elif s.__class__.__name__ == "ReassignmentValue":
                self.state[s.name] = s.value

# Test Program
finscript_model = finscript_mm.model_from_file('sandbox.fin')
interpreter = FinScriptInterpreter()
interpreter.interpret(finscript_model)
