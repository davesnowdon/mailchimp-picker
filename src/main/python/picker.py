'''
Created on 28 Mar 2014

@author: davesnowdon
'''

import urllib2
import json
import collections
import random
import os

import mailchimp

import kivy
kivy.require('1.7.1')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.properties import ListProperty
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.config import Config
from kivy.logger import Logger

# Requirements
# - select list member at random [DONE]
# - once list member approved, set tag on mailshimp
# - update selection to not choose list members with 'monthlywinner' tag

KEY_FILE = '~/.mailchimp.key'

HDR_EMAIL = "Email Address"
HDR_FIRST_NAME = "First Name"
HDR_LAST_NAME = "Last Name"
HDR_LAST_PHONE = "Phone"

ListMember = collections.namedtuple('ListMember',
                                   ['email', 'first_name', 'last_name', 'phone'])

def get_mailchimp_api(key):
    return mailchimp.Mailchimp(key)

def get_lists(api):
    my_lists = api.lists.list()
    list_name_id = {}
    for l in my_lists['data']:
        list_name_id[l['name']] = l['id']
    return list_name_id

def get_list_members(key, list_id):
    '''
    Use the export API to get all the members of a list
    '''
    url = 'http://us1.api.mailchimp.com/export/1.0/list?apikey={}&id={}'.format(key, list_id)
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    the_list = response.read()
    lines = the_list.splitlines()
    fields = json.loads(lines[0])
    Logger.debug("fields = {}".format(fields))
    index_email = -1
    index_first_name = -1
    index_last_name = -1
    index_phone = -1

    for i, v in enumerate(fields):
        if v == HDR_EMAIL:
            index_email = i
        elif v == HDR_FIRST_NAME:
            index_first_name = i
        elif v == HDR_LAST_NAME:
            index_last_name = i
        elif v == HDR_LAST_PHONE:
            index_phone = i

    if index_email == -1 or index_first_name == -1 or index_last_name == -1:
        Logger.error("Error could not locate headers for list")
        return None

    data = lines[1:]
    result = []
    for l in data:
        j = json.loads(l)
        this_phone = j[index_phone] if index_phone != -1 else ''
        result.append(ListMember(first_name=j[index_first_name], last_name=j[index_last_name],
                                 email=j[index_email], phone=this_phone))
    return result

def read_api_key():
    try:
        with open(os.path.expanduser(KEY_FILE), 'r') as key_file:
            key = key_file.read()
            return key.strip()
    except IOError:
        pass
    return None

def write_api_key(key):
    with open(os.path.expanduser(KEY_FILE), 'w+') as key_file:
        key_file.write(key)

def check_key(key):
    if not key:
        return False
    api = get_mailchimp_api(key)
    try:
        api.helper.ping()
        return True
    except mailchimp.Error:
        Logger.debug("Invalid API key")
        return False


class ApiKeyDialog(Popup):
    pass

class MailchimpListPicker(Widget):
    w_mailinglists = ObjectProperty(None)
    w_firstname = ObjectProperty(None)
    w_lastname = ObjectProperty(None)
    w_email = ObjectProperty(None)
    w_phone = ObjectProperty(None)

class MailchimpListPickerApp(App):

    def build(self):
        self.list_members = None
        self.picker_ui = MailchimpListPicker()
        return self.picker_ui

    def on_start(self):
        if self.picker_ui.w_mailinglists:
            self.picker_ui.w_mailinglists.bind(text=self.on_list_selection)

        if self.picker_ui.w_pickanother:
            self.picker_ui.w_pickanother.bind(on_press=self.on_pick_another)
        key = read_api_key()
        if self.verify_key(key):
            self.on_valid_key()

    def on_stop(self):
        # shutdown
        pass

    def on_list_selection(self, instance, list_name):
        Logger.info("List selected = {}".format(list_name))
        self.selected_list_name = list_name
        self.selected_list_id = self.lists[list_name]
        self.list_members = get_list_members(self.api_key, self.selected_list_id)
        if self.list_members:
            self.pick_winner()

    def on_pick_another(self, instance):
        if self.list_members:
            self.pick_winner()

    def show_key_dialog(self):
        p = ApiKeyDialog()
        p.bind(on_dismiss=self.do_key_entered)
        p.open()

    def do_key_entered(self, popup):
        key = popup.f_key.text
        if self.verify_key(key):
            self.on_valid_key()

    def verify_key(self, key):
        if not check_key(key):
            self.show_key_dialog()
            return False
        else:
            self.api_key = key
            self.api = get_mailchimp_api(key)
            write_api_key(key)
            return True

    def on_valid_key(self):
        # build list selection
        if self.picker_ui.w_mailinglists:
            self.lists = get_lists(self.api)
            self.picker_ui.w_mailinglists.values = self.lists.keys()

    def pick_winner(self):
        winner = random.choice(self.list_members)
        Logger.info("winner = {}".format(winner))
        self.picker_ui.w_firstname.text = winner.first_name
        self.picker_ui.w_lastname.text = winner.last_name
        self.picker_ui.w_email.text = winner.email
        self.picker_ui.w_phone.text = winner.phone

    def _make_child_dict(self):
        return {c.kvid : c for c in self.root.children[0].children if c.kvid}

if __name__ == '__main__':
    Config.set('graphics', 'width', '400')
    Config.set('graphics', 'height', '400')
    MailchimpListPickerApp().run()
