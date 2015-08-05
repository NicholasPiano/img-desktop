import re

totalR_line_template = r'HardwareSetting\|ScannerSettingRecord\|dblVoxelX #1: (.*)'
totalC_line_template = r'HardwareSetting\|ScannerSettingRecord\|dblVoxelY #1: (.*)'
totalZ_line_template = r'HardwareSetting\|ScannerSettingRecord\|dblSizeZ #1: (.*)'
tpf_line_template = r'HardwareSetting\|ScannerSettingRecord\|nDelayTime_s #1: (.*)'

value = lambda lines, template: re.match(template, list(filter(lambda l: re.match(template, l) is not None, lines))[0].rstrip()).group(1)

inf_path = './inf.txt'

with open(inf_path) as inf_file:
  lines = inf_file.readlines()

  totalR = float(value(lines, totalR_line_template))
  totalC = float(value(lines, totalC_line_template))
  totalZ = float(value(lines, totalZ_line_template))
  # tpf = float(value(lines, tpf_line_template))
  print(totalR, totalC, totalZ)
