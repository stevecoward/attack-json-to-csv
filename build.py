#!/usr/bin/env python
import click
import csv
from itertools import zip_longest
import json
import os
import requests
import sys

github_enterprise_attack = 'https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json'

tactics = {
    'Initial Access': [],
    'Execution': [],
    'Persistence': [],
    'Privilege Escalation': [],
    'Defense Evasion': [],
    'Credential Access': [],
    'Discovery': [],
    'Lateral Movement': [],
    'Collection': [],
    'Command And Control': [],
    'Exfiltration': [],
    'Impact': [],
}


def get_remote_techniques():
    """Fetches enterprise att&ck data from its github source
    and parses it into a json file.
    """
    if not os.path.exists('techniques.json'):
        click.secho(
            '[+] fetching remote att&ck data for parsing...', fg='green')
        response = requests.get(github_enterprise_attack)
        if not response.ok:
            click.secho('[!] error fetching raw att&ck json data', 'fg=red')
            sys.exit(1)

        click.secho('[+] parsing att&ck data...', fg='yellow')
        parsed_objects = []
        attack_blob = response.json()
        # We're only concerned with objects of type 'attack-pattern' from the enterprise att&ck data
        attack_blob = [obj for obj in attack_blob['objects']
                       if obj['type'] == 'attack-pattern']
        for attack_object in attack_blob:
            technique_id = [obj['external_id'] for obj in attack_object['external_references']
                            if obj['source_name'] == 'mitre-attack'][0]
            # The 'phases' value simply splits the kill_chain_phase elements into human-readable formats
            parsed_objects.append({
                'id': technique_id,
                'name': attack_object['name'],
                'phases': [' '.join(obj['phase_name'].split('-')).title() for obj in attack_object['kill_chain_phases']],
            })
        with open('techniques.json', 'w') as fh:
            fh.write(json.dumps(parsed_objects))
        click.secho(
            f'[!] successfully parsed att&ck data and wrote {len(parsed_objects)} records to techniques.json', fg='green')
    else:
        click.secho(
            '[!] techniques.json already exists, skipping', fg='yellow')


@click.command()
@click.argument('technique_json', type=click.Path(exists=True))
@click.argument('output_filename', type=str)
@click.option('--fetch-techniques', is_flag=True)
def main(technique_json, output_filename, fetch_techniques):
    """Takes a JSON file from ATT&CK Navigator and converts it to CSV format

    Args:

        technique_json (click.Path): ATT&CK Navigator JSON file
        output_filename (string): Name of the file to be saved
        fetch_techniques (bool): Flag to fetch remote techniques
    """
    # Fetch enterprise techniques if set
    if fetch_techniques:
        get_remote_techniques()

    #  Load all techniques from enterprise att&ck
    all_techniques = {}
    with open('techniques.json', 'r') as fh:
        all_techniques = json.loads(fh.read())

    # Parse user-submitted json, removing any duplicate keys to avoid showing dupes in the csv
    blob = {}
    with open(technique_json, 'r') as fh:
        click.secho('[+] parsing user-submitted json...', fg='yellow')
        blob = json.loads(fh.read())
    unique_techniques = list(
        {v['techniqueID']: v for v in blob['techniques']}.values())

    click.secho('[+] building tactics from json data...', fg='yellow')
    for technique in unique_techniques:
        found = [t for t in all_techniques if t['id']
                 == technique['techniqueID']][0]
        try:
            tactics[' '.join(technique['tactic'].split('-')).title()
                    ].append(f'{found["name"]} ({found["id"]})')
        except Exception as e:
            from pprint import pprint
            import ipdb
            ipdb.set_trace()
            x = None

    # Uses zip_longest here because the length of each list is not uniform
    rows = zip_longest(
        tactics['Initial Access'],
        tactics['Execution'],
        tactics['Persistence'],
        tactics['Privilege Escalation'],
        tactics['Defense Evasion'],
        tactics['Credential Access'],
        tactics['Discovery'],
        tactics['Lateral Movement'],
        tactics['Collection'],
        tactics['Command And Control'],
        tactics['Exfiltration'],
        tactics['Impact']
    )

    click.secho('[+] writing parsed data to csv...', fg='yellow')
    with open(f'{output_filename}.csv', 'w') as fh:
        writer = csv.writer(fh)
        writer.writerow(list(tactics.keys()))
        for row in rows:
            writer.writerow(row)
    click.secho('[!] process completed successfully!', fg='green')


if __name__ == '__main__':
    main()
