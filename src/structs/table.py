from collections import OrderedDict
import re, copy
from src.helpers import *

# This function splits, into a Python array, the "line" parameter
# every time more than "tab_size" spaces are encountered.
# If it is possible, the array values are converted to float values.
#
# Example:
#   - "           val1        12         val2  " --> ["val1", 12, "val2"]
#   - "     val1    " --> "val1"
def tab_split(line):
	line = line.strip("\n ")

	tmp_line = ""
	spaces_range = [0, 0]

	for i in range(len(line)):
		if line[i] == " ":
			if i == spaces_range[1]:
				spaces_range[1] += 1
			else:
				spaces_range[0] = i
				spaces_range[1] = i + 1
		else:
			if i == spaces_range[1]:
				nb_spaces = spaces_range[1] - spaces_range[0]
				tmp_line += ("#" if nb_spaces >= tab_size else " " * nb_spaces)
			tmp_line += line[i]

	splited_line = list(map(
		lambda item: float(item) if re.match("^\d+(\.\d+)?$", item) else item,
		tmp_line.split("#")
	))

	return splited_line

# This class handles txt tables: loading from txt / file, exporting to txt / file,
# getting and setting values...
class Table:
	def __init__(self):
		self.table = []
		self.filename = None

	# This method converts a txt table to a structured table.
	#
	# Example:
	#   - "col1     col2     ...    colK
	#      val11    val12    ...    val1K
	#      ...
	#      valN1    valN2    ...    valNK"
	#     --> (1st step)
	#     [["col1",  "col2",  ..., "colK"],
	#      ["val11", "val12", ..., "val1K"],
	#      ...
	#      ["valN1", "valN2", ..., "valNK"]]
	#     --> (2nd step)
	#     [{"col1": "val1", ..., "colK": "val1K"},
	#      ...
	#      {"col1": "valN1", ..., "colK": "valNK"}]
	def from_txt(self, txt_table):
		# 1st step
		inter_table = [tab_split(line) for line in txt_table.strip("\n ").split("\n")]

		# 2nd step
		self.table = []

		for inter_line in inter_table[1:]:
			line = OrderedDict()
			for i in range(len(inter_table[0])):
				line[inter_table[0][i]] = inter_line[i]
			self.table.append(line)

		return self

	# This method converts the content of the "filename" file to
	# a structured table.
	def from_file(self, filename):
		self.filename = filename
		with open(filename) as file:
			return self.from_txt(file.read())

	# This method converts the structured table to a txt table,
	# with respect for column alignment.
	# It is the reverse method of "from_txt".
	def to_txt(self):
		# 1st step
		cols = merge_lists([line.keys() for line in self.table])
		inter_table = [cols] + [list(expand_dict(line, cols).values()) for line in self.table]

		# 2nd step
		for line_id in range(len(inter_table)):
			for i in range(len(inter_table[line_id])):
				inter_table[line_id][i] = clean_value(inter_table[line_id][i])

		lengths = [
			tab_size * (max([len(str(line[i])) for line in inter_table]) // tab_size + 2)
			for i in range(len(inter_table[0]))
		]

		txt_lines = []
		for line in inter_table:
			txt_line = ""
			for i in range(len(line)):
				txt_line += line[i] + " "*(lengths[i]-len(line[i]))
			txt_lines.append(txt_line.strip())

		return "\n".join(txt_lines)

	# This method converts the structured table to a txt table
	# and write it in the "filename" file.
	def to_file(self, filename):
		os.makedirs(os.path.dirname(filename), exist_ok = True)
		with open(filename, "w") as file:
			file.write(self.to_txt())

		return self

	# This method extracts the data corresponding to the "path" path.
	# If the path doesn't exist, None is returned. The path can have:
	#   - 0 segment (no "path" parameter)
	#   -> returns the table content
	#   - 1 segment: the line identifier which can be:
	#       - a number: the line number (starting at 0)
	#       - a name: the first-column value of the line
	#   -> returns the line corresponding
	#   - 2 segments: the line identifier / the column name
	#   -> returns the cell value corresponding
	# 
	# Example:
	#   - "0" --> { "Epreuve": "Mathematiques 1", "Note": 12.5 }
	#   - "Mathematiques 1" --> { "Epreuve": "Mathematiques 1", "Note": 12.5 }
	#   - "0/Note" --> 12.5
	def get(self, path = ""):
		value = self.table
		segs = ops(path)

		if len(segs) > 0:
			if re.match("^-?\d+$", segs[0]):
				segs[0] = int(segs[0])
				if segs[0] < len(value):
					value = value[segs[0]]
				else:
					return None
			else:
				found = False
				for line in value:
					if line[list(line.keys())[0]] == segs[0]:
						value = line
						found = True
						break
				if not(found):
					return None
		if len(segs) > 1:
			if segs[1] in value.keys():
				value = value[segs[1]]
			else:
				return None

		return copy.copy(value)

	# This method returns the list of the column names.
	def get_columns(self):
		return self.table[0].keys()

	# This method sets the "value" in the corresponding path. If the path
	# doesn't exist, it is created. The path can have:
	#   - 0 segment (no "path" parameter)
	#   -> sets the value of the table
	#   - 1 segment: the line identifier which can be a number or a name.
	#                If it is "-1", the value is inserted in a new line.
	#   -> sets the value of a line
	#   - 2 segments: the line identifier / the column name
	#   -> sets the value of the corresponding cell
	def set(self, value, path = ""):
		segs = ops(path)

		if len(segs) > 0:
			if re.match("^-?\d+$", segs[0]):
				segs[0] = int(segs[0])
			else:
				found = False
				for line_id, line in enumerate(self.table):
					if line[list(line.keys())[0]] == segs[0]:
						segs[0] = line_id
						found = True
						break
				if not(found):
					segs[0] = -1

			if segs[0] == -1:
				self.table.append({})

			if len(segs) > 1:
				if segs[1] in self.table[segs[0]].keys():
					del self.table[segs[0]][segs[1]]
				self.table[segs[0]][segs[1]] = value
			else:
				self.table[segs[0]] = value
		else:
			self.table = value

		return self