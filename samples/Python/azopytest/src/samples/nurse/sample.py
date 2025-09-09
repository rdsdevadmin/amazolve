import os
import numpy
import json
from common import csvtable
from azo import atoms

class NurseSample:

    def __init__(self, db_path: str, dyndata_path: str):

        # member initialization
        self.db_path = db_path
        self.dyndata_path = dyndata_path

    def create_dyndata(self):

        self._load_tables()
        self.atom_def = atoms.AtomDefinition(self.staff_table.size(), self.horizon, self.shift_table.size())
        self.atom_def.save(os.path.join(self.dyndata_path, "atoms.json"))

        # create arrays
        days_off_array = self._create_days_off_array()
        max_shifts_array = self._create_max_shifts_array()
        shift_length_array = self._create_shift_length_array()
        staff_array = self._create_staff_array()
        cover_array = self._create_cover_array()
        cover_init_array = self._create_cover_init_array()
        shift_on_req_array = self._create_shift_req_array(self.shift_on_req_table)
        shift_off_req_array = self._create_shift_req_array(self.shift_off_req_table)
        cannot_follow_array = self._create_cannot_follow_array()

        # save arrays
        self._save_array(days_off_array, "array_days_off.json")
        self._save_array(max_shifts_array, "array_max_shifts.json")
        self._save_array(shift_length_array, "array_shift_length.json")
        self._save_array(staff_array, "array_staff.json")
        self._save_array(cover_array, "array_cover.json")
        self._save_array(cover_init_array, "array_cover_init.json")
        self._save_array(shift_on_req_array, "array_shift_on_req.json")
        self._save_array(shift_off_req_array, "array_shift_off_req.json")
        self._save_array(cannot_follow_array, "array_cannot_follow.json")

    def _save_array(self, a, filename: str):

        with open(os.path.join(self.dyndata_path, filename), "w") as f:
            json.dump(a, f, indent=4)

    def _load_tables(self):

        # load horizon table
        horizon_table = csvtable.CsvTable(os.path.join(self.db_path, "horizon.csv"), True)
        self.horizon = int(horizon_table.rows[0][0])

        # load shifts table
        self.shift_table = csvtable.CsvTable(os.path.join(self.db_path, "shifts.csv"), True)
        # insert blank shift for empty shift (0 state)
        self.shift_table.insert_row([' '])
        self.shift_table.init_index()

        # load staff table
        self.staff_table = csvtable.CsvTable(os.path.join(self.db_path, "staff.csv"), True)
        self.staff_table.init_index()

        # load days off table
        self.days_off_table = csvtable.CsvTable(os.path.join(self.db_path, "days_off.csv"), True)

        # load cover table
        self.cover_table = csvtable.CsvTable(os.path.join(self.db_path, "cover.csv"), True)

        # load shift on/off requests
        self.shift_on_req_table = csvtable.CsvTable(os.path.join(self.db_path, "shift_on_requests.csv"), True)
        self.shift_off_req_table = csvtable.CsvTable(os.path.join(self.db_path, "shift_off_requests.csv"), True)

    def _create_days_off_array(self):

        a = numpy.zeros((self.atom_def.resource_count, self.atom_def.time_count))
        for row in self.days_off_table.rows:
            if len(row) < 2:
                continue
            r = self.staff_table.find(row[0]);
            for day in range(1, len(row)):
                if not row[day]:
                    continue
                a[r][int(row[day])] = 1.0

        return a.tolist()


    def _create_max_shifts_array(self):

        a = numpy.zeros((self.atom_def.resource_count, self.atom_def.state_count))
        for r in range(self.staff_table.size()):
            row = self.staff_table.rows[r]
            if len(row) < 2 or not row[1]:
                continue
            shift_maxes = row[1].split('|')
            for shift_max in shift_maxes:
                shift_max_parts = shift_max.split('=')
                if len(shift_max_parts) == 2:
                    s = self.shift_table.find(shift_max_parts[0])
                    a[r][s] = float(shift_max_parts[1])

        return a.tolist()


    def _create_shift_length_array(self):

        a = numpy.zeros(self.atom_def.state_count)
        for s in range(self.shift_table.size()):
            row = self.shift_table.rows[s]
            if len(row) < 2 or not row[1]:
                continue
            a[s] = float(row[1])

        return a.tolist()


    def _create_staff_array(self):

        a = numpy.zeros((self.atom_def.resource_count, 6))
        for r in range(self.staff_table.size()):
            row = self.staff_table.rows[r]
            if len(row) < 3 or not row[2] or not row[3]:
                continue

            # get columns in csv order
            max_minutes = float(row[2])
            min_minutes = float(row[3])
            max_cons_shifts = float(row[4])
            min_cons_shifts = float(row[5])
            min_cons_off = float(row[6])
            max_weekends = float(row[7])

            # set columns in array (different) order
            a[r][0] = min_minutes
            a[r][1] = max_minutes
            a[r][2] = min_cons_shifts
            a[r][3] = max_cons_shifts
            a[r][4] = min_cons_off
            a[r][5] = max_weekends

        return a.tolist()


    def _create_cover_array(self):

        a = numpy.zeros((self.atom_def.time_count, self.atom_def.state_count, 3))
        for i in range(self.cover_table.size()):
            row = self.cover_table.rows[i]
            if len(row) < 5:
                continue

            # get columns in csv order
            t = int(row[0])
            s = self.shift_table.find(row[1])
            req = int(row[2])
            wu = int(row[3])
            wo = int(row[4])

            # set columns in array order
            a[t][s][0] = req;
            a[t][s][1] = wu;
            a[t][s][2] = wo;

        return a.tolist()


    def _create_cover_init_array(self):

        a = numpy.zeros((self.cover_table.size(), 3))
        for i in range(self.cover_table.size()):
            row = self.cover_table.rows[i]
            if len(row) < 5:
                continue

            # get columns in csv order
            t = int(row[0])
            s = self.shift_table.find(row[1])
            req = int(row[2])

            # set columns in array order
            a[i][0] = t
            a[i][1] = s
            a[i][2] = req

        return a.tolist();

    def _create_shift_req_array(self, shift_req_table):

        a = numpy.zeros((self.atom_def.resource_count, self.atom_def.time_count, 2))
        for i in range(shift_req_table.size()):
            row = shift_req_table.rows[i]
            if len(row) != 4:
                continue

            # get columns in csv order
            r = self.staff_table.find(row[0])
            t = int(row[1])
            s = self.shift_table.find(row[2]);
            w = int(row[3])

            # set columns in array order
            a[r][t][0] = s;
            a[r][t][1] = w;

        return a.tolist()


    def _create_cannot_follow_array(self):

        a1 = []
        for row in self.shift_table.rows:
            if len(row) < 3 or not row[2]:
                continue
            s1 = self.shift_table.find(row[0])
            shifts = row[2].split("|")
            for shift in shifts:
                s2 = self.shift_table.find(shift);
                a1.append((s1, s2))

        a = numpy.zeros((self.atom_def.state_count, self.atom_def.state_count))
        for i in range(len(a1)):
            a[a1[i][0]][a1[i][1]] = 1.0

        return a.tolist()
