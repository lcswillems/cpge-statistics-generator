from collections import OrderedDict
import hashlib
from src.helpers import *
from src.student.student import *

def anonymize(name):
	return hashlib.sha256(str.encode(name)).hexdigest()

class Students:
	def load(self, folder, year, anonymize_names = False):
		names = list(filter(
			lambda name: os.path.isdir(opj(folder, name, str(year))),
			old(folder)
		))

		if anonymize_names:
			anonymized_names = sorted(list(map(anonymize, names)))
			nb_digits = len(str(1 + len(anonymized_names)))
			ids = {
				name: "Elève " + '{0:0{width}}'.format(1 + anonymized_names.index(anonymize(name)), width=nb_digits)
				for name in names
			}
		else:
			ids = {name: name for name in names}

		self.students = {}

		for name in names:
			if anonymize_names:
				with open(opj(folder, name, ".id"), "w") as file:
					file.write(ids[name])
			self.students[ids[name]] = Student().load(opj(folder, name))

		return self

	def save(self, folder):
		for id, student in self.students.items():
			student.save(opj(folder, id))

		return self

	def get_student(self, path = ""):
		if path == "":
			return self.students
		return self.students[path]


	def get_ranking(self, path = ""):
		if path == "":
			return self.rankings
		return self.rankings[path]

	def compute_rankings(self, cols):
		self.rankings = {}

		for id, student in self.students.items():
			reports = student.get("0")
			for school, report in reports.items():
				for section in report.get_sections():
					for table_id, table in enumerate(report.get(section)):
						cols_in = [col for col in cols if col in table.get_columns()]
						if len(cols_in) > 0:
							col = cols_in[0]
							for line in table.get():
								line_id = line[list(line.keys())[0]]
								if isinstance(line[col], str):
									continue

								ranking_path = opj(school, section, str(table_id), line_id)
								if not(ranking_path in self.rankings.keys()):
									self.rankings[ranking_path] = []
								self.rankings[ranking_path].append((id, line[col]))

		for ranking_path, unordered_ranking in self.rankings.items():
			ranking_helper = {}
			ranking = []

			for id, value in unordered_ranking:
				if not(value in ranking_helper.keys()):
					ranking_helper[value] = []
				ranking_helper[value].append(id)

			rank = 1

			for value in sorted(ranking_helper.keys(), reverse = True):
				ids = ranking_helper[value]
				for id in ids:
					ranking.append((id, rank))
				rank += len(ids)

			self.rankings[ranking_path] = ranking

		return self

	def add_ranks(self, col):
		for id, student in self.students.items():
			reports = student.get("0")
			for school, report in reports.items():
				for section in report.get_sections():
					for table_id, table in enumerate(report.get(section)):
						for line in table.get():
							line_id = line[list(line.keys())[0]]
							
							ranking_path = opj(school, section, str(table_id), line_id)
							if ranking_path in self.rankings.keys():
								ranking = self.rankings[ranking_path]
								rank = OrderedDict(ranking)[id]
								str_rank = "{0!s} / {1!s}".format(rank, len(ranking))
								report.set(str_rank, opj(section, str(table_id), line_id, col))

		return self

	def anonymize_general_ranks(self, col):
		for id, student in self.students.items():
			for power, reports in student.get().items():			
				for school, report in reports.items():
					for section in report.get_sections():
						for table_id, table in enumerate(report.get(section)):
							if col in table.get_columns():
								for line in table.get():
									line_id = line[list(line.keys())[0]]

									rank = report.get(opj(section, str(table_id), line_id, col))
									anonymized_rank = clean_value(rank)
									anonymized_rank = anonymized_rank[:-1] + "?"
									report.set(anonymized_rank, opj(section, str(table_id), line_id, col))

		return self