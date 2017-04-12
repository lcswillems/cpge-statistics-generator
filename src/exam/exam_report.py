from src.helpers import *
from src.structs.report import *
from src.structs.table import *

class ExamReport(Report):
	def create(self, year, exam):
		grid = load_grid(year, exam)

		coeff_sum_global = 0
		
		for section in ["ECRIT", "ORAL"]:
			coeff_sums = OrderedDict()
			coeff_sums["*"] = 0

			grps = []

			table2 = Table()

			for test, details in grid[section]["epreuves"].items():
				spec = details["spec"] if "spec" in list(details.keys()) else None
				grp = details["grp"] if "grp" in list(details.keys()) else None
				cat = details["cat"] if "cat" in list(details.keys()) else None

				if not(grp in grps):
					line = OrderedDict()

					if grp != None:
						grps.append(grp)
						line["Epreuve"] = grp
					else:
						line["Epreuve"] = test

					if spec == "option":
						line["Epreuve"] += " (O)"
					elif spec == "reprise":
						line["Epreuve"] += " (R)"
					elif spec == "ecrit":
						line["Epreuve"] += " (E)"

					line["Coeff"] = details["coeff"]
					mark = 10 if spec == "option" else 20
					line["Points"] = details["coeff"] * mark

					if spec != "option":
						coeff_sums["*"] += details["coeff"]
						if cat != None:
							if not(cat in coeff_sums.keys()):
								coeff_sums[cat] = 0
							coeff_sums[cat] += details["coeff"]

					table2.set(line, -1)

			for power, points in grid[section]["bonification"].items():
				bonus_line = OrderedDict()
				bonus_line["Epreuve"] = "Bonus " + power
				bonus_line["Coeff"] = ""
				bonus_line["Points"] = points
				table2.set(bonus_line, -1)

			table1 = Table()

			line = OrderedDict()
			line["Concours"] = exam
			for key, coeff_sum in reversed(coeff_sums.items()):
				coeff_name = "Coeffs" + ("" if key == "*" else " " + key) + " " + section.lower()
				line[coeff_name] = coeff_sum
				if key != "*":
					line["% " + section.lower()] = coeff_sum / coeff_sums["*"] * 100

			table1.set(line, -1)

			self.set([table1, table2], section)

			coeff_sum_global += coeff_sums["*"] if section in grid["TOTAL"] else 0

		for section in ["ECRIT", "ORAL"]:
			coeff_section = self.get(opj(section, "0", "0", "Coeffs " + section.lower()))

			self.set(
				coeff_section / coeff_sum_global * 100,
				opj(section, "0", "0", "% total")
			)

			if section == "ECRIT":
				if "barres" in grid[section].keys():
					for key, details in grid[section]["barres"].items():
						key_name = "" if key == "*" else " " + key
						barre_points = details["points"]
						if key == "*":
							total_points = coeff_section * 20
						else:
							total_points = sum([
								grid[section]["epreuves"][test]["coeff"] * 20
								for test in grid[section]["barres"][key]["epreuves"]
							])

						self.set(
							clean_value(barre_points) + " (" + clean_value(barre_points / total_points * 20) + ")",
							opj(section, "0/0", "Barre" + key_name + " (moy.)")
						)

			if section == "ORAL":
				self.set(coeff_sum_global, opj(section, "0/0/Coeffs total"))

			for line_id, line in enumerate(self.get(opj(section, "1")).get()):
				self.set(
					line["Points"] / (coeff_section * 20) * 100,
					opj(section, "1", str(line_id), "% " + section.lower())
				)
				self.set(
					line["Points"] / (coeff_sum_global * 20) * 100,
					opj(section, "1", str(line_id), "% total")
				)

		return self