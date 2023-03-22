import re
import asyncio
import sys
import logging
import aifunctions
import json, regex
import config

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
        {"role": "user", "content": f"Mike: You will receive one of many headings for a newsletter entitled {title} and job is to provide content for that heading. It is really important you *do not* act conversationally, just take a break and be a robot."},
        {"role": "assistant", "content": "OK, I understand."}
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
    return text

async def getPostSummary(title):
    """
    Get a conclusion para
    """
    with open(f"{config.SAVE_FOLDER}/{title}.md", 'r') as file:
        text = file.read()
    
    priming_sequence = [
        {"role": "user", "content": "Mike: Please summarize this text {text}"},
    ]

    options = {
        "messages": priming_sequence,
        "temperature": 1,
        "max_tokens": 1024,
        "n": 1,
        "stop": None,
    }

    aiResponse = aifunctions.chatCompletionQuery(options)
    return aifunctions.getChoices(aiResponse)
    

def write_to_file(file_path, content, openhow="a"):
    with open(file_path, openhow) as f:
        f.write(content)

async def getBlogPost(title, heading_count):
    """
    This boy does all the hard work
    """
    write_to_file(
        f"{config.SAVE_FOLDER}/{title}.md", 
        f"# {title}\n\n",
        "w"
    )  
    print("Getting Headings")
    headings = getHeadings(title, heading_count)
    print("Populating Headings")
    for order, section_heading in headings.items():
        write_to_file(
            f"{config.SAVE_FOLDER}/{title}.md", 
            f"## {order}. {section_heading}\n\n"
        )        
        write_to_file(
            f"{config.SAVE_FOLDER}/{title}.md", 
            f"{await getHeadingContent(section_heading, title)}\n\n"
        )
        print(f"Heading [{section_heading}] written to file")
    
    print("Getting a conclusion")
    write_to_file(
        f"{config.SAVE_FOLDER}/{title}.md", 
        await getPostSummary(title)
    )
    
    print(f"Finished writing: {title}")


# Generate Intro para for each heading

# Generate

if __name__ == '__main__':

    asyncio.run(getBlogPost(
        title='Why I love HR',
        heading_count=5
    ))
