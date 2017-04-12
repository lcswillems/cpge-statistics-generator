import os
from src.helpers import *
from src.exam.exam_report import *

class Exams:
	def load(self, year = None):
		self.reports = {}

		years = old(grids_folder) if year == None else [str(year)]

		for year in years:
			self.reports[year] = {}

			for basename in olf(opj(grids_folder, year)):
				exam, ext = os.path.splitext(basename)

				if ext == ".json":
					self.reports[year][exam] = ExamReport()\
											   .create(year, exam)

		return self

	def save(self, folder):
		for year, reports in self.reports.items():
			for exam, report in reports.items():
				report.to_file(opj(folder, year, exam + ".rep"))

		return self