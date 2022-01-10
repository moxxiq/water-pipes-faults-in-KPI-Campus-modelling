import json
import operator
import pprint
import re
from functools import reduce


filename = "result"


def flat_message(message):
    return dict(
        date=message["date"],
        text=message["text"]
        if isinstance(message["text"], str) else
        reduce(operator.add, (m if isinstance(m, str)
               else m["text"] for m in message["text"]))
    )


def lower_message_text(message):
    text = message["text"].lower()
    message["text"] = text
    return message


with open(filename + ".json") as f:
    # Open message, flat all texts, remove all empty
    messages = list(filter(lambda m: m["text"],
                           map(lower_message_text, map(
                               flat_message, json.load(f)["messages"]))
                           ))

# Filter to pass only messages with content related to water supply problems
key_words = ['води', 'водою', 'воды', 'водой', 'водопостачання', 'аварія тепломереж', '🥶', '🚿', ]
messages = list(filter(lambda m: any(
    w in m["text"] for w in key_words), messages))
# Filter to pass only messages with numbers
messages = list(filter(lambda m: re.search(
    r"(?:,| ?і| ?и| ?та) ?(\d+)", m["text"]), messages))

with open(filename + "_flatten.json", "w") as f:
    # Save flatten messages
    json.dump(messages,
              f,
              ensure_ascii=False,
              indent=4,
              )


# On this stage user manually removes some 'bad' messages
# or/and all numbers that not a dormitor, 'period to recovery' remove
def get_number_set(message):
    return dict(
        date=message["date"],
        dormitories=set(map(int, re.findall(r'\d+', message["text"])))
    )


with open(filename + "_flatten_manual_cleaned.json") as f:
    # Open message, extract sets of dormitory numbers
    messages = list(map(get_number_set, json.load(f)))

# Print all groups of dormitories that have problems with water supply
dormitories = sorted(
    set(
        map(lambda m: tuple(
            sorted(m["dormitories"])), messages)
    ),
    key=len
)[::-1]

print(*dormitories, sep='\n',)

print(len(messages), len(dormitories))
# pprint.pprint(messages)
