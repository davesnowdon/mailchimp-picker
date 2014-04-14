#! /bin/bash
pyinstaller --onedir --name mailchimp-picker --paths=src/main/python --specpath=pyinstaller --clean src/main/python/recorder/picker.py
