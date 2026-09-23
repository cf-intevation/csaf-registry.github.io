#!/usr/bin/env python
# SPDX-FileCopyrightText: 2026 Intevation GmbH <https://intevation.de>
# SPDX-License-Identifier: Apache-2.0

import json
import os
from pathlib import Path

from github import Github, Repository


def load_registry(repo: Repository.Repository, path: str):
    res = {}
    for entry in repo.get_contents(path):
        if entry.type == 'file' and (entry.name == 'mapping.json' or entry.name == 'registry.json'):
            res[Path(entry.name).stem] = json.loads(entry.decoded_content.decode('utf-8'))
    return res

def main():
    gh = Github(lazy=True)
    repo = gh.get_repo('oasis-tcs/csaf')
    registries = {'mapping': {}, 'registry': {}}

    for entry in repo.get_contents('registry'):
        if entry.type == 'dir':
            print(f'Downloading Registry {entry.name} from {repo.owner.login}/{repo.name}')
            loaded = load_registry(repo, f'registry/{entry.name}')
            if 'mapping' in loaded:
                registries['mapping'][entry.name] = loaded['mapping']
            if 'registry' in loaded:
                registries['registry'][entry.name] = loaded['registry']
    os.makedirs('data', exist_ok=True)
    with open('data/registries.json', 'w') as f:
        json.dump(registries, f, indent=2)

if __name__ == '__main__':
    main()
