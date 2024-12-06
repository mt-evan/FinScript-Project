from textx import metamodel_from_file
import re
import sys

# Load the meta-model
finscript_mm = metamodel_from_file('FinScript.tx')

# Preprocess the file to handle commas
# May need to update if I implement methods
# because commas are used to separate arguments
def preprocess_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    content = re.sub(r'(?<=\d),(?=\d)', '', content)  # Remove commas surrounded by numbers
    with open(file_path, 'w') as file:
        file.write(content)

class FinScriptInterpreter:
    def __init__(self):
        self.state = {}

    # In state, store the value for currencies as Currency objects
    # update parser so that it sees any 100USD and changes it to a Currency object and can do math with Currency objects by accessing it's amount field
    def math_parser(self, expr):

        # Remove commas
        expr = expr.replace(",", "")

        # Replace logical operators and boolean values
        expr = expr.replace("||", " or ")
        expr = expr.replace("&&", " and ")
        expr = re.sub(r'(?<!\!)\!', ' not ', expr)
        expr = expr.replace("true", "True").replace("false", "False")
        # change a 'not=' to !=
        expr = expr.replace("not =", "!=")

        # Update the regular expression to correctly identify tokens
        tokens = re.findall(r'\d+(?:\.\d+)?(?:USD|EUR|GBP|JPY)|==|!=|<=|>=|[+\-*/%()=<>&!|]|-?\d+\.\d+|-?\d+|[a-zA-Z_][a-zA-Z0-9_]*', expr)

        # print(tokens)

        for i, token in enumerate(tokens):
            # If the token is a currency literal
            if re.match(r'^\d+(?:\.\d+)?(USD|EUR|GBP|JPY)$', token):
                match = re.match(r'^(\d+(?:\.\d+)?)(USD|EUR|GBP|JPY)$', token)
                amount, currency = match.groups()
                amount = float(amount)
                tokens[i] = f"Currency({amount}, '{currency}')"
            # If the token is a negative currency literal
            elif re.match(r'^-\d+(?:\.\d+)?(USD|EUR|GBP|JPY)$', token):
                match = re.match(r'^-(\d+(?:\.\d+)?)(USD|EUR|GBP|JPY)$', token)
                amount, currency = match.groups()
                amount = -float(amount)
                tokens[i] = f"Currency({amount}, '{currency}')"
            # If the token is a known variable in the state
            elif token in self.state:
                tokens[i] = f"self.state['{token}']"
            # Handle undefined variables
            elif re.match(r'[a-zA-Z_][a-zA-Z0-9_]*', token) and token not in ['and', 'or', 'not', 'True', 'False']:
                raise ValueError(f"Variable '{token}' not defined.")

        # Reassemble the tokens into a single expression with spaces
        expr = " ".join(tokens)

        # print(expr)

        # Prepare the context for eval
        context = {
            "Currency": Currency,  # Make the Currency class accessible
            "self": self  # Include self to access self.state
        }

        try:
            result = eval(expr, {}, context)
        except Exception as e:
            raise ValueError(f"Error evaluating expression '{expr}': {e}")

        # print(f"Result: {result}")
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

class Currency:
    # Exchange rates relative to USD (can be updated dynamically)
    exchange_rates = {
        'USD': 1.0,
        'EUR': 0.85,
        'GBP': 0.75,
        'JPY': 110.0
    }

    def __init__(self, amount, currency):
        if currency not in self.exchange_rates:
            raise ValueError(f"Unsupported currency: {currency}")
        self.amount = amount
        self.currency = currency

    def to_base(self):
        """Convert to base currency (USD)."""
        return self.amount / self.exchange_rates[self.currency]

    def convert_to(self, target_currency):
        """Convert this currency to another."""
        if target_currency not in self.exchange_rates:
            raise ValueError(f"Unsupported currency: {target_currency}")
        base_amount = self.to_base()
        return Currency(base_amount * self.exchange_rates[target_currency], target_currency)

    def __add__(self, other):
        if isinstance(other, (int, float)):  # If other is a number
            return Currency(self.amount + other, self.currency)
        if isinstance(other, Currency):  # If other is another Currency
            other_converted = other.convert_to(self.currency)
            return Currency(self.amount + other_converted.amount, self.currency)
        raise TypeError(f"Cannot add {type(other)} to Currency")

    def __radd__(self, other):
        return self.__add__(other)  # Reuse the __add__ method for reversed addition

    def __sub__(self, other):
        if isinstance(other, (int, float)):  # If other is a number
            return Currency(self.amount - other, self.currency)
        if isinstance(other, Currency):
            other_converted = other.convert_to(self.currency)
            return Currency(self.amount - other_converted.amount, self.currency)
        raise TypeError(f"Cannot subtract {type(other)} from Currency")

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            return Currency(other - self.amount, self.currency)
        raise TypeError(f"Cannot subtract Currency from {type(other)}")

    def __mul__(self, other):
        if isinstance(other, (int, float)):  # If other is a number
            return Currency(self.amount * other, self.currency)
        raise TypeError(f"Cannot multiply {type(other)} with Currency")

    def __rmul__(self, other):
        return self.__mul__(other)  # Reuse the __mul__ method for reversed multiplication

    def __truediv__(self, other):
        if isinstance(other, (int, float)):  # If other is a number
            return Currency(self.amount / other, self.currency)
        raise TypeError(f"Cannot divide something by {type(other)}")

    def __rtruediv__(self, other):
        raise TypeError("Cannot divide something by Currency")

    def __neg__(self):
        """Unary negation."""
        return Currency(-self.amount, self.currency)

    def __eq__(self, other):
        if isinstance(other, Currency):
            return self.to_base() == other.to_base()
        elif isinstance(other, (int, float)):
            return self.amount == other
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if isinstance(other, Currency):
            return self.to_base() < other.to_base()
        elif isinstance(other, (int, float)):
            return self.amount < other
        raise TypeError(f"Cannot compare {type(other)} with Currency")

    def __le__(self, other):
        if isinstance(other, Currency):
            return self.to_base() <= other.to_base()
        elif isinstance(other, (int, float)):
            return self.amount <= other
        raise TypeError(f"Cannot compare {type(other)} with Currency")

    def __gt__(self, other):
        if isinstance(other, Currency):
            return self.to_base() > other.to_base()
        elif isinstance(other, (int, float)):
            return self.amount > other
        raise TypeError(f"Cannot compare {type(other)} with Currency")

    def __ge__(self, other):
        if isinstance(other, Currency):
            return self.to_base() >= other.to_base()
        elif isinstance(other, (int, float)):
            return self.amount >= other
        raise TypeError(f"Cannot compare {type(other)} with Currency")

    def __str__(self):
        return f"{self.amount:,.4f}{self.currency}"


    def __repr__(self):
        return str(self)



# Test Program
#file_path = "sandbox.fin"
file_path = "Program1.fin"
preprocess_file(file_path)
finscript_model = finscript_mm.model_from_file(file_path)
interpreter = FinScriptInterpreter()
interpreter.interpret(finscript_model)



