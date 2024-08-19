#import all packages
import customtkinter
import sys
from twikit import Client, TooManyRequests
import asyncio
import time
from datetime import datetime
import csv
from configparser import ConfigParser
from random import randint
import pandas as pd
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
from geopy.geocoders import Nominatim
import os


first_color = "#030e23"
light_first_color = '#071633'
second_color = "#5cfa7c"
third_color = '#edfef8'
red_color = '#4A0404'


raw_score = 90
scoring_factor = 1.1112
follower_count_limit = 10000
following_count_limit = 5000
ask_for_username = True
patient_0_ID = ''
patient_0_username = ''
user_profile_results = None
no_Results = False

# Define PrintRedirector class
class DualOutput:
    def __init__(self, widget):
        self.widget = widget
        self.original_stdout = sys.stdout  # Save the original standard output

    def write(self, text):
        self.widget.insert(customtkinter.END, text)  # Write to the Tkinter text box
        self.widget.see(customtkinter.END)  # Auto-scroll to the end
        self.original_stdout.write(text)  # Write to the terminal

    def flush(self):
        pass  # Required for Python compatibility


def search_user():
    text_box.configure(state=customtkinter.NORMAL)  
    print('string')
    text_box.configure(state=customtkinter.DISABLED)  


# Main function to run the asynchronous code
async def login_save_cookies(client, username, email, password):
    client = await login_user(client, username, email, password)
    save_cookies_0(client)

# Define your async function
async def login_user(client, username, email, password):
    await client.login(auth_info_1=username, 
                       auth_info_2=email, 
                       password=password)
    return client

# Define the function to handle saving cookies
def save_cookies_0(client, filename='cookies.json'):
    # Assuming client.save_cookies is an async function
    client.save_cookies(filename)

def load_cookies_0(client, filename='cookies.json'):
    client.load_cookies(filename)

async def search_user_0(query, count):
    user_profile_results = await client.search_user(query, count)
    #user_profile_results = await client.search_tweet(query,'Top', count)
    return user_profile_results

def search_for_profile():
    query = input('Type in username: ').lower()

    user_profile_results = asyncio.run(search_user_0(query, 20))
    return user_profile_results, query

def append_data_to_csv(entries, name, type):
    if type is 'raw':
        with open(f'rawProfiles_{name}.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(entries)

    if type is 'fine':
        with open(f'Profiles_{name}.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(entries)

def create_CSVs(name, type):
    #create csv file for scrapped data
    if type is 'raw':
        with open(f'rawProfiles_{name}.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Name', 'Username', 'URL', 'Followers', 'Following', 'Tweets', 'Can_DM','Location', 'Joined_X', 'Translator', 'Likes', 'Blue_Tick', 'Profile_Pic'])

    if type is 'fine':
            with open(f'Profiles_{name}.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Username', 'Followers', 'Following', 'Tweets', 'URL'])

def random_wait():
    wait_time = randint(5, 10)
    print(f'Waiting for {wait_time} seconds..')
    time.sleep(wait_time)

def filter_profiles_by_Followers_following(profile_list):
    if len(profile_list) > 0:
        for follower in profile_list:
            if follower.followers_count > follower_count_limit or follower.following_count > following_count_limit:
                continue
            else:
                follower_url = f'https://x.com/{follower.screen_name}'
                user_data = [follower.name, follower.screen_name, follower_url, follower.followers_count, follower.following_count, follower.statuses_count, follower.can_dm, follower.location, follower.created_at, follower.is_translator, follower.favourites_count, follower.is_blue_verified, follower.default_profile_image]
                append_data_to_csv(user_data, patient_0_username, 'raw')

def count_csv_entries(name, type):
    if type is 'raw':
        with open(f'rawProfiles_{name}', mode='r') as file:
            csv_reader = csv.reader(file)
            row_count = sum(1 for row in csv_reader) - 1  
    if type is 'fine':
        with open(f'Profiles_{name}', mode='r') as file:
            csv_reader = csv.reader(file)
            row_count = sum(1 for row in csv_reader) - 1  
    return row_count

# Initialize the main window
customtkinter.set_appearance_mode('dark')
customtkinter.set_default_color_theme('dark-blue')
root = customtkinter.CTk(first_color)
root.title("XBot")
root.geometry('900x700')

# Input bar for typing username
label = customtkinter.CTkLabel(root, text="Enter Username:", text_color=third_color,)
label.pack(pady=5)
entry = customtkinter.CTkEntry(root, width=300, justify="center", text_color=third_color, font=('Helvetica', 16, 'bold'))
entry.pack(pady=5)

# Button to run the main function
button = customtkinter.CTkButton(root, text="Run", command=search_user)
button.pack(pady=5)

# Disabled text box for output
text_box = customtkinter.CTkTextbox(root, height=550, width=800, fg_color=light_first_color)
text_box.pack(pady=10)
text_box.configure(state=customtkinter.DISABLED)  # Disable editing

sys.stdout = DualOutput(text_box)

# Start the main loop
root.mainloop()