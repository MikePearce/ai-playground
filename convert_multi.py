import json
import datetime
import time as ptime

def write_multiple_text(filename):
  # example filename: audio.json
  
  # take the input as the filename
  
  filename = (filename).split('.')[0]

  # Create an output txt file
  print(filename+'.txt')
  with open(filename+'.txt','w') as w:
    with open(filename+'.json') as f:

      data=json.loads(f.read())
      labels = data['results']['speaker_labels']['segments']
      speaker_start_times={}
      
      for label in labels:
        for item in label['items']:
          speaker_start_times[item['start_time']] = item['speaker_label']

      items = data['results']['items']
      lines = []
      line = ''
      time = 0
      speaker = 'null'
      i = 0

      # loop through all elements
      for item in items:
        i = i+1
        content = item['alternatives'][0]['content']

        # if it's starting time
        if item.get('start_time'):
          current_speaker = speaker_start_times[item['start_time']]
        
        # in AWS output, there are types as punctuation
        elif item['type'] == 'punctuation':
          line = line + content

        # handle different speaker
        if current_speaker != speaker:
          if speaker:
            lines.append({'speaker':speaker, 'line':line, 'time':time})
          line = content
          speaker = current_speaker
          time = item['start_time']
          
        elif item['type'] != 'punctuation':
          line = line + ' ' + content
      lines.append({'speaker': speaker, 'line': line,'time': time})

      # sort the results by the time
      sorted_lines = sorted(lines,key=lambda k: float(k['time']))

      # write into the .txt file
      for line_data in sorted_lines:
        line = '[' + str(datetime.timedelta(seconds=int(round(float(line_data['time']))))) + '] ' + line_data.get('speaker') + ': ' + line_data.get('line')
        w.write(line + '\n\n')