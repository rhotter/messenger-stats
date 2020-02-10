"""
Want:
- average response time
- tf idf
- average individual message length
"""

import json
import pandas as pd
from helpers import *

def get_all_stats(file_names):
    all_stats = []
    for file in file_names:
        file_stats = get_stats(file)
        if file_stats:
            all_stats.append(file_stats)

    return pd.DataFrame(all_stats)

def get_stats(file):
    with open(file) as f:
        data = json.load(f)
    person = get_person(data)
    num_participants = len(data["participants"])
    if num_participants > 2:
        # don't consider group chats
        return None
    if not {m["sender_name"] for m in data["messages"]}.issubset({MY_NAME, person}):
        return None # group chats that have become 2 person chats
    
    my_word_count, their_word_count, total_word_count = word_counts(data)
    my_average_word_size, their_average_word_size = average_word_size(data)
    my_average_message_size, their_average_message_size = average_message_size(data, my_word_count, their_word_count)
    word_count_percent_difference = percent_more_less(my_word_count, their_word_count)
    num_links_sent, num_links_received = link_count(data)
    num_links_percent_difference = percent_more_less(num_links_sent, num_links_received)
    my_words_to_links_ratio, their_words_to_links_ratio, our_words_to_links_ratio = words_to_something_ratio(data, num_links_sent, num_links_received, my_word_count, their_word_count)
    num_photos_sent, num_photos_received = photos_count(data)
    num_photos_percent_difference = percent_more_less(num_photos_sent, num_photos_received)
    my_words_to_photos_ratio, their_words_to_photos_ratio, our_words_to_photos_ratio = words_to_something_ratio(data, num_photos_sent, num_photos_received, my_word_count, their_word_count)

    response_times_list = response_times(data)
    print(data["participants"])
    for r in response_times_list:
        print(r)
    print()


    return {
        "person": person,
        "my word count": my_word_count,
        "their word count": their_word_count,
        "total word count": total_word_count,
        "my average word size": my_average_word_size,
        "their average word size": their_average_word_size,
        "my average message size": my_average_message_size,
        "their average message size": their_average_message_size,
        "word count percent difference": word_count_percent_difference,

        "num links sent": num_links_sent,
        "num links received": num_links_received,
        "num links percent difference": num_links_percent_difference,
        "my words to links ratio" : my_words_to_links_ratio,
        "their words to links ratio" : their_words_to_links_ratio,
        "our words to links ratio" : our_words_to_links_ratio,

        "num photos sent": num_photos_sent,
        "num photos received": num_photos_received,
        "num photos percent difference": num_photos_percent_difference,
        "my words to photos ratio" : my_words_to_photos_ratio,
        "their words to photos ratio" : their_words_to_photos_ratio,
        "our words to photos ratio" : our_words_to_photos_ratio,

    }