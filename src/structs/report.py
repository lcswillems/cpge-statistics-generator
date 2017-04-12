from collections import OrderedDict
import os, copy
from src.helpers import *
from src.structs.table import *

# This function adds "nb_tabs" indentations to "txt" text.
#
# Example:
#   - "line1
#      line2
#      line3"
#     -->
#     "     line1
#           line2
#           line3"
def indent(txt, nb_tabs):
	return "\n".join([nb_tabs * tab_size * " " + line for line in txt.split("\n")])

# This class handles txt reports: loading from txt / file, exporting to txt / file,
# getting and setting values...
class Report:
	def __init__(self):
		self.report = OrderedDict()
		self.filename = None

	# This method converts a txt report to a structured report.
	#
	# Example:
	#   - "section1
	#         
	#           col1    col2    ...     colM
	#           val11   val12   ...     val1M
	#           val21   val21   ...     val2M
	#           .............................
	#           valN1   valN2   ...     valNM
	#
	#      ...
	#
	#      sectionP
	#
	#           col1    col2    ...     colM
	#           val11   val12   ...     val1M
	#           val21   val21   ...     val2M
	#           .............................
	#           valN1   valN2   ...     valNM"
	#     -->
	#     { "section1": table1 object, ..., "sectionP": tableP object }
	#     where "table1" and "table2" are structured tables
	def from_txt(self, txt_report):
		txt_report = txt_report.replace("\t", " " * tab_size)
		txt_report = txt_report[1:] if txt_report[0] == "\ufeff" else txt_report
		txt_report = "\n".join([line.strip(" ") for line in txt_report.split("\n")])
		big_blocks = [big_block.strip("\n ").split("\n\n") for big_block in txt_report.strip("\n ").split("\n\n\n")]

		self.report = OrderedDict()

		for big_block in big_blocks:
			self.report[big_block[0]] = [
				Table().from_txt(txt_table)
				for txt_table in big_block[1:]
			]

		return self

	# This method converts the content of the "filename" file to
	# a structured report.
	def from_file(self, filename):
		self.filename = filename
		with open(filename) as file:
			return self.from_txt(file.read())

	# This method converts the structured report to a txt report.
	# It is the reverse method of "from_txt".
	def to_txt(self):
		return "\n\n\n".join([
			"\n\n".join([section] + [
				indent(table.to_txt(), 1)
				for table in tables
			])
			for section, tables in self.report.items()
		])

	# This method converts the structured report to a txt report
	# and write it in the "filename" file.
	def to_file(self, filename):
		os.makedirs(os.path.dirname(filename), exist_ok = True)
		with open(filename, "w") as file:
			file.write(self.to_txt())

		return self

	# This method extracts the data corresponding to the "path" path.
	# If the path doesn't exist, None is returned. The path can have:
	#   - 0 segment (no "path" parameter)
	#   -> returns the report content
	#   - 1 segment: the section
	#   -> returns the tables in this section
	#   - 2 segments: the section / the table number (starting at 0)
	#   -> returns the corresponding table
	#   - > 2 segments: the section / the table number / the path in the table
	#   -> returns the data corresponding to the path in the corresponding table
	#
	# Example:
	#   - "ECRIT/0" --> table object
	#   - "ECRIT/1/Mathematiques 1" --> { "Epreuve": "Mathematiques 1", "Note": 12.5 }
	#   - "ECRIT/1/0/Note" --> 12.5
	def get(self, path = ""):
		value = self.report
		segs = ops(path)

		if len(segs) > 0:
			if segs[0] in value.keys():
				value = value[segs[0]]
			else:
				return None
		if len(segs) > 1:
			segs[1] = int(segs[1])
			if segs[1] < len(value):
				value = value[segs[1]]
			else:
				return None
		if len(segs) > 2:
			value = value.get(opj(*segs[2:]))

		return copy.copy(value)

	# This method returns the list of the sections.
	def get_sections(self):
		return self.report.keys()

	# This method sets the "value" in the corresponding path. If the path
	# doesn't exist, it is created. The path can have:
	#   - 0 segment (no "path" parameter)
	#   -> sets the value of the report
	#   - 1 segment: the section
	#   -> sets the value of a section
	#   - 2 segments: the line identifier / the column name
	#   -> sets the value of the corresponding table
	#   - > 2 segments: the section / the table number / the path in the table
	#   -> sets the value corresponding to the path in the corresponding table
	def set(self, value, path = ""):
		segs = ops(path)

		if len(segs) > 0:
			if not(segs[0] in self.report.keys()):
				self.report[segs[0]] = []

			if len(segs) > 1:
				segs[1] = int(segs[1])

				if segs[1] == -1:
					self.report[segs[0]].append(Table())

				if len(segs) > 2:
					self.report[segs[0]][segs[1]] = self.report[segs[0]][segs[1]].set(value, opj(*segs[2:]))
				else:
					self.report[segs[0]][segs[1]] = value
			else:
				self.report[segs[0]] = value
		else:
			self.report = value

		return self