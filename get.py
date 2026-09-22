#!/usr/bin/env python
# SPDX-FileCopyrightText: 2026 Intevation GmbH <https://intevation.de>
# SPDX-License-Identifier: Apache-2.0

import json
import os

import requests

r = requests.get('https://github.com/oasis-tcs/csaf/raw/refs/heads/master/registry/id/mapping.json')
data = r.json()
os.makedirs('data', exist_ok=True)
with open('data/mapping.json', 'w', newline='\n') as f:
    json.dump(data, f, indent=2)
r = requests.get('https://github.com/oasis-tcs/csaf/raw/refs/heads/master/registry/id/registry.json')
data = r.json()
with open('data/registry.json', 'w', newline='\n') as f:
    json.dump(data, f, indent=2)
