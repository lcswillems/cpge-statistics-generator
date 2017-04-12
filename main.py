from collections import OrderedDict
import os
from src.exam.exams import *
from src.student.students import *

def rank_students(filename, students, school, exam, coeff):
	ranking = students.get_ranking(opj(school, "ORAL/0", exam))

	table = Table()

	for id, rank in ranking:
		student = students.get_student(id)
		report = student.get(opj("0", school))
		if report == None:
			continue

		line = OrderedDict()
		line["Rang (F)"] = rank
		line["Rang (E)"] = report.get(opj("ECRIT/0", exam, "Rang (classe)")).split("/")[0].strip()
		line["Rang (N)"] = report.get(opj("ORAL/0", exam, "Rang"))
		line["Nom"] = id
		line["Total"] = report.get(opj("ORAL/0", exam, "Tot."))
		line["Total / " + str(coeff)] = line["Total"] / coeff
		table.set(line, -1)

	with open(filename, "w") as file:
		file.write(table.to_txt())

def list_students(folder):
	baseurl = "https://www.lucaswillems.com/upload/articles/87/Students"
	html = '<meta charset="utf-8">\n<ul>'

	for id in old(folder):
		html += "<li>" + id + "<ul>"

		for fpower in old(opj(folder, id)):
			power = fpower.replace(" ", "/")
			html += "<li>" + power + " :<ul>"

			schools_exts = OrderedDict()

			for basename in olf(opj(folder, id, fpower)):
				school, ext = os.path.splitext(basename)
				if not(school in schools_exts.keys()):
					schools_exts[school] = []
				schools_exts[school].append(ext)

			for school, exts in schools_exts.items():
				html += "<li>" + school + " : "
				html += ", ".join([
					'<a href="' + opj(baseurl, id, fpower, school + ext) + '">' + ext[1:] + "</a>"
					for ext in exts
				])
				html += "</li>"

			html += "</ul>"
		html += "</ul></li>"
	html += "</ul>"

	with open(opj(folder, "index.html"), "w") as file:
		file.write(html)

Exams().load().save("data/exams")

students_folder = "data/students"

for mode in ["offline", "online"]:
	input_folder = opj(students_folder, "raw")
	output_folder = opj(students_folder, mode)

	students = Students()\
	.load(input_folder, mode == "online")\
	.compute_rankings(["Tot. ecrit", "Tot.", "Note"])\
	.add_ranks("Rang (classe)")

	if mode == "online":
		students.anonymize_general_ranks("Rang")

	students.save(output_folder)

	rank_students(
		opj(output_folder, "Classement - Mines Ponts.txt"),
		students,
		"Mines Ponts",
		"Mines Ponts MP",
		12
	)
	rank_students(
		opj(output_folder, "Classement - Centrale.txt"),
		students,
		"Centrale",
		"Centrale Paris filière MP",
		19
	)

	list_students(output_folder)