import json, copy
from src.helpers import *
from src.structs.report import *
from src.structs.table import *

class StudentReport(Report):
	def print_error(self, exam, col, precomputed, computed):
		precomputed = clean_value(precomputed)
		computed = clean_value(computed)

		if precomputed != computed:
			print(">> Attention !")
			if self.filename != None:
				print("Fichier :", self.filename)
			print("Concours :", exam)
			print("{0} précalculé : '{1!s}'".format(col, precomputed))
			print("{0} calculé :    '{1!s}'".format(col, computed))
			print()

	def fill(self, power, year, default_exam = None):
		if default_exam == None:
			default_exam = self.get("ECRIT/0/0/Concours")
		new_report = self.new(power, year, default_exam)

		for section in self.get_sections():
			for i in range(len(self.get(opj(section, "0")).get())):
				exam = self.get(opj(section, "0", str(i), "Concours"))
				if exam != default_exam:
					new_report.set(
						self.new(power, year, exam).get(opj(section, "0", exam)),
						opj(section, "0", "-1")
					)

		self.report = new_report.get()

		return self

	def new(self, power, year, exam):
		grid = load_grid(year, exam)
		new_report = Report()

		coeff_sum_global = 0
		points_sum_global = 0
		
		for section in self.get_sections():
			coeff_sum = 0
			points_sums = OrderedDict()
			for key in (grid[section]["barres"].keys() if "barres" in grid[section] else ["*"]):
				points_sums[key] = 0

			new_table2 = Table()

			for test, details in grid[section]["epreuves"].items():
				spec = details["spec"] if "spec" in list(details.keys()) else None
				test_section = "ECRIT" if spec == "reprise" else section
				line = self.get(opj(test_section, "1", test))

				if line != None:
					new_line = copy.copy(line)

					if spec == "option":
						new_line["Epreuve"] += " (O)"
					elif spec == "reprise":
						new_line["Epreuve"] += " (R)"
					elif spec == "ecrit":
						new_line["Epreuve"] += " (E)"

					new_line["Coeff"] = details["coeff"]
					mark = 0 if line["Note"] == "Absent" else line["Note"]
					mark = max(mark - 10, 0) if spec == "option" else mark
					new_line["Points"] = details["coeff"] * mark

					coeff_sum += 0 if spec == "option" else details["coeff"]
					for key, points_sum in points_sums.items():
						if key == "*" or line["Epreuve"] in grid[section]["barres"][key]["epreuves"]:
							points_sums[key] += new_line["Points"]

					new_table2.set(new_line, -1)

			bonus_line = OrderedDict()
			bonus_line["Epreuve"] = "Bonus " + power
			bonus_line["Note"] = ""
			bonus_line["Coeff"] = ""
			bonus_line["Points"] = grid[section]["bonification"][power]

			points_sums["*"] += grid[section]["bonification"][power]

			new_table2.set(bonus_line, -1)

			new_table1 = Table()

			exam_line = self.get(opj(section, "0", exam))
			if exam_line == None:
				exam_line = OrderedDict()
				exam_line["Concours"] = exam

			for key, points_sum in points_sums.items():
				total_name = "Tot." + ("" if key == "*" else " " + key) + " " + section.lower()

				if total_name in list(exam_line.keys()):
					self.print_error(exam, total_name, exam_line[total_name], points_sum)

				exam_line[total_name] = points_sum
			exam_line["Moy. " + section.lower()] = points_sums["*"] / coeff_sum

			new_table1.set(exam_line, -1)

			new_report.set([new_table1, new_table2], section)

			coeff_sum_global += coeff_sum if section in grid["TOTAL"] else 0
			points_sum_global += points_sums["*"] if section in grid["TOTAL"] else 0

		for section in self.get_sections():
			new_report.set(
				new_report.get(opj(section, "0/0/Tot. " + section.lower())) / points_sum_global * 100,
				opj(section, "0/0/% total")
			)

			if section == "ECRIT":
				if "barres" in grid[section].keys():
					is_eligible = True

					for key, details in grid[section]["barres"].items():
						key_name = "" if key == "*" else " " + key
						total_name = "Tot." + key_name + " " + section.lower()
						new_report.set(details["points"], opj(section, "0/0", "Barre" + key_name))

						if new_report.get(opj(section, "0/0", total_name)) < details["points"]:
							is_eligible = False

					if not(is_eligible):
						result = "Refusé"
					elif not("ORAL" in self.get_sections()):
						result = "Démission"
					else:
						result = "Admissible"

					new_report.set(result, opj(section, "0/0/Resultat"))

			if section == "ORAL":
				if "Tot." in new_report.get(opj(section, "0/0")).keys():
					self.print_error(exam, "Tot.", new_report.get(opj(section, "0/0/Tot.")), points_sum_global)
				new_report.set(points_sum_global, opj(section, "0/0/Tot."))
				new_report.set(points_sum_global / coeff_sum_global, opj(section, "0/0/Moy."))

			for new_line_id, new_line in enumerate(new_report.get(opj(section, "1")).get()):
				new_report.set(
					new_line["Points"] / new_report.get(opj(section, "0/0", "Tot. " + section.lower())) * 100,
					opj(section, "1", str(new_line_id), "% " + section.lower())
				)
				new_report.set(
					new_line["Points"] / points_sum_global * 100,
					opj(section, "1", str(new_line_id), "% total")
				)

		return new_report