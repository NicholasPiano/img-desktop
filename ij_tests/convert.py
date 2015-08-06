xls_file = './050714_s13_ch-zbf.xls'
csv_file = './test.csv'

tracks = {} # stores list of tracks that can then be put into the database

with open(xls_file, 'rb') as track_file:

  lines = track_file.read().decode('mac-roman').split('\n')[1:-1]
  for i, line in enumerate(lines): # omit title line and final blank line
    line = line.split('\t')

    # details
    track_id = int(float(line[1]))
    r = int(float(line[4]))
    c = int(float(line[3]))
    t = int(float(line[2])) - 1

    if track_id in tracks:
      tracks[track_id].append((r,c,t))
    else:
      tracks[track_id] = [(r,c,t)]

with open(csv_file, 'w+') as out_file:
  out_file.write('expt,series,channel,id,t,r,c\n')
  for track_id, track in tracks.items():
    for frame in list(sorted(track, key=lambda t: t[2])):
      out_file.write('{},{},{},{},{},{},{}\n'.format('expt','series','-zbf',track_id,frame[2],frame[0],frame[1]))
