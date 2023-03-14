import os
import boto3
import time
import urllib.request
import json
import pandas as pd
import convert_multi
import config
import logging
import sys
from botocore.exceptions import ClientError
from datetime import datetime
import time

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
SESSION_TOKEN = os.environ.get('AWS_SESSION_TOKEN')
BUCKET_NAME = 'tmp-transcribe-lessons-mikep'
FILE_NAME = 'MathsGCSE4.mp4'

logger = logging.getLogger(__name__)


def get_job(job_name, transcribe_client):
    """
    Gets details about a transcription job.
    :param job_name: The name of the job to retrieve.
    :param transcribe_client: The Boto3 Transcribe client.
    :return: The retrieved transcription job.
    """
    try:
        response = transcribe_client.get_transcription_job(
            TranscriptionJobName=job_name)
        job = response['TranscriptionJob']
        logger.info("Got job %s.", job['TranscriptionJobName'])
    except ClientError:
        logger.info("Couldn't get job %s.", job_name)
        return False
    else:
        return job


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
    
    # Check if a job exists first.
    file_uri = f'https://s3.amazonaws.com/{bucket_name}/{file_name}'
    while True:
        try:
            job = get_job(job_name, transcribe)
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if job['TranscriptionJobStatus'] == 'IN_PROGRESS':
                print(f"[{current_time}] Job exists and is still processing...")
            elif job['TranscriptionJobStatus'] == 'COMPLETED':
                print(f"[{current_time}] Job exists and processing has finished")
                return True
            else:
                print(f"[{current_time}] Job exists but is in an unexpected state: {job['TranscriptionJobStatus']}")
        except Exception as e:
            print(f"Job does not exist")
            break
        time.sleep(15)
    
    # Job doesn't exist
    try:
        media_format = file_name.split('.')[-1].lower()
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': file_uri},
            MediaFormat=media_format,
            LanguageCode='en-US',
            Settings={
                'ShowSpeakerLabels': show_speakers,
                'MaxSpeakerLabels': max_speakers
            }
        )
        print("Starting job...")
        return True
    except Exception as e:
        print(f"Failed to start job: {e}. File URI: {file_uri}")
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
    job = get_job(job_name, transcribe)
    
    while True:
        result = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if job['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            print(f"[{current_time}] Job status: {job['TranscriptionJobStatus']}")
            break
        print(f"[{current_time}] Job status: {job['TranscriptionJobStatus']}")
        time.sleep(15)

    print(f"Status of job {job_name}: {job['TranscriptionJobStatus']}")

    if job['TranscriptionJobStatus'] == 'COMPLETED':
        response = urllib.request.urlopen(job['Transcript']['TranscriptFileUri'])
        data = json.loads(response.read())
        json_filename = os.path.join(os.getcwd(), f"{job_name.split('.')[0]}.json")
        with open(json_filename, 'w') as file:
            json.dump(data, file)

        print(f"Transcription complete. JSON written to {json_filename}")
        return json_filename
    else:
        print(f"Transcription failed with status {job['TranscriptionJobStatus']}")
        return None


if __name__ == '__main__':

    # Get a unique Name
    #JOB_NAME = get_unique_filename(FILE_NAME)
    JOB_NAME = FILE_NAME

    # create the AWS client object
    transcribe = boto3.client(
        'transcribe',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_KEY,
        aws_session_token=SESSION_TOKEN,
        region_name='eu-west-2'
    )

    # Start the job
    if start_transcribe_job(transcribe, BUCKET_NAME, JOB_NAME, FILE_NAME):
        print("Trying to get transcription...")
        transcription_file = get_transcription_text(transcribe, JOB_NAME)
        if transcription_file:
            print("Converting JSON to multi person script file...")
            convert_multi.write_multiple_text(transcription_file)
        else:
            print("Failed to get transcription text.")
    else:
        print(f"Failed to start job {JOB_NAME}.")
