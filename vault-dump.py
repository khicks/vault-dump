#!/usr/bin/env python3

import os
import sys
from pathlib import Path
import getopt
import requests
import json
import datetime


def usage():
    print("usage: vault-dump.py [-a|--address URL] [-t|--token TOKEN]")


def get_token():
    if 'VAULT_TOKEN' in os.environ:
        return os.environ['VAULT_TOKEN']

    token_file = Path('/'.join([str(Path.home()), '.vault-token']))
    if token_file.is_file():
        with open(token_file) as f:
            return f.read()

    raise Exception("There is no Vault token. Please set a token value in env var 'VAULT_TOKEN', "
                    "the '~/.vault-token' file, or the '-t' arg.")


def parse_opts():
    address = None
    token = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'ha:t:', ['help', 'address=', 'token='])
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        if opt in ('-a', '--address'):
            address = arg
        if opt in ('-t', '--token'):
            token = arg

    if address is None:
        address = os.environ.get('VAULT_ADDR', 'http://127.0.0.1')

    if token is None:
        token = get_token()

    return {'address': address, 'token': token}


def vault_request(options, verb, path):
    r = requests.request(method=verb, url=options['address']+'/v1/'+path, headers={'X-Vault-Token': options['token']})
    if r.status_code != 200:
        raise Exception("API request failed: {verb} {path}".format(verb=verb, path=path))
    return json.loads(r.text)


def check_vault_token(options):
    try:
        vault_request(options, 'GET', 'auth/token/lookup-self')
    except Exception:
        raise Exception("Failed to authenticate to Vault at {address}".format(address=options['address']))


def fetch_kv2_secret(options, mount, path):
    secret_path = mount + 'data/' + path
    out_file = options['outdir']+mount+path+'.json'

    print(mount+path)
    secret = vault_request(options, 'GET', secret_path)

    with open(out_file, 'w') as f:
        json.dump(secret['data']['data'], f, indent=4)
        f.write('\n')


def list_kv2_secrets(options, mount, path=''):
    list_path = mount + 'metadata/' + path
    print(mount + path)

    secrets = vault_request(options, 'LIST', list_path)

    for element in secrets['data']['keys']:
        if element[-1] == '/':
            os.makedirs(options['outdir']+mount+path+element)
            list_kv2_secrets(options, mount, path+element)
        else:
            fetch_kv2_secret(options, mount, path+element)


def main():
    time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

    options = parse_opts()
    options['outdir'] = str(Path.home()) + '/vault-dump/dumps/' + time + '/'

    print('Dumping contents of Vault server at '+options['address'])
    print('Output directory is '+options['outdir'])
    print()

    check_vault_token(options)
    list_kv2_secrets(options, 'secret/')


if __name__ == "__main__":
    main()
