#!/usr/bin/env python
"""
Helper for parsing magic costs.

Accepts a single argument: path to a JSON file containing full card data for
the cards you wish to parse.

Outputs a JSON file with just the magicCost and effectMagicCost keys (and
a text key for cards that have costs that require manual processing).

YOU MUST EDIT THE RESULTING JSON BY HAND. This script speeds things up, but
does not handle the `diceRecursion` key and doesn't try to parse costs in
effect text.

Keys used by magic cost logic:

* `magicCost`: object with keys that are the names of the dice types, and
  values that are integers. Parallel costs are represented by a slash in
  the key name like `divine / sympathy`
* `effectMagicCost`: identical to `magicCost`, but tracks costs incurred in
  the card effects. Note that this is the cost for a single activation.
  The site does not try to predict how many times you will actually activate
  a card like Jessa or Frost Fang.
* `diceRecursion`: a root-level integer that represents the number of dice
  this card returns from the exhausted pool as part of its effects. Defaults
  to 1 for things like Empower or Battle Mage where the number is actually
  optional or variable depending on usage.
"""

import json
import re
import os.path
import sys


cost_types = ['basic', 'ceremonial', 'charm', 'illusion', 'natural', 'divine', 'sympathy', 'time']
magic_cost_re = re.compile(r'(\d+)\s+\[\[((?:' + r'|'.join(cost_types) + r')(?::\w+)?)\]\]')


def parse_cost(cost, data_object, cost_key='magicCost'):
    # Handle a split cost
    if isinstance(cost, list):
        split_1 = magic_cost_re.match(cost[0])
        split_2 = magic_cost_re.match(cost[1])
        if not split_1 or not split_2:
            return
        split_key = '{} / {}'.format(split_1.group(2), split_2.group(2))
        alt_split_key = '{} / {}'.format(split_2.group(2), split_1.group(2))
        magic_cost = max(int(split_1.group(1)), int(split_2.group(1)))
        if split_key in data_object:
            data_object[cost_key][split_key] += magic_cost
        elif alt_split_key in data_object:
            data_object[cost_key][alt_split_key] += magic_cost
        else:
            data_object[cost_key][split_key] = magic_cost
        return
    # Normal cost, so just add it to our object
    cost_match = magic_cost_re.match(cost)
    if not cost_match:
        return
    if cost_match.group(2) in data_object[cost_key]:
        data_object[cost_key][cost_match.group(2)] += int(cost_match.group(1))
    else:
        data_object[cost_key][cost_match.group(2)] = int(cost_match.group(1))
    


def cleanup_data(data_object, delete_text=False, skip_effect_cost=False):
    if not data_object['magicCost']:
        del data_object['magicCost']
    if not data_object['effectMagicCost'] and not skip_effect_cost:
        del data_object['effectMagicCost']
    if delete_text and 'text' in data_object:
        del data_object['text']


file_path = sys.argv[1]
if not os.path.exists(file_path):
    print('Requires a valid path to a JSON file as the only argument')
    sys.exit()

with open(file_path) as file:
    content = file.read()
    data = json.loads(content)
    new_data = {}
    for card in data:
        stub = card['stub']
        new_data[stub] = {
            'magicCost': {},
            'effectMagicCost': {},
            'text': card.get('text')
        }
        # Parse out the card costs
        for cost in card.get('cost', []):
            parse_cost(cost, new_data[stub])
        # No need to continue if we don't have any effect text
        if not new_data[stub]['text']:
            cleanup_data(new_data[stub], delete_text=True)
            continue
        # Check to see if there are any inline costs (we'll handle these by hand)
        card_text = []
        for effect in new_data[stub]['text']:
            if effect.get('name', None) == 'Respark':
                parse_cost(effect['text'], new_data[stub], cost_key='effectMagicCost')
            else:
                card_text.append(effect['text'].replace('[[', '').replace(']]', ''))
            for cost in effect.get('cost', []):
                parse_cost(cost, new_data[stub], cost_key='effectMagicCost')
        card_text = ' '.join(card_text)
        if any(x in card_text for x in cost_types):
            cleanup_data(new_data[stub], skip_effect_cost=True)
            continue
        # If nothing in the effect text, remove it
        cleanup_data(new_data[stub], delete_text=True)
    content = json.dumps(new_data, indent=4)
    with open('./dice_counts.json', mode='w') as new_file:
        new_file.write(content)

print(
    'All done! Remember to edit JSON by hand to ensure effect costs, '
    'diceRecursion, and effectRepeats keys are included.'
)
