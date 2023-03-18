import os
import openai
import time
import re
import asyncio

openai.api_key = os.environ["OPENAI_KEY"]  # set the OpenAI API key

def get_last_paragraph(text):
    paragraphs = text.split("\n")
    last_paragraph = paragraphs[-1]
    last_paragraph_length = len(last_paragraph)
    document_length = len(text)
    return last_paragraph, last_paragraph_length, document_length

async def summarize_content(current_summary, last_message):
    system_message = {
        "role": "system",
        "content": "You are an AI summarizer. You summarize content."
    }
    messages = [
        system_message,
        {
            "role": "user",
            "content": f"Please concatenate these texts: {current_summary or ''}\n\n{last_message}."
        }
    ]
    concatenate_stuff = {
        "model": "text-davinci-002",
        "prompt": messages,
        "temperature": 0.7,
        "frequency_penalty": 0,
        "presence_penalty": 0,
    }
    response = openai.Completion.create(**concatenate_stuff)
    concatenated_summary = response["choices"][0]["text"].strip()
    return concatenated_summary

async def generate_content(initial_prompt, desired_length):
    system_message = {
        "role": "system",
        "content": "You are an AI writer. You write compelling and informative content designed to help people understand complex topics."
    }
    priming_sequence = [
        {
            "role": "user",
            "content": "Mackenzie: Hi, I'm a programmer setting up your environment."
        },
        {"role": "assistant", "content": "It's nice to meet you."},
        {
            "role": "user",
            "content": f"Mackenzie: You will receive a document summary as a prompt, a length, the last paragraph that was written, and the desired length. You are going to interpolate this information to write custom, logical paragraphs that will help the user understand the topic. The difference between the length and desired length will let you know how much more you need to write. You can use the last paragraph to help you write the next paragraph. You can also use the prompt to help you understand the topic. Make sense?"
        },
        {"role": "assistant", "content": "Yes, I think so. I'm ready to begin."},
        {"role": "user", "content": "Mackenzie: Great! Let's get started."},
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
                "content": f"You are writing this blog post: {prompt}\n\nYou have written {document_length} characters so far, and this is a summary of the current content: {summary}. You need to write {desired_length - document_length} more characters. You will get multiple opportunities, so only write 100-300 characters at a time. Your last paragraph was: {last_paragraph}.",
            }
        )

        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=messages,
            temperature=1,
            max_tokens=1024,
            n=1,
            stop=None,
        )

        new_message = response.choices[0].text.strip()
        all_messages.append(new_message)

        new_document_length = len(re.sub(r'\s+', ' ', ''.join(all_messages)))
        new_last_paragraph, new_last_paragraph_length, _ = get_last_paragraph(new_message)
        finished = new_document_length >= desired_length

        if finished:
            print("Finished!")
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

initial_prompt = "5 Ways AI Chat Agents Can Streamline Customer Service for E-commerce Businesses."
desired_length = 7000

asyncio.run(generate_content(initial_prompt, desired_length))