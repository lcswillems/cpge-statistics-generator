import os
from src.helpers import *
from src.student.student_report import *

class Student:
	def load(self, folder):
		self.reports = {}

		years = old(folder)

		for i, year in enumerate(years):
			power = ["3/2", "5/2", "7/2"][i]
			self.reports[power] = {}

			for basename in olf(opj(folder, year)):
				school, ext = os.path.splitext(basename)

				if ext == ".rep":
					report = StudentReport()\
							 .from_file(opj(folder, year, basename))\
							 .fill(power, int(year))
					self.reports[power][school] = report

		return self

	def save(self, folder):
		for power, reports in self.reports.items():
			fpower = power.replace("/", " ")
			for school, report in reports.items():
				report.to_file(opj(folder, fpower, school + ".rep"))

		return self

	def get(self, path = ""):
		value = self.reports
		segs = ops(path)

		if len(segs) > 0:
			segs[0] = int(segs[0]) + 1

			if len(self.reports) >= segs[0]:
				power = list(sorted(self.reports.keys()))[-segs[0]]
				value = self.reports[power]

				if len(segs) > 1:
					found = False
					for school, report in self.reports[power].items():
						if school == segs[1]:
							value = report
							found = True

							if len(segs) > 2:
								value = value.get(opj(*segs[2:]))
					if not(found):
						value = None
			else:
				value = None

		return value