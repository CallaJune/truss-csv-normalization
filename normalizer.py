import csv
from datetime import datetime
import pytz
import rfc3339
import sys

def normalize_timestamp(s):
	"""
	Input: String in month/day/year hour:minute:second AM/PM format
	Output: String of datetime object converted from assumed PDT to EDT in RFC3339 format
	"""
	datetime_object = datetime.strptime(s, "%m/%d/%y %I:%M:%S %p")
	source_timezone = pytz.timezone("America/Los_Angeles")
	target_timezone = pytz.timezone("America/New_York")
	datetime_object_converted = source_timezone.localize(datetime_object, is_dst=True).astimezone(target_timezone)
	return rfc3339.rfc3339(datetime_object_converted)

def normalize_zip(s):
	"""
	Input: Expects a string containing only numeric characters of length <= 5
	Output: A string of length 5 with 0s inserted at the front of input if input string length < 5
	"""
	if len(s) > 5 or not int(s):
		raise ValueError("Zip code {} is not in the right format.".format(s))
	return s if len(s) == 5 else ("0" * (5 - len(s))) + s

def normalize_fullname(s):
	"""
	Input: A string
	Output: A string with characters that can be capitalized set to uppercase
	"""
	return s.upper()

def normalize_duration(s):
	"""
	Input: String in HH:MM:SS.MS format
	Output: Float representing number of seconds
	"""
	split_duration = s.split(":")
	hours = int(split_duration[0])
	minutes = int(split_duration[1])
	seconds = float(split_duration[2])
	return seconds + (minutes * 60) + (hours * 3600)

def main(input_file, output_file):
	reader = csv.reader(input_file, delimiter=",")
	writer = csv.writer(output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)

	header = {}	
	for row in reader:
		if header == {}:
			for col_index in range(len(row)):
				header[row[col_index]] = col_index
			writer.writerow(row)
			continue

		try:
			row[header["Timestamp"]] = normalize_timestamp(row[header["Timestamp"]])
			row[header["ZIP"]] = normalize_zip(row[header["ZIP"]])
			row[header["FullName"]] = normalize_fullname(row[header["FullName"]])
			fooDuration = normalize_duration(row[header["FooDuration"]])
			barDuration = normalize_duration(row[header["BarDuration"]])
			row[header["FooDuration"]] = fooDuration
			row[header["BarDuration"]] = barDuration
			row[header["TotalDuration"]] = fooDuration + barDuration
		except Exception as e:
			sys.stderr.write("Dropped the following row due to error: {}\n".format(str(row)))
			continue

		writer.writerow(row)

if __name__ == "__main__":
	sys.stdin.reconfigure(encoding="utf-8", errors="replace")
	main(sys.stdin, sys.stdout)