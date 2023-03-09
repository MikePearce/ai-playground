import openai
import config, os
from pydub import AudioSegment
openai.api_key = config.OPENAI_API_KEY

def whisperQuery(filename):
    
    audio_file = open(filename, "rb")
    path_name, filename = os.path.split(filename)

    lesson = AudioSegment.from_file(audio_file, "mp4")

    # PyDub handles time in milliseconds
    ten_minutes = 10 * 60 * 1000
    first_10_minutes = lesson[:ten_minutes]
    new_file_name = f"{path_name}/10_{filename}"
    first_10_minutes.export(new_file_name, format="mp4")    

    return openai.Audio.transcribe("whisper-1", open(new_file_name, "rb"))


def openAIQuery(query):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=query,
        temperature=0.7,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    if 'choices' in response:
        if len(response['choices']) > 0:
            answer = response['choices'][0]['text']
        else:
            answer = 'Opps sorry, you beat the AI this time'
    else:
        answer = 'Opps sorry, you beat the AI this time'

    return answer
