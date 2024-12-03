from textx import metamodel_from_file

def move_command_processor(move_cmd):
  # If steps is not given, set it to default 1 value.
  if move_cmd.steps == 0:
    move_cmd.steps = 1

class Robot:
    origin_x = 0
    origin_y = 0
    def __init__(self):
        # Initial position is (0,0)
        self.x = 0
        self.y = 0

    def __str__(self):
        return f"Robot position is {self.x}, {self.y}."

    def interpret(self, model):

        # model is an instance of Program
        for c in model.commands:

            if c.__class__.__name__ == "InitialCommand":
                print(f"Setting position to: {c.x}, {c.y}")
                self.x = c.x
                self.y = c.y
                origin_x = self.x
                origin_y = self.y
            elif c == "spin":
                print("Spinning the robot, \"WEEEEEEE!\"")
            elif c == "origin":
                print(f"Setting position to starting position: {origin_x}, {origin_y}")
                self.x = origin_x
                self.y = origin_y
            else:
                print(f"Going {c.direction} for {c.steps} step(s).")

                move = {
                    "up": (0, 1),
                    "down": (0, -1),
                    "left": (-1, 0),
                    "right": (1, 0),
                    "upleft": (-1, 1),
                    "upright": (1, 1),
                    "downleft": (-1, -1),
                    "downright": (1, -1),
                    "spin": (0, 0)
                }[c.direction]

                # Calculate new robot position
                self.x += c.steps * move[0]
                self.y += c.steps * move[1]

            print(self)

robot_mm = metamodel_from_file('robot.tx')
robot_mm.register_obj_processors({'MoveCommand': move_command_processor})

# robot_model = robot_mm.model_from_file('program.rbt')
# #robot_model = robot_mm.model_from_file('program2.rbt')
robot_model = robot_mm.model_from_file('program3.rbt')
#robot_model = robot_mm.model_from_file('program4.rbt')
#robot_model = robot_mm.model_from_file('program5.rbt')

robot = Robot()
robot.interpret(robot_model)