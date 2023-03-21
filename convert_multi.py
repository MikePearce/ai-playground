import json
import datetime
import time as ptime
import aifunctions

def read_in_chunks(file, chunk_size=2048):
  while True:
      data = file.read(chunk_size)
      if not data:
          break
      yield data

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
        #line = '[' + str(datetime.timedelta(seconds=int(round(float(line_data['time']))))) + '] ' + line_data.get('speaker') + ': ' + line_data.get('line')
        speaker = line_data.get('speaker').replace("spk_0", "John").replace("spk_1", "Jack")
        line = speaker + ': ' + line_data.get('line')
        w.write(line + '\n')

      #Also write to a JSON file
      print(f"{filename}-withseconds.json")
      sorted_lines_data = []

      for line_data in sorted_lines:
          seconds_text = int(round(float(line_data['time'])))
          speaker = line_data.get('speaker').replace("spk_0", "John").replace("spk_1", "Jack")
          speaks = line_data.get('line')
          line = f'{speaker}: {speaks}'
          sorted_lines_data.append({seconds_text: line})

      with open(f"{filename}-withseconds.json", 'w') as seconds_file:
          json.dump(sorted_lines_data, seconds_file, indent=2)

      #Now, get the openAI summary
      #Open the text
      options = {
        "model": "text-davinci-003",
        "temperature":0.7,
        "max_tokens":1024,
        "top_p":1,
        "frequency_penalty":0,
        "presence_penalty":0
      } 

      print("Summarising")
      #It's too big to summarise in one go, so chunk it.
      with open(f"{filename}.txt", 'r', encoding='utf-8') as file:
          chunks = list(read_in_chunks(file))

      # For each chunk get a summary
      total_summary = ""
      for chunk in chunks:
        options["prompt"] = f"You are helping me summarise a long piece of text. There are two speakers: John and Jack. The current summary is \n\n'{total_summary}'. \n\nPlease summarise this text:\n\n {chunk.strip()} \n\nand add it to the previous summary so it makes sense. The summary should be around 300-500 words.",
        #print(aifunctions.completionQuery(options))
        total_summary = aifunctions.getChoices(aifunctions.completionQuery(options), "completionQuery")

      # Then get a summary of the summaries
      with open(f"{filename}-summary.txt", 'w') as summary:
          summary.write(total_summary)
        