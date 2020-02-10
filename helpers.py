import os
import json
import pandas as pd
import re

MY_NAME = "Raffi Hotter"

def get_person(data):
    for person in data["participants"]:
        if person["name"] != MY_NAME:
            return person["name"]
    return ""

def get_file_names():
    path = "inbox"
    directories = next(os.walk(path))[1]
    return [os.path.join(path, d, "message_1.json") for d in directories]


def num_words(m):
    return len(m["content"].split())

def is_link(word):
    return 'http://' in word or 'https://' in word

def word_counts(data):
    my_word_count = 0
    their_word_count = 0
    for m in data["messages"]:
        if "content" in m: # make sure not image
            msg_length = num_words(m)
            if m["sender_name"] == MY_NAME:
                my_word_count += msg_length
            else:
                their_word_count += msg_length
    total_word_count = their_word_count + my_word_count

    return my_word_count, their_word_count, total_word_count

def link_count(data):
    num_links_sent = 0
    num_links_received = 0
    for m in data["messages"]:
        if "content" in m:
            num_links_in_message = sum([is_link(x) for x in m["content"].split()])
            if m["sender_name"] == MY_NAME:
                num_links_sent += num_links_in_message
            else:
                num_links_received += num_links_in_message

    return num_links_sent, num_links_received

def words_to_something_ratio(data, num_something_sent, num_something_received, my_word_count, their_word_count):
    try:
        my_words_to_something_ratio = my_word_count/num_something_sent
    except:
        my_words_to_something_ratio = None
    try:
        their_words_to_something_ratio = their_word_count/num_something_received
    except:
        their_words_to_something_ratio = None
    try:
        our_words_to_something_ratio = (my_word_count + their_word_count)/(num_something_received + num_something_sent)
    except:
        our_words_to_something_ratio = None
    return my_words_to_something_ratio, their_words_to_something_ratio, our_words_to_something_ratio
    
def photos_count(data):
    num_photos_sent = 0
    num_photos_received = 0
    for m in data["messages"]:
        if "photos" in m:
            if m["sender_name"] == MY_NAME:
                num_photos_sent += 1
            else:
                num_photos_received += 1

    return num_photos_sent, num_photos_received

# Facebook Messenger encoding of emoji is complicated
# def emoji_count(data):
#     num_emojis_sent = 0
#     num_emojis_received = 0
#     for m in data["messages"]:
#         if "content" in m:
#             num_emojis_in_message = len(re.findall(u'[\u0001f600-\u0001f650]', m["content"]))
#             if m["sender_name"] == MY_NAME:
#                 num_emojis_sent += num_emojis_in_message
#             else:
#                 num_emojis_received += num_emojis_in_message

#     return num_emojis_sent, num_emojis_received

def average_word_size(data):
    my_total_word_size = 0
    my_total_word_count = 0
    their_total_word_size = 0
    their_total_word_count = 0
    for m in data["messages"]:
        message_total_word_size = 0
        message_word_count = 0
        if "content" in m: # make sure not image
            # make sure not link
            message_total_word_size += sum([len(x)*(1-is_link(x)) for x in m["content"].split()])
            message_word_count += num_words(m)
            if m["sender_name"] == MY_NAME:
                my_total_word_count += message_word_count
                my_total_word_size += message_total_word_size
            else:
                their_total_word_count += message_word_count
                their_total_word_size += message_total_word_size
    
    if my_total_word_count != 0: # avoid divide by 0
        my_average_word_size = my_total_word_size/my_total_word_count
    else:
        my_average_word_size = 0
    if their_total_word_count != 0:
        their_average_word_size = their_total_word_size/their_total_word_count
    else:
        their_average_word_size = 0
    
    return my_average_word_size, their_average_word_size

def average_message_size(data, my_word_count, their_word_count):
    # new message is when the person speaking switches
    # (group consecutive messages together)
    their_name = get_person(data)
    num_messages = {
        MY_NAME: 0,
        their_name: 0
    }

    last_person_speaking = ""
    for m in data["messages"]:
        person_speaking = m["sender_name"]
        if person_speaking != last_person_speaking:
            num_messages[person_speaking] += 1
        last_person_speaking = person_speaking
    try:
        my_average_message_size = my_word_count / num_messages[MY_NAME]
    except:
        my_average_message_size = 0
    try: 
        their_average_message_size = their_word_count / num_messages[their_name]
    except:
        their_average_message_size = 0

    return my_average_message_size, their_average_message_size

def percent_more_less(my_count, their_count):
    # I speak _% more than you in our conversation (if positive number; reverse if negative)
    try:
        my_percentage = my_count/(my_count + their_count)
    except:
        my_percentage = None
    if my_percentage in [0.0,1.0, None] :
        return None
    their_percentage = 1-my_percentage
    if my_percentage >= 0.5:
        return my_percentage/their_percentage - 1
    else:
        return -(their_percentage/my_percentage - 1)

def response_times(data):
    last_time = data["messages"][-1]["timestamp_ms"]
    last_sender = data["messages"][-1]["sender_name"]
    response_times = []
    for m in reversed(data["messages"]):
        if m["sender_name"] != last_sender:
            response_time = m["timestamp_ms"] - last_time
            response_times.append(response_time)
            
            last_time = m["timestamp_ms"]
            last_sender = m["sender_name"]
    return response_times