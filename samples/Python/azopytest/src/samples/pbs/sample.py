import os
import numpy
import json
from common import csvtable
from azo import atoms

class PbsTreeNode:

    def __init__(self):

        self.partID = 0;
        self.level = 0;
        self.children = []

class PbsTree:

    def __init__(self):
        self.root = PbsTreeNode()
        self.levels = 0

    def init_from_table(self, pbs_table: csvtable.CsvTable):
        self.root.partID = 1
        self.root.level = 0
        self._recurse_get_children(pbs_table, self.root)

    def recurse_print_result(self, result, node: PbsTreeNode):

        for i in range(node.level):
            print("  ", end="")

        print(f"P{node.partID}: (S{result.atoms[node.partID - 1] + 1})")
        for child in node.children:
            self.recurse_print_result(result, child)

    def _recurse_get_children(self, pbs_table: csvtable.CsvTable, parent: PbsTreeNode):

        # record level
        if parent.level + 1 > self.levels:
            self.levels = parent.level + 1

        # recurse through children
        for row in pbs_table.rows:
            if row[0] == "sib":
                continue
            if int(row[2]) == parent.partID:
                
                child = PbsTreeNode()
                child.partID = int(row[1])
                child.level = parent.level + 1
                parent.children.append(child)

        for child in parent.children:
            self._recurse_get_children(pbs_table, child)


class PbsSample:

    def __init__(self, db_path: str, dyndata_path: str):

        # member initialization
        self.db_path = db_path
        self.dyndata_path = dyndata_path
        self.pbs_tree = PbsTree()

    def create_dyndata(self):

        self._load_tables()

        self.pbs_tree.init_from_table(self.pbs_table)

        self.atom_def = atoms.AtomDefinition(self.get_part_count(), 1, self.get_site_count())
        self.atom_def.save(self.dyndata_path + "atoms.json")

        # create arrays
        cost_array = self._create_cost_array()
        children_array = self._create_children_array()
        siblings_array = self._create_siblings_array()

        # save arrays
        self._save_array(cost_array, "array_cost.json")
        self._save_array(children_array, "array_children.json")
        self._save_array(siblings_array, "array_siblings.json")

    def _save_array(self, a, filename: str):

        with open(os.path.join(self.dyndata_path, filename), "w") as f:
            json.dump(a, f, indent=4)

    def _load_tables(self):

        # load costs table
        self.costs_table = csvtable.CsvTable(self.db_path  + "costs.csv", True)

        # load pbs table
        self.pbs_table = csvtable.CsvTable(self.db_path  + "pbs.csv", True)


    def get_part_count(self):
        maxv = 0
        minv = 0
        first = True
        for row in self.pbs_table.rows:
            p1 = int(row[1])
            p2 = int(row[2])
            if first:
                maxv = max(p1, p2)
                minv = min(p1, p2)
                first = False
            else:
                if max(p1, p2) > maxv:
                    maxv = max(p1, p2)
                if min(p1, p2) < minv:
                    minv = min(p1, p2)

        return 1 + (maxv - minv)

    def get_site_count(self):
        maxv = 0
        minv = 0
        first = True
        for row in self.costs_table.rows:
            s1 = int(row[1])
            s2 = int(row[2])
            if first:
                maxv = max(s1, s2)
                minv = min(s1, s2)
                first = False
            else:
                if max(s1, s2) > maxv:
                    maxv = max(s1, s2)
                if min(s1, s2) < minv:
                    minv = min(s1, s2)

        return 1 + (maxv - minv)

    def get_child_relation_count(self):

        count = 0
        for row in self.pbs_table.rows:
            if row[0] == "sub":
                count += 1
        return count

    def get_sibling_relation_count(self):

        count = 0
        for row in self.pbs_table.rows:
            if row[0] == "sib":
                count += 1
        return count

    def _create_cost_array(self):

        a = numpy.zeros((self.atom_def.resource_count, self.atom_def.state_count, self.atom_def.state_count))

        for row in self.costs_table.rows:

            # get columns in csv order
            r = int(row[0]) - 1
            s1 = int(row[1]) - 1
            s2 = int(row[2]) - 1
            cost = float(row[3])

            # set columns in array order
            a[r][s1][s2] = cost
            a[r][s2][s1] = cost

        return a.tolist()

    def _create_children_array(self):

        a = numpy.zeros((self.get_child_relation_count(), 2))

        irow = 0
        for row in self.pbs_table.rows:

            if row[0] == "sib":
                continue

            # child in first column
            a[irow][0] = int(row[1]) - 1
            # parent in second column
            a[irow][1] = int(row[2]) - 1

            irow += 1

        return a.tolist()

    def _create_siblings_array(self):

        a = numpy.zeros((self.get_sibling_relation_count(), 2))

        irow = 0
        for row in self.pbs_table.rows:

            if row[0] == "sub":
                continue

            # brother in first column
            a[irow][0] = int(row[1]) - 1
            # sister in second column
            a[irow][1] = int(row[2]) - 1

            irow += 1

        return a.tolist()
