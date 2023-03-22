import os
import openai
import time
import re
import asyncio
import sys
import logging

openai.api_key = os.environ["OPENAI_KEY"]  # Set the OpenAI API key

# Configure logging
logging.basicConfig(level=logging.INFO)


def get_last_paragraph(text):
    paragraphs = text.split("\n")
    last_paragraph = paragraphs[-1]
    last_paragraph_length = len(last_paragraph)
    document_length = len(text)
    return last_paragraph, last_paragraph_length, document_length


async def summarize_content(current_summary, last_message):
    current_summary = current_summary.replace("'", '')
    last_message = last_message.replace("'", '')
    prompt = f"Please summarise these texts: {current_summary or ''}\n\n{last_message}."
    request_params = {
        "model": "text-davinci-002",
        "prompt": prompt,
        "temperature": 0.7,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "max_tokens": 1024,
    }
    logging.info(f'Prompt: {prompt}')
    response = openai.Completion.create(**request_params)
    concatenated_summary = response["choices"][0]["text"].strip()
    logging.info(f'Summary: {concatenated_summary}')
    return concatenated_summary


async def generate_content(initial_prompt, desired_length):
    system_message = {
        "role": "system",
        "content": "You are an AI writer. You write compelling and informative content designed to help people understand complex topics."
    }
    
    priming_sequence = [
        {"role": "user", "content": "Mike: Hi, I'm a programmer setting up your environment."},
        {"role": "assistant", "content": "It's nice to meet you."},
        {"role": "user", "content": f"Mike: You will receive a document summary as a prompt, a length, the last paragraph that was written, and the desired length. You are going to interpolate this information to write custom, logical paragraphs that will help the user understand the topic. The difference between the length and desired length will let you know how much more you need to write. You can use the last paragraph to help you write the next paragraph. You can also use the prompt to help you understand the topic. Make sense?"},
        {"role": "assistant", "content": "Yes, I think so. I'm ready to begin."},
        {"role": "user", "content": "Mike: Great! Let's get started."},
    ]
    
    messages = [system_message] + priming_sequence
    prompt_object = {
        "prompt": initial_prompt,
        "desired_length": desired_length,
        "last_paragraph": "",
        "last_paragraph_length": 0,
        "document_length": 0,
    }
    all_messages = []

    while True:
        summary = prompt_object.get("summary", "")
        prompt = prompt_object["prompt"]
        desired_length = prompt_object["desired_length"]
        last_paragraph = prompt_object["last_paragraph"]
        last_paragraph_length = prompt_object["last_paragraph_length"]
        document_length = prompt_object["document_length"]
        
        messages.append(
            {
                "role": "user",
                "content": f"You are writing this blog post: {prompt}\n\nYou have written {document_length} characters so far, and this is a summary of the current content: {summary}. You need to write {desired_length - document_length} more characters. You will get multiple opportunities, so only write 300-500 characters at atime. Please use a British English dictionary. Your last paragraph was: {last_paragraph}.",
            }
        )
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=1,
            max_tokens=1024,
            n=1,
            stop=None,
        )

        new_message = response.choices[0]['message']['content'].strip()
        all_messages.append(new_message)

        new_document_length = len(re.sub(r'\s+', ' ', ''.join(all_messages)))
        new_last_paragraph, new_last_paragraph_length, _ = get_last_paragraph(new_message)
        finished = new_document_length >= desired_length

        if finished:
            logging.info(f"Finished! Length: {new_document_length} ({desired_length})")
            write_to_file("./file.md", all_messages)
            return

        new_summary = await summarize_content(summary, new_message)

        prompt_object = {
            "summary": new_summary,
            "prompt": prompt,
            "desired_length": desired_length,
            "last_paragraph": new_last_paragraph,
            "last_paragraph_length": new_last_paragraph_length,
            "document_length": new_document_length,
        }

        time.sleep(1)

def write_to_file(file_path, content):
    with open(file_path, "w") as f:
        f.write("\n\n".join(content))

initial_prompt = "5 Little Known HR Tricks for Hiring Top Talent"
desired_length = 7000 # This is around 1500 words

asyncio.run(generate_content(initial_prompt, desired_length))