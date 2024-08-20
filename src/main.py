#import all packages
import customtkinter
from tkinter import messagebox
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


progress_var = 0
calculating_Progress = 0
followers_Progress = 0
following_Progress = 0
# original working directory
original_directory = os.getcwd()

# UI colors
first_color = "#030e23"
light_first_color = '#071633'
second_color = "#5cfa7c"
third_color = '#edfef8'
red_color = '#4A0404'


#primary variables
patient_0_ID = ''
patient_0_username = ''


# scoring system constants
raw_score = 90
scoring_factor = 1.1112

# filter constants
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
to_cancel = False

# Initialize the main window
customtkinter.set_appearance_mode('dark')
customtkinter.set_default_color_theme('dark-blue')
root = customtkinter.CTk(first_color)
root.title("XBot")
root.geometry('1050x700')
root.resizable(False, False)

login_width = 430
extractor_width = 660
entry_width = 200

 # create client
client = Client(language='en-US')



# # Define PrintRedirector class
# class DualOutput:
#     def __init__(self, widget):
#         self.widget = widget
#         self.original_stdout = sys.stdout  # Save the original standard output

#     def write(self, text):
#         self.widget.insert(customtkinter.END, text)  # Write to the Tkinter text box
#         self.widget.see(customtkinter.END)  # Auto-scroll to the end
#         self.original_stdout.write(text)  # Write to the terminal

#     def flush(self):
#         pass  # Required for Python compatibility

# Define DualOutput class for stdout and stderr
class DualOutput:
    def __init__(self, widget):
        self.widget = widget
        self.original_stdout = sys.stdout  # Save the original standard output
        self.original_stderr = sys.stderr  # Save the original standard error

    def write(self, text):
        self.widget.insert(customtkinter.END, text)  # Write to the Tkinter text box
        self.widget.see(customtkinter.END)  # Auto-scroll to the end
        word_list = ["Exception", "exception", "EXECEPTION", "Error", "error", "ERROR","Warning", "Warning", "WARNING"]
        if self.original_stdout:
            self.original_stdout.write(text)  # Write to the terminal if stdout
        if self.original_stderr and  self.includes(text, word_list):
            self.original_stderr.write(text)  # Write to the terminal if stderr

    def includes(self, string_data, list_of_words):
        return any(word in string_data for word in list_of_words)

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

def filter_profiles_by_Followers_following(user, profile_list, stage):
    global progress_var
    global followers_Progress
    global following_Progress

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
                progress_var += 1
                if stage == 'followers':
                    total = followers_Progress
                elif stage == 'following':
                    total = following_Progress
                calculate_percentage_progress(progress_var, total)

def calculate_percentage_progress(value_, total):
    if value_ > 0:
        x = int((value_/total)* 100)
        if x > 85:
            progress_text.configure(text=f"{x}%", text_color='Green')
            return
        progress_text.configure(text=f"{x}%", text_color='orange', font=('Helvetica', 30, 'bold'))


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
    global progress_var
    print_(f'\n\n{user.screen_name}: GETTING FOLLOWERS')
    
    global follower_list
    global no_of_follower_profiles
    while True:
        if to_cancel:
            return
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
                print_(f'{user.screen_name}: {no_of_follower_profiles} Follower Profiles collected')
                progress_var = 0
                
                break
        
        # add to filtered users to csv
        filter_profiles_by_Followers_following(user, follower_list, 'followers')

# retrieve user's followers in safe batches and save to csv
async def get_user_following(user):
    global progress_var
    print_(f'\n\n{user.screen_name}: GETTING FOLLOWINGS')
    global following_list
    global no_of_follower_profiles
    while True:
        if to_cancel:
            return

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
                print_(f'{user.screen_name}: {no_of_following_profiles} Following Profiles collected')

                progress_var = 0
                break
        
        # add to filtered users to csv
        filter_profiles_by_Followers_following(user, following_list, 'following')


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

def print_(obj):
    text_box.configure(state=customtkinter.NORMAL)  
    print(obj)
    text_box.configure(state=customtkinter.DISABLED)  


# Scoring Functions

# SCORING SCRIPT
# Define deduction criteria with multiple conditions
def scoring_algorithmn(df, user):
    global progress_var    
    # Add a new column with a constant value
    df['Raw_Score'] = raw_score

    df['FinalScore'] = None
    
    df['Joined_X'] = df['Joined_X'].astype(str)

    progress_var = 0

    # Apply deduction based on criteria
    df['Raw_Score'] = df.apply(apply_deduction, axis=1)

    # Apply the new scoring function
    #df['FinalScore'] = df.apply(calculate_final_score, axis=1)

    # create new dataframe containing specific columns
    final_df = df.drop(columns=
        ['Name', 'Bio','Can_DM','Location', 'Joined_X', 'Translator', 'Likes', 'Blue_Tick', 'Profile_Pic'])
    
    # change director to save file in docs    
    os.chdir('../docs')
    if isinstance(user, str):
        name = user
    else:
        name = user.screen_name
    # save and dislay final result
    final_df.to_csv(f'Profiles_{name}.csv', index=False)

    # switch back to original_directory
    os.chdir(original_directory)

    return final_df

def reset_progress():
    global progress_var
    progress_var = 0
    progress_text.configure(text='')

# final score caculation
def calculate_final_score(row):
    return scoring_factor * row['Raw_Score']

# deduction criteria
def apply_deduction(row):
    global calculating_Progress
    global progress_var


    if to_cancel:
        return

    # Suspicious keywords and regex patterns
    sus_keywords = [
    "crypto guru",
    "bitcoin millionaire",
    "NFT investor",
    "crypto airdrop",
    "blockchain expert",
    "free tokens",
    "get rich quick",
    "DM for collab",
    "giveaway",
    "earn money from home",
    "make money fast",
    "follow for follow",
    "100% legit",
    "guaranteed earnings",
    "passive income",
    "affiliate marketer",
    "join my team",
    "work from home",
    "entrepreneur",
    "business opportunity",
    "influencer",
    "brand ambassador",
    "model",
    "verified",
    "official",
    "user123456789",
    "click the link",
    "free giveaway",
    "no risk",
    "double your money",
    "instant access"
    ]

    user_regex = re.compile(r'^user\d+[a-zA-Z0-9]+$', re.IGNORECASE)

    value = row['Raw_Score']

    # Check if 'Username' contains any suspicious keywords
    username_normal = row['Username']
    username_lower = row['Username'].lower()
    if any(keyword in username_lower for keyword in sus_keywords) or any(keyword in username_normal for keyword in sus_keywords):
        value -= 10

    # Check if 'Username' matches the suspicious pattern
    if user_regex.match(row['Username']):
        value -= 10


    # Check if 'Bio' contains more than 3 emojis
    bio = row.get('Bio', '')
    if isinstance(bio, (str, bytes)):  # Check if bio is a string or bytes
        emoji_pattern = re.compile("["
                            u"\U0001F600-\U0001F64F"  # emoticons
                            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                            u"\U0001F680-\U0001F6FF"  # transport & map symbols
                            u"\U0001F700-\U0001F77F"  # alchemical symbols
                            u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                            u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                            u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                            u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                            u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                            u"\U00002702-\U000027B0"  # Dingbats
                            "]+", flags=re.UNICODE)
        if len(emoji_pattern.findall(bio)) > 3:
            value -= 5

        try:
                # Check if 'Bio' contains any suspicious keywords
                if isinstance(bio, bytes):
                    string_data = bio.decode('utf-8')
                    
                    bio_lower = string_data.lower()

                if any(keyword in bio_lower for keyword in sus_keywords) or any(keyword in bio for keyword in sus_keywords):
                    value -= 10
        except:
            pass
        
    # Check the Followers/Following ratio
    if row['Followers'] > 0:
        ratio = row['Following'] / row['Followers']
        if ratio > 10:
            value -= 10
        elif 3 <= ratio <= 10:
            value -= 5

    # Check the number of Tweets
    if row['Tweets'] < 10:
        value -= 10
    elif 10 <= row['Tweets'] < 50:
        value -= 5

    # Check if 'Can_DM' is True
    if row['Can_DM']:
        value -= 5
   
    # check location
    # Check if 'Location' is in Africa, India, or Pakistan
    africa_countries = ['Nigeria', 'South Africa', 'Egypt', 'Kenya', 'Ghana', 'Ethiopia', 'Tanzania', 'Uganda']
    asia_countries = ['India', 'Pakistan']
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = row['Location']
    try:
        location_data = geolocator.geocode(location, language='en')
        if location_data:
            country = location_data.address.split(',')[-1].strip()
            if country in africa_countries or country in asia_countries:
                value -= 5
    except Exception as e:
        # print(e)
        # print("error making location analysis")
        pass

    try:
        # Check the account age based on 'Joined_X'
        str_datetime = row['Joined_X']
#        joined_date = pd.to_datetime(str_datetime, utc=False)
        

        joined_date = str_datetime.split('+')[0]
        joined_date = datetime.strptime(joined_date, '%Y-%m-%d %H:%M:%S')

        # print(joined_date)
        age = relativedelta(datetime.now(), joined_date)
        if age.years < 1:
            if age.months < 6:
                value -= 10
            elif 6 <= age.months <= 12:
                value -= 5
    except Exception as e:
        print(e)
        print("error making date analysis")

    row['FinalScore'] = scoring_factor * row['Raw_Score']
    progress_var += 1
    calculate_percentage_progress(progress_var, calculating_Progress)

    return value

# main app functions
def start_bot():
    asyncio.run(main())

def start_bot_calculation():
    global calculating_Progress
    global to_cancel
    reset_progress()
    user_input = entry.get()
    
    calculating_Progress = count_csv_entries(user_input, 'raw')
    # Reading the CSV file into a DataFrame
    df = pd.read_csv(f'rawProfiles_{user_input}.csv')
    print_(df)

    final_df = scoring_algorithmn(df, user_input)

    print_('''

FINAL RESULTS BELOW:
''')
    print_(final_df)

    if check_if_to_stop():
        to_cancel = False
        reset_progress()
        print_('EXTRACTION ENDED')
        return

    print_('\n\nDONE.')



def RUN_(event=None):
    # Start the long-running task in a separate thread
    global thread
    checkbox_state = checkbox_var.get()

    if checkbox_state:
        thread = Thread(target=start_bot_calculation)
        thread.start()        
        return

    thread = Thread(target=start_bot)
    thread.start()

async def main():
    global followers_Progress
    global following_Progress
    global calculating_Progress
    global to_cancel
    reset_progress()
    user_input = entry.get()
    if len(user_input) < 1:
        print_("Input a Username !")
        return
    
    # get patient_0
    try:
        user =  await get_user_by_username(client, user_input)
    except:
        return
    
    followers_Progress = user.followers_count
    following_Progress = user.following_count

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
        
    if check_if_to_stop():
        to_cancel = False
        reset_progress()
        print_('EXTRACTION ENDED')
        return

    await get_user_following(user)

    
    calculating_Progress = count_csv_entries(user.screen_name, 'raw')
    # Reading the CSV file into a DataFrame
    df = pd.read_csv(f'rawProfiles_{user.screen_name}.csv')
    print_(df)

    if check_if_to_stop():
        to_cancel = False
        reset_progress()
        print_('EXTRACTION ENDED')
        return

    final_df = scoring_algorithmn(df, user)
    print_('''

FINAL RESULTS BELOW:
''')
    print_(final_df)

    print_('\n\nDONE.')


# function to generate cookies
def generate_cookies():
    username_ = login_entry.get()
    email_ = email_entry.get()
    password_ = password_entry.get()
    if len(username_) > 0 and len(email_) > 0 and len(password_) > 0:
        #login and save cookies
        try:
            asyncio.run(client.login(auth_info_1=username_, 
                                auth_info_2=email_, 
                                password=password_))
            client.save_cookies('cookies.json')

            # tells user it is done
            messagebox.showinfo("Generate Cookies", "Cookies generated!")
        except Exception as e:
            print(e)
            info_label.configure(text="Login on Browser and Try again.")
    else:
        info_label.configure(text="Input all fields")
        

# Function to handle the "Load Cookies" button click
def load_cookies_function():
    # logs into bot
    try:
        client.load_cookies('cookies.json')
        info_label.configure(text="")
        print_("Logged In !")
    except Exception as e:
        print(e)
        info_label.configure(text="Please Generate Cookies")
        return
    

def stop_thread(reset=None):
    global to_cancel
    to_cancel = True

def check_if_to_stop():
    global to_cancel
    if to_cancel:
        return True
    else:
        return False

    


login_frame = customtkinter.CTkFrame(root, fg_color=first_color, width=login_width)
login_frame.grid(column=0, row=0, padx=10)

extractor_frame = customtkinter.CTkFrame(root, fg_color=first_color, width=extractor_width)
extractor_frame.grid(column=1, row=0)

user_frame = customtkinter.CTkFrame(extractor_frame, width=extractor_width)
user_frame.grid(column=0, row=0, sticky='nsew')

log_frame = customtkinter.CTkFrame(extractor_frame, fg_color=first_color, width=extractor_width)
log_frame.grid(column=0, row=1)

# Create and place the Login Bar
login_label = customtkinter.CTkLabel(login_frame, text="Login:")
login_label.pack(pady=(10, 0))
login_entry = customtkinter.CTkEntry(login_frame, width=entry_width, justify="center", text_color=third_color, font=('Helvetica', 16, 'bold'))
login_entry.pack()

