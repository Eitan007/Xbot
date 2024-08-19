#import all packages
import customtkinter
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
import sys
from threading import Thread

# UI colors
first_color = "#030e23"
light_first_color = '#071633'
second_color = "#5cfa7c"
third_color = '#edfef8'
red_color = '#4A0404'


#primary variables
patient_0_ID = ''
patient_0_username = ''


# constants
raw_score = 90
scoring_factor = 1.1112
follower_count_limit = 10000
following_count_limit = 5000

# logic variables
new_account = False
ask_for_username = True
no_Results = False
user_profile_results = None
following_list = None
follower_list = None
no_of_follower_profiles = 0


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

async def search_user_0(client, query, count):
    user_profile_results = await client.search_user(query, count)
    #user_profile_results = await client.search_tweet(query,'Top', count)
    return user_profile_results

async def search_for_profile():
    query = input('Type in username: ').lower()

    user_profile_results = await search_user_0(query, 20)
    return user_profile_results, query

def append_data_to_csv(entries, name, type):
    if type == 'raw':
        with open(f'rawProfiles_{name}.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(entries)

    if type == 'fine':
        with open(f'Profiles_{name}.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(entries)

def create_CSVs(name, type):
    #create csv file for scrapped data
    if type == 'raw':
        with open(f'rawProfiles_{name}.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Name', 'Username', 'URL', 'Followers', 'Following', 'Tweets', 'Bio','Can_DM','Location', 'Joined_X', 'Translator', 'Likes', 'Blue_Tick', 'Profile_Pic'])

    if type == 'fine':
            with open(f'Profiles_{name}.csv', 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Username', 'Followers', 'Following', 'Tweets', 'URL'])

def random_wait():
    wait_time = randint(5, 10)
    print_(f'Waiting for {wait_time} seconds..')
    time.sleep(wait_time)

def count_csv_entries(name, type):
    if type == 'raw':
        with open(f'rawProfiles_{name}.csv', mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            row_count = sum(1 for row in csv_reader) - 1  
    if type == 'fine':
        with open(f'Profiles_{name}.csv', mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            row_count = sum(1 for row in csv_reader) - 1  
    return row_count

def filter_profiles_by_Followers_following(user, profile_list):
    #print_(profile_list)
    if profile_list is not None:
        if len(profile_list) > 0:
            for follower in profile_list:
                if follower.followers_count > follower_count_limit or follower.following_count > following_count_limit:
                    continue
                else:
                    follower_url = f'https://x.com/{follower.screen_name}'
                    user_data = [follower.name, follower.screen_name, follower_url, follower.followers_count, follower.following_count, follower.statuses_count, follower.description, follower.can_dm, follower.location, follower.created_at_datetime, follower.is_translator, follower.favourites_count, follower.is_blue_verified, follower.default_profile_image]
                    append_data_to_csv(user_data, user.screen_name, 'raw')

# searches for first user and gets ID
async def get_patient_0():
    global patient_0_ID
    global patient_0_username

    while ask_for_username:
        # reset search
        if no_Results:
            user_profile_results = None
            no_Results = False

        # NETWORK REQUEST
        # first results search
        if user_profile_results is None:
            # get point-zero username ID

            # sleep before making request
            random_wait()
            try:
                Results_and_query = search_for_profile()    # A REQUEST
            except TooManyRequests as e:
                limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
                print_(f'Rate limit reached - {datetime.now()}')
                print_(f'Waiting until - {limit_reset}')
                wait_time = limit_reset - datetime.now()
                time.sleep(wait_time.total_seconds())
                continue

            user_profile_results = Results_and_query[0]
            query = Results_and_query[1]
            
        # getting next page
        else:
            # if there were prev results let scheck for more results 
            if len(user_profile_results) > 0:

                # sleep before making request
                random_wait()
                try:
                    user_profile_results = await user_profile_results.next()  # A REQUEST
                except TooManyRequests as e:
                    limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
                    print_(f'Rate limit reached - {datetime.now()}')
                    print_(f'Waiting until - {limit_reset}')
                    wait_time = limit_reset - datetime.now()
                    time.sleep(wait_time.total_seconds())
                    continue

        # POST NETWORK REQUEST
        if len(user_profile_results) > 0:
            for user in user_profile_results:
                # check if username matches with user found in search then get id
                screen_name = user.screen_name

                if query == screen_name:
                    patient_0_ID = user.id
                    patient_0_username = user.screen_name
                    # after finding user, stop asking operator for username
                    ask_for_username = False
                    print_(f'{query}: USER PROFILE FOUND')
                    print_(patient_0_ID)
                    print_(patient_0_username)
                    print_(vars(user))

                    #create csv to store raw data
                    create_CSVs(query, 'raw')
                    break
            if ask_for_username:
                print_(f"{query}: results don't match username")
                print_(f"{query}: getting next results page")

        else:
            no_Results = True
            print_(f"{query}: PROFILE NOT FOUND")
            print_(f"{query}: TRY ANOTHER USERNAME")

# retrieve user's followers in safe batches and save to csv
async def get_user_follower(user):
    print_(f'{user.screen_name}: GETTING FOLLOWERS')
    global follower_list
    global no_of_follower_profiles
    while True:
        # NETWORK REQUEST
        # first results search
        if follower_list is None:
            # sleep before making request
            random_wait()
            try:
                follower_list = await user.get_followers() # REQUEST
            except TooManyRequests as e:
                limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
                print_(f'Rate limit reached - {datetime.now()}')
                print_(f'Waiting until - {limit_reset}')
                wait_time = limit_reset - datetime.now()
                time.sleep(wait_time.total_seconds())
                continue

        # getting next page
        else:
            # check if previous search results had users
            if len(follower_list) > 0:
                # try getting next results
                random_wait()
                try:
                    print_(f'{user.screen_name}: retrieving next batch of profiles')
                    follower_list = await follower_list.next() # REQUEST
                except TooManyRequests as e:
                    limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
                    print_(f'Rate limit reached - {datetime.now()}')
                    print_(f'Waiting until - {limit_reset}')
                    wait_time = limit_reset - datetime.now()
                    time.sleep(wait_time.total_seconds())
                    continue

            # if there are no more users
            else:
                no_of_follower_profiles = count_csv_entries(user.screen_name, 'raw')
                print_(f'{user.screen_name}: {no_of_follower_profiles} Profiles collected')
                break
        
        # add to filtered users to csv
        filter_profiles_by_Followers_following(user, follower_list)

# retrieve user's followers in safe batches and save to csv
async def get_user_following(user):
    print_(f'{user.screen_name}: GETTING FOLLOWINGS')
    global following_list
    global no_of_follower_profiles
    while True:
        # NETWORK REQUEST
        # first results search
        if following_list is None:
            # sleep before making request
            random_wait()
            try:
                following_list = await user.get_following() # REQUEST
            except TooManyRequests as e:
                limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
                print_(f'Rate limit reached - {datetime.now()}')
                print_(f'Waiting until - {limit_reset}')
                wait_time = limit_reset - datetime.now()
                time.sleep(wait_time.total_seconds())
                continue

        # getting next page
        else:
            # check if previous search results had users
            if len(following_list) > 0:
                # try getting next results
                random_wait()
                try:
                    print_(f'{user.screen_name}: retrieving next batch of profiles')
                    following_list = await following_list.next() # REQUEST
                except TooManyRequests as e:
                    limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
                    print_(f'Rate limit reached - {datetime.now()}')
                    print_(f'Waiting until - {limit_reset}')
                    wait_time = limit_reset - datetime.now()
                    time.sleep(wait_time.total_seconds())
                    continue

            # if there are no more users
            else:
                no_of_all_profiles = count_csv_entries(user.screen_name, 'raw')
                no_of_following_profiles = no_of_all_profiles - no_of_follower_profiles 
                print_(f'{user.screen_name}: {no_of_following_profiles} Profiles collected')
                break
        
        # add to filtered users to csv
        filter_profiles_by_Followers_following(user, following_list)


async def get_user_by_username_old(client, username):
    random_wait()
    print_('getting username')
    try:
        user = await client.get_user_by_screen_name(username) # REQUEST
    except TooManyRequests as e:
                limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
                print_(f'Rate limit reached - {datetime.now()}')
                print_(f'Waiting until - {limit_reset}')
                wait_time = limit_reset - datetime.now()
                time.sleep(wait_time.total_seconds())
                get_user_by_username(client, username)
    except:
        print_("didn't work chief")

    return user


async def get_user_by_username(client, username, max_retries=5):
    retry_count = 0

    while retry_count < max_retries:
        try:
            user = await client.get_user_by_screen_name(username)  # REQUEST
            return user
        except TooManyRequests as e:
            limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
            print_(f'Rate limit reached - {datetime.now()}')
            print_(f'Waiting until - {limit_reset}')
            wait_time = (limit_reset - datetime.now()).total_seconds()
            time.sleep(wait_time)  # Use asyncio.sleep() for asynchronous delay
            retry_count += 1
        except Exception as e:
            print_(f"Error occurred: {e}")
            # You can choose to retry or break based on the exception type
            retry_count += 1  # Increment retry count for non-rate limit errors
    # If maximum retries are exhausted
    print_("Max retries reached, request failed.")
    raise("Trouble Getting User Profile")

async def main():

    # login credentials              
    config = ConfigParser()
    config.read('config.ini')
    username = config['X']['username']
    email = config['X']['email']
    password = config['X']['password']


    # create client
    client = Client(language='en-US')

    # choose whether to login in from scratch or use cookies
    if new_account:
        #login and save cookies
        await client.login(auth_info_1=username, 
                            auth_info_2=email, 
                            password=password)
        client.save_cookies('cookies.json')

    else:
        load_cookies_0(client)

    user_input = entry.get()

    if len(user_input) < 0:
        print_("Input a Username !")
        return
    
    # get patient_0
    try:
        user =  await get_user_by_username(client, user_input)
    except:
        return
    
    print_(f'''
USERNAME: {user.screen_name}
DISPLAY NAME: {user.name}
BIO: {user.description}
FOLLOWERS: {user.followers_count}
FOLLOWING: {user.following_count}
DATE JOINED: {user.created_at_datetime}
''')
    # create csv to save raw data
    create_CSVs(user.screen_name, 'raw')

    #print_(vars(user))

    await get_user_follower(user)

    await get_user_following(user)

    # Reading the CSV file into a DataFrame
    df = pd.read_csv(f'rawProfiles_{user.screen_name}.csv')

    print_(df)

def start_bot():
    asyncio.run(main())

def RUN_():
    # Start the long-running task in a separate thread
    thread = Thread(target=start_bot)
    thread.start()

def print_(string):
    text_box.configure(state=customtkinter.NORMAL)  
    print(string)
    text_box.configure(state=customtkinter.DISABLED)  


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
button = customtkinter.CTkButton(root, text="Run", command=RUN_)
button.pack(pady=5)

# Disabled text box for output
text_box = customtkinter.CTkTextbox(root, height=550, width=800, fg_color=light_first_color)
text_box.pack(pady=10)
text_box.configure(state=customtkinter.DISABLED)  # Disable editing

# Set default encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# set print log to display on app interface
sys.stdout = DualOutput(text_box)

# Start the main loop
root.mainloop()
















# # SCORING SCRIPT
# # Define deduction criteria with multiple conditions
# def scoring_algorithmn():
#     # deduction criteria
#     def apply_deduction(row):
#         # Suspicious keywords and regex patterns
#         sus_keywords = ['john doe', 'samuel', 'ctrader']
#         user_regex = re.compile(r'^user\d+[a-zA-Z0-9]+$', re.IGNORECASE)

#         value = row['Raw_Score']

#         # Check if 'Username' contains any suspicious keywords
#         username_lower = row['Username'].lower()
#         if any(keyword in username_lower for keyword in sus_keywords):
#             value -= 10

#         # Check if 'Username' matches the suspicious pattern
#         if user_regex.match(row['Username']):
#             value -= 10

#         # Check if 'Bio' contains more than 3 emojis
#         emoji_pattern = re.compile("["
#                             u"\U0001F600-\U0001F64F"  # emoticons
#                             u"\U0001F300-\U0001F5FF"  # symbols & pictographs
#                             u"\U0001F680-\U0001F6FF"  # transport & map symbols
#                             u"\U0001F700-\U0001F77F"  # alchemical symbols
#                             u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
#                             u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
#                             u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
#                             u"\U0001FA00-\U0001FA6F"  # Chess Symbols
#                             u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
#                             u"\U00002702-\U000027B0"  # Dingbats
#                             "]+", flags=re.UNICODE)
#         if len(emoji_pattern.findall(row['Bio'])) > 3:
#             value -= 5

#         # Check if 'Bio' contains any suspicious keywords
#         bio_lower = row['Bio'].lower()
#         if any(keyword in bio_lower for keyword in sus_keywords):
#             value -= 10

#         # Check the Followers/Following ratio
#         if row['Followers'] > 0:
#             ratio = row['Following'] / row['Followers']
#             if ratio > 10:
#                 value -= 10
#             elif 3 <= ratio <= 10:
#                 value -= 5

#         # Check the number of Tweets
#         if row['Tweets'] < 10:
#             value -= 10
#         elif 10 <= row['Tweets'] < 50:
#             value -= 5

#         # Check if 'Can_DM' is True
#         if row['Can_DM']:
#             value -= 5

#         # Check the account age based on 'Joined_X'
#         joined_date = pd.to_datetime(row['Joined_X'])
#         age = relativedelta(datetime.now(), joined_date)
#         if age.years < 1:
#             if age.months < 6:
#                 value -= 10
#             elif 6 <= age.months <= 12:
#                 value -= 5

#         # Check if 'Location' is in Africa, India, or Pakistan
#         africa_countries = ['Nigeria', 'South Africa', 'Egypt', 'Kenya', 'Ghana', 'Ethiopia', 'Tanzania', 'Uganda']
#         asia_countries = ['India', 'Pakistan']

#         geolocator = Nominatim(user_agent="geoapiExercises")
#         location = row['Location']
#         try:
#             location_data = geolocator.geocode(location, language='en')
#             if location_data:
#                 country = location_data.address.split(',')[-1].strip()
#                 if country in africa_countries or country in asia_countries:
#                     value -= 5
#         except:
#             pass  # Ignore any errors in geolocation

#         return value

#     # Define a new scoring function
#     def calculate_final_score(row):
#         return scoring_factor * row['Raw_Score']

#     # Reading the CSV file into a DataFrame
#     df = pd.read_csv(f'rawProfiles_{patient_0_username}.csv')

#     # Add a new column with a constant value
#     df['Raw_Score'] = raw_score

#     # Apply deduction based on criteria
#     df['Raw_Score'] = df.apply(apply_deduction, axis=1)

#     # Apply the new scoring function
#     df['FinalScore'] = df.apply(calculate_final_score, axis=1)

#     #print_(df)
