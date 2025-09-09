import json

class AtomDefinition:

    def __init__(self, resource_count: int, time_count: int, state_count: int):

        # member initialization
        self.resource_count = resource_count
        self.time_count = time_count
        self.state_count = state_count

    def save(self, filename: str):

        atoms = {
            "atoms": {
                "resourceCount": self.resource_count,
                "timeCount": self.time_count,
                "stateCount": self.state_count
            }
        }
        with open(filename, "w") as f:
            json.dump(atoms, f, indent=4)