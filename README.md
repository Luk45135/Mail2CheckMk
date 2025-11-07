# Mail2CheckMk

Mail2CheckMk is a [checkmk](https://checkmk.com/) localcheck that reads emails from a IMAP server, parses them with RegEx and saves them to service files that are then printed to stdout to be sent to checkmk.

Why? - Do you have a stupid service that can't use SNMP and can only send emails? Then you can write a config file for your specific service and let Mail2CheckMk handle the rest.

Mail2CheckMk is built with user-serviceability in mind. Everything is saved in easy to read and override txt files.


# Installation

This project is packaged with [uv](https://docs.astral.sh/uv/).


Git clone this repo or download the archive and extract it to your chosen location.

On Debian make sure you have python3-venv installed.
`sudo apt install python3.13-venv`

Create a virtual environment.
`python3 -m venv .venv`

Enter the venv.
`source .venv/bin/activate`

Update pip.
`pip install --upgrade pip`

Install the needed requirements.
`pip install -r requirements.txt`

You can now exit the venv with `exit` or by pressing Ctrl+D


# Configure

Configure your IMAP server and login details in `./config/config.cfg`.

Use a template or create your own service config file in `./config/services/~Your config file~.cfg`.

# Usage
To manually run this script for debugging purposes you can either:

Enter the venv.
`source .venv/bin/activate`

Run the main file.
`python main.py`

--OR--

Directly run the script.
`.venv/bin/python main.py`
