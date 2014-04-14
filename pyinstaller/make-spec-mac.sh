#! /bin/bash
pyinstaller --windowed --name mailchimp-picker --paths=src/main/python --specpath=pyinstaller --clean src/main/python/picker.py
