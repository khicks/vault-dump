# Vault Dump

This Python script will help you export all of your secrets data in Vault.

## Requirements

You will need Python3 with the requests module. Ubuntu may have this installed by default.

## Parameters

vault-dump requires two parameters: a Vault address and token.

The address is obtained by the first of whichever is set:

* Passed into the script with the `-a` flag.
* The `VAULT_ADDR` environment variable.
* A default value of `http://127.0.0.1:8200`.

The token is obtained by the first of whichever is set:

* Passed into the script with the `-t` flag.
* The `VAULT_TOKEN` environment variable.
* The `~/.vault-token` file.

There is no default value for the Vault token. It must be set, or the script will fail.

## Usage

You can run the script like so:

    $ chmod +x vault-dump.py
    $ ./vault-dump.py [-a ADDRESS] [-t TOKEN]
    
The contents of your Vault server will be written to `$HOME/vault-dump/<time>/`.

## To do

* KV 1 secrets engine.
* Detect and enumerate through secrets engines.