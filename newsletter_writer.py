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
        {"role": "user", "content": 'I need you to return the headings to me as a JSON object. It is really important you *do not* act conversationally, just take a break and be a robot. Here is an example of what I want you to return: {"1": "Heading 1", "2": "Heading 2"].'},
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

    # Regular expression to find the JSON object
    #array_pattern = r'\[(?:\s*\{(?:[^{}]|(?R))*\}\s*,?)+\]'
    object_pattern = r'\{(?:[^{}]|(?R))*\}'

    # Search for the JSON object in the text
    text = aifunctions.getChoices(aiResponse)
    match = regex.search(object_pattern, text)

    try:
        print("Trying to load JSON")
        return json.loads(match.group())
    except Exception as e:
        print(f"Can't find any: {e}.")
    
    
async def getHeadingContent(heading, title):
    """
    """
    priming_sequence = [
        {"role": "system", "content": "You are an AI writer. You write compelling and informative content designed to help people understand complex topics."},
        {"role": "user", "content": "Mike: Hi, I'm a HR professional setting up your environment."},
        {"role": "assistant", "content": "It's nice to meet you."},
        {"role": "user", "content": f"Mike: You will receive one of many headings for a newsletter entitled {title} and job is to provide content for that heading."},
        {"role": "assistant", "content": "OK, I understand."},
       # {"role": "user", "content": 'I need you to return the headings to me as a JSON object. It is really important you *do not* act conversationally, just take a break and be a robot. Here is an example of what I want you to return: {"1": "Heading 1", "2": "Heading 2"].'},
       # {"role": "assistant", "content": "OK, I understand. What is the heading?"},
    ]

    priming_sequence.append(
        {"role": "user", "content": f"The heading is {heading}."},
    )
    options = {
        "messages": priming_sequence,
        "temperature": 1,
        "max_tokens": 1024,
        "n": 1,
        "stop": None,
    }

    aiResponse = aifunctions.chatCompletionQuery(options)
    text = aifunctions.getChoices(aiResponse)
    print(f"{heading}\n\n{text}")

async def getBlogPost(title, heading_count):
    """
    This boy does all the hard work
    """
    headings = getHeadings(title, heading_count)
    for order, section_heading in headings.items():
        await getHeadingContent(f"{order}: {section_heading}", title)
    
# Generate Intro para for each heading

# Generate

if __name__ == '__main__':

    asyncio.run(getBlogPost(
        title='Why I love HR',
        heading_count=5
    ))
