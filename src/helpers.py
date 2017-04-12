from collections import OrderedDict
import os, json
from src.settings import *

def ops(path):
	path = str(path)
	return [seg.strip(" ") for seg in path.split("/")] if path != "" else []

def opj(*argv):
	return "/".join(argv)

def old(folder):
	return list(filter(
		lambda name: os.path.isdir(os.path.join(folder, name)),
		os.listdir(folder)
	))

def olf(folder):
	return list(filter(
		lambda name: os.path.isfile(os.path.join(folder, name)),
		os.listdir(folder)
	))

def load_grid(year, exam):
	with open(opj(grids_folder, str(year), exam + ".json")) as file:
		return json.loads(file.read(), object_pairs_hook=OrderedDict)

def clean_value(value):
	if isinstance(value, float):
		value = round(value, 2)
		if value == int(value):
			value = int(value)

	return str(value)

def merge_lists(lists):
	merged_list = []

	for l in lists:
		for el in l:
			if not(el in merged_list):
				merged_list.append(el)
	
	return merged_list

def expand_dict(d, keys):
	expanded_dict = OrderedDict()

	for key in keys:
		if key in d.keys():
			expanded_dict[key] = d[key]
		else:
			expanded_dict[key] = ""

	return expanded_dict