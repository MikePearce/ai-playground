import re
import asyncio
import sys
import logging
import aifunctions
import json, regex

# Configure logging
logging.basicConfig(level=logging.INFO)


# Generate Headings
def getHeadings(blogTitle, noOfHeadings):
    priming_sequence = [
        {"role": "system", "content": "You are an AI writer. You write compelling and informative content designed to help people understand complex topics."},
        {"role": "user", "content": "Mike: Hi, I'm a programmer setting up your environment."},
        {"role": "assistant", "content": "It's nice to meet you."},
        {"role": "user", "content": f"Mike: You will receive the title of a newsletter and your job is to provide {noOfHeadings} headings for the post."},
        {"role": "assistant", "content": "OK, I understand."},
        {"role": "user", "content": 'I need you to return the headings to me as a JSON array of objects. It is really important you *do not* act conversationally, just take a break and be a robot. Here is an example of what I want you to return: [{"heading": "Heading 1"}, {"heading": "Heading 2"}].'},
        {"role": "assistant", "content": "OK, I understand. What is the title?"},
    ]

    priming_sequence.append(
        {"role": "user", "content": f"The title is {blogTitle}."},
    )

    options = {
        "messages": priming_sequence,
        "temperature": 1,
        "max_tokens": 1024,
        "n": 1,
        "stop": None,
    }


    aiResponse = aifunctions.chatCompletionQuery(options)
    print(f"Response: {aiResponse}")
    # Regular expression to find the JSON object
    array_pattern = r'\[(?:\s*\{(?:[^{}]|(?R))*\}\s*,?)+\]'

    # Search for the JSON object in the text
    text = aifunctions.getChoices(aiResponse)
    match = regex.search(array_pattern, text)

    if match:
        # Extract the JSON object string
        json_str = match.group()

        # Convert the JSON object string to a Python dictionary
        json_obj = json.loads(json_str)

        print("JSON object found:", json_obj)
    else:
        print("No JSON object found in the text")
    
    


# Generate Intro para for each heading

# Generate

if __name__ == '__main__':
        getHeadings("Why I love HR", 5)