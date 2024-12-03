from textx import metamodel_from_file

# Load the meta-model
finscript_mm = metamodel_from_file('FinScript.tx')

# Interpreter Class
class FinScriptInterpreter:
    def __init__(self):
        self.state = {}

    def interpret(self, model):
        for s in model.statements:
            if s.__class__.__name__ == "Output":
                print(s.content)
            elif s.__class__.__name__ == "Declaration":
                self.state[s.name] = s.value

# Test Program
finscript_model = finscript_mm.model_from_file('sandbox.fin')
interpreter = FinScriptInterpreter()
interpreter.interpret(finscript_model)