# Create and place the Email Bar
email_label = customtkinter.CTkLabel(login_frame, text="Email:")
email_label.pack(pady=(10, 0))
email_entry = customtkinter.CTkEntry(login_frame, width=entry_width, justify="center", text_color=third_color, font=('Helvetica', 16, 'bold'))
email_entry.pack()

# Create and place the Password Bar
password_label = customtkinter.CTkLabel(login_frame, text="Password:")
password_label.pack(pady=(10, 0))
password_entry = customtkinter.CTkEntry(login_frame, width=entry_width, justify="center", text_color=third_color, show="#", font=('Helvetica', 16, 'bold'))
password_entry.pack()

# Create a frame to hold the buttons
button_frame = customtkinter.CTkFrame(login_frame, width=login_width, fg_color=first_color)
button_frame.pack(pady=(10, 0))

# Create and place the Generate Cookies Button in the frame
generate_button = customtkinter.CTkButton(button_frame, text="Generate", width=100, command=generate_cookies)
generate_button.pack(side=customtkinter.LEFT, padx=(0, 10))

# Create and place the Load Cookies Button in the frame
load_button = customtkinter.CTkButton(button_frame, text="Login", width=100, command=load_cookies_function)
load_button.pack(side=customtkinter.LEFT)

info_label = customtkinter.CTkLabel(login_frame, text="", text_color='orange', font=('Helvetica', 12, 'bold'))
info_label.pack(pady=(10, 0))

progress_text = customtkinter.CTkLabel(login_frame, text="", text_color='orange', font=('Helvetica', 12, 'bold'))
progress_text.pack(pady=(180, 0))





# Input bar for typing username
label = customtkinter.CTkLabel(user_frame, text="Enter Username:", text_color=third_color,)
label.pack(pady=5)
entry = customtkinter.CTkEntry(user_frame, width=entry_width, justify="center", text_color=third_color, font=('Helvetica', 16, 'bold'))
entry.pack(pady=5)

button_frame = customtkinter.CTkFrame(user_frame, bg_color="transparent",fg_color="transparent")
button_frame.pack(pady=5)

# Button to run the main function
button = customtkinter.CTkButton(button_frame, width=120, text="Run", command=RUN_)
button.grid(column=0, row=0, padx=10)

# Button to cancel
cancel_button = customtkinter.CTkButton(button_frame, width=120, text="Cancel", fg_color='#6D1D1D', command=stop_thread, hover_color="#4A0000")
cancel_button.grid(column=1, row=0, padx=10)

checkbox_var = customtkinter.BooleanVar()
# Create a checkbox and link it to the BooleanVar
checkbox = customtkinter.CTkCheckBox(user_frame, text="Calculate from CSV", variable=checkbox_var, onvalue=True, offvalue=False)
checkbox.pack(pady=(10, 5))

# Disabled text box for output
text_box = customtkinter.CTkTextbox(log_frame, height=500, width=809, fg_color=light_first_color)
text_box.pack(pady=(10, 0))
text_box.configure(state=customtkinter.DISABLED)  # Disable editing

root.bind('<Return>', RUN_)

# Set default encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# set print log to display on app interface
sys.stdout = DualOutput(text_box)

# Start the main loop
root.mainloop()















    # # login credentials              
    # # config = ConfigParser()
    # # config.read('config.ini')
    # # username = config['X']['username']
    # # email = config['X']['email']
    # # password = config['X']['password']


    # # create client
    # client = Client(language='en-US')

    # # choose whether to login in from scratch or use cookies
    # if new_account:
    #     #login and save cookies
    #     await client.login(auth_info_1=username, 
    #                         auth_info_2=email, 
    #                         password=password)
    #     client.save_cookies('cookies.json')

    # else:
    #     load_cookies_0(client)



    # def animate_frame(frame, start_x, end_x, step):
    #     if abs(end_x - start_x) < abs(step):
    #         frame.place(x=end_x, y=0)
    #     else:
    #         frame.place(x=start_x, y=0)
    #         root.after(5, animate_frame, frame, start_x + step, end_x, step)

    # def hide_frame1(frame, start_x, end_x):
    #     animate_frame(frame, start_x, end_x, (end_x - start_x) // 30)  # Animate the frame off the screen

    # def show_frame2():
    #     hide_frame1(login_frame, 0, -400)  # Hide frame1 (move to left)
    #     root.after(300, lambda: animate_frame(extractor_frame, 50, 0, -10))  # Show frame2 (animate to original position)

    # def place_():
    #     login_wrapper.place(x=0, y=0, relx=0, rely=0, relwidth=1, relheight=1)
    #     login_frame.grid(row=0, column=0, sticky='nsew')
    #     extractor_frame.place(x=400, y=0)
    #     extractor_frame.place_forget()