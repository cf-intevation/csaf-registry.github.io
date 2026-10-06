#!/usr/bin/env python
# SPDX-FileCopyrightText: 2026 Intevation GmbH <https://intevation.de>
# SPDX-License-Identifier: Apache-2.0

import json
import os
from datetime import UTC, datetime
from pathlib import Path

from github import Github, Repository


def load_registry(repo: Repository.Repository, path: str):
    res = {}
    for entry in repo.get_contents(path):
        if entry.type == 'file' and entry.name in ['mapping.json', 'registry.json']:
            res[Path(entry.name).stem.lower()] = json.loads(entry.decoded_content.decode('utf-8'))
        elif entry.type == 'file' and entry.name in ['README.md', 'README', 'README.txt', 'README.rst']:
            res[Path(entry.name).stem.lower()] = entry.decoded_content.decode('utf-8')
    return res

def create_hugo_data(data: dict):
    gitignore = []
    gi = Path('.gitignore')
    if gi.exists() and gi.is_file():
        with gi.open() as f:
            gitignore = [x.strip() for x in f.readlines()]
    updated = datetime.fromtimestamp(0, UTC)
    for name, registry in data.items():
        ignore_line = f'/content/{name}/'
        if not ignore_line in gitignore:
            gitignore.append(ignore_line)
        os.makedirs(f'content/{name}', exist_ok=True)
        for kind in ['registry', 'mapping']:
            tmp = registry.get(kind, {}).get('last_updated', None)
            if tmp is not None:
                dt = datetime.fromisoformat(tmp)
                updated = max(dt, updated)
            if kind in registry:
                lines = [
                    '+++',
                    f'title = \'{name}::{kind}.json\'',
                    f'date = {registry.get(kind, {}).get("last_updated", datetime.now(UTC).replace(microsecond=0).isoformat().replace('+00:00', 'Z'))}',
                    '+++',
                    f'{{{{< highlight_source registry="{name}" src="{kind}" type="json" >}}}}'
                ]
                with open(f'content/{name}/{kind}.md', 'w') as f:
                    f.write('\n'.join(lines))
                    f.write('\n')
        if int(updated.timestamp()) == 0:
            updated = datetime.now(UTC)
        lines = [
            '+++',
            f'title = \'Registry {name}\'',
            'type = \'page\'',
            'layout = \'combined\'',
            f'date = {registry.get("last_updated", updated.replace(microsecond=0).isoformat().replace('+00:00', 'Z'))}',
            '[params]',
            f'registry = \'{name}\'',
            '+++'
        ]
        with open(f'content/{name}/_index.md', 'w') as f:
            f.write('\n'.join(lines))
            f.write('\n')
    with gi.open('w') as f:
        f.write('\n'.join(gitignore))
        f.write('\n')

def main():
    gh = Github(lazy=True)
    repo = gh.get_repo('oasis-tcs/csaf')
    registries = {}
    for entry in repo.get_contents('registry'):
        if entry.type == 'dir':
            print(f'Downloading Registry {entry.name} from {repo.owner.login}/{repo.name}')
            registries[entry.name.lower()] = load_registry(repo, f'registry/{entry.name}')
    os.makedirs('data', exist_ok=True)
    with open('data/registries.json', 'w') as f:
        json.dump(registries, f, indent=2)
    create_hugo_data(registries)

if __name__ == '__main__':
    main()
