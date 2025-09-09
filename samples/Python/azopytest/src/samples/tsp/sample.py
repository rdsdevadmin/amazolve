import os
import numpy
import random
import json
from common import csvtable
from azo import atoms

class TspSample:

    def __init__(self, dyndata_path: str):

        # member initialization
        self.dyndata_path = dyndata_path
        self.city_count = 100   # find shortest path among this many cities

    def create_dyndata(self):

        self.atom_def = atoms.AtomDefinition(1, self.city_count, self.city_count)
        self.atom_def.save(os.path.join(self.dyndata_path, "atoms.json"))

        # create arrays
        cost_array = self._create_cost_array()

        # save arrays
        self._save_array(cost_array, "array_cost.json")

    def _save_array(self, a, filename: str):

        with open(os.path.join(self.dyndata_path, filename), "w") as f:
            json.dump(a, f, indent=4)

    def _create_cost_array(self):

        a = numpy.zeros((self.city_count, self.city_count))

        for i in range(self.city_count):
            for j in range(self.city_count):

                trans_cost = 0.0
                if a[j][i] > 0:
                    # same cost in both directions
                    trans_cost = a[j][i]
                elif i != j:
                    # random cost (distance between cities)
                    trans_cost = random.random() 

                a[i][j] = trans_cost

        return a.tolist()
