import os
import boto3
import time
import urllib.request
import json
import pandas as pd
import convert_multi

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
BUCKET_NAME = 'myt-test-transcribe'
FILE_NAME = '10_Sample_lesson_recording_1.mp4'


def get_unique_filename(filename):
    """
    Returns a unique filename by appending a timestamp to the input filename.

    Parameters
    ----------
    filename : str
        The filename to be made unique.

    Returns
    -------
    str
        A unique filename.
    """
    timestamp = str(int(time.time()))
    basename, ext = os.path.splitext(filename)
    unique_filename = f'{basename}-{timestamp}{ext}'
    return unique_filename


def start_transcribe_job(transcribe, bucket_name, job_name, file_name, max_speakers=2, show_speakers=True):
    """
    Starts an AWS Transcribe job.

    Parameters
    ----------
    transcribe : boto3.client
        A boto3 client for the AWS Transcribe service.
    bucket_name : str
        The name of the S3 bucket where the file to be transcribed is located.
    job_name : str
        The name of the Transcribe job to be started.
    file_name : str
        The name of the file to be transcribed.
    max_speakers : int, optional
        The maximum number of speakers to be detected in the file, by default 2.
    show_speakers : bool, optional
        Whether or not to label speaker changes in the transcription, by default True.

    Returns
    -------
    bool
        True if the job was started successfully, False otherwise.
    """
    if max_speakers > 10:
        raise ValueError("Maximum detected speakers is 10.")

    file_uri = f'https://s3.amazonaws.com/{bucket_name}/{file_name}'

    try:
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': file_uri},
            MediaFormat='mp4',
            LanguageCode='en-US',
            Settings={
                'ShowSpeakerLabels': show_speakers,
                'MaxSpeakerLabels': max_speakers
            }
        )
        print("Starting job...")
        return True
    except Exception as e:
        print(f"Failed to start job: {e}")
        return False


def get_transcription_text(transcribe, job_name):
    """
    Returns transcription text for an AWS Transcribe job and writes it to a JSON file

    Parameters
    ----------
    transcribe : boto3.client
        A boto3 client for the AWS Transcribe service.
    job_name : str
        The name of the Transcribe job.

    Returns
    -------
    str
        The filename of a JSON file containing the transcription.
    """
    job = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    status = job['TranscriptionJob']['TranscriptionJobStatus']

    while True:
        result = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if result['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        
    print(f"Status of job {job_name}: {result['TranscriptionJob']['TranscriptionJobStatus']}")
    time.sleep(15)

    if result['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
        response = urllib.request.urlopen(job['TranscriptionJob']['Transcript']['TranscriptFileUri'])
        data = json.loads(response.read())
        json_filename = os.path.join(os.getcwd(), f"{job_name.split('.')[0]}.json")
        with open(json_filename, 'w') as file:
            json.dump(data, file)

        print(f"Transcription complete. JSON written to {json_filename}")
        return json_filename
    else:
        print(f"Transcription failed with status {result['TranscriptionJob']['TranscriptionJobStatus']}")
        return None


if __name__ == '__main__':

    # Get a unique Name
    JOB_NAME = get_unique_filename(FILE_NAME)

    # create the AWS client object
    transcribe = boto3.client(
        'transcribe',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name='eu-west-2'
    )

    # Start the job
    if start_transcribe_job(transcribe, BUCKET_NAME, JOB_NAME, FILE_NAME):
        transcription_file = get_transcription_text(transcribe, JOB_NAME)
        if transcription_file:
            print("Converting JSON to multi person script file...")
            convert_multi.write_multiple_text(transcription_file)
        else:
            print("Failed to get transcription text.")
    else:
        print(f"Failed to start job {JOB_NAME}.")
