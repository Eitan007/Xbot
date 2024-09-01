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
import requests
import sys
from threading import Thread
import subprocess




# original working directory
original_directory = os.getcwd()

# UI variables
progress_var = 0
calculating_Progress = 0
followers_Progress = 0
following_Progress = 0
login_width = 430
extractor_width = 660
entry_width = 200

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

# main function logic variables
new_account = False
ask_for_username = True
no_Results = False
user_profile_results = None
following_list = None
follower_list = None
no_of_follower_profiles = 0
use_cursor = False
to_cancel = False

# Initialize the main window
customtkinter.set_appearance_mode('dark')
customtkinter.set_default_color_theme('dark-blue')
root = customtkinter.CTk(first_color)
root.title("XBot")
root.geometry('1050x700')
root.resizable(False, False)

#multiple client usernames and password
clients_details = []
clients_cookies = []

#find out how save cookies works and use it to save multiple cookies in one file.

def append_to_client_list():
    username_ = login_entry.get()
    email_ = email_entry.get()
    password_ = password_entry.get()

    if len(username_) > 0 and len(email_) > 0 and len(password_) > 0:
        # arrange as list and append
        details = [username_, email_, password_]
        clients_details.append(details)

        # clear texts
        info_label.configure(text="")
        login_entry.delete(0,customtkinter.END)
        email_entry.delete(0,customtkinter.END)
        password_entry.delete(0,customtkinter.END)

        # tells user it is done
        messagebox.showinfo("Add Account", "Account Added!")
    else:
        info_label.configure(text="Input all fields")

def random_cookie_picker():
    num = randint(0,len())


#create multiple clients
async def create_client( details):
    # create multiple clients
    client_num = 0
    for details in clients_details:
        client = Client(language='en-US')
        client = await login_user(client, details[0], details[1], details[2])
        client.save_cookies(f'cookies_{client_num}.json')
        client_num += 1
        

##################################################################################################################

#   CLIENT AUTHENTICATION   #########################

# Login and save cookies
async def login_save_cookies(client, username, email, password):
    client = await login_user(client, username, email, password)
    save_cookies_0(client)

# Define login function
async def login_user(client, username, email, password):
    await client.login(auth_info_1=username, 
                       auth_info_2=email, 
                       password=password)
    return client

# generate cookies function 
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

# Saving cookies function
def save_cookies_0(client, filename='cookies.json'):
    # Assuming client.save_cookies is an async function
    client.save_cookies(filename)

# Load Cookies function
def load_cookies_function():
    # logs into bot
    try:
        client.load_cookies('cookies.json')
    
        info_label.configure(text="")
        login_entry.delete(0,customtkinter.END)
        email_entry.delete(0,customtkinter.END)
        password_entry.delete(0,customtkinter.END)

        test = asyncio.run(client.search_tweet('chatgpt','Top'))
        
        print_("Logged In !")
    except Exception as e:
        print(e)
        info_label.configure(text="Please Generate Cookies")
        return


##################################################################################################################

#   BOT BASE OPERATIONS   #########################

# refreshes the software
def restart_app():
    # Restart the current script
    python = sys.executable
    os.execv(python, [python] + sys.argv)

# DualOutput class for stdout and stderr
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

# software pause function
def random_wait():
    wait_time = randint(4,7)
    print_(f'Waiting for {wait_time} seconds..')
    time.sleep(wait_time)

# software output function
def print_(obj):
    text_box.configure(state=customtkinter.NORMAL)  
    print(obj)
    text_box.configure(state=customtkinter.DISABLED)  

# progress update
def calculate_percentage_progress(value_, total):
    if value_ > 0:
        x = int((value_/total)* 100)
        if x > 85:
            progress_text.configure(text=f"{x}%", text_color='Green')
            return
        progress_text.configure(text=f"{x}%", text_color='orange', font=('Helvetica', 30, 'bold'))

# progress reset
def reset_progress():
    global progress_var
    progress_var = 0
    progress_text.configure(text='')


##################################################################################################################

#   STORAGE OPERATIONS   #########################

# create a CSV file
def create_CSVs(name, type):
    #create csv file for scrapped data

    # Define the base directories
    if type == 'raw':
        base_dir = os.getcwd()  # Gets the current working directory
        directory = os.path.join(base_dir, 'RawFiles')

    elif type == 'fine':
        os.chdir('../docs')
        with open(f'Profiles_{name}.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Username', 'Followers', 'Following', 'Tweets', 'URL'])
        os.chdir(original_directory)
        return

    else:
        raise ValueError("Invalid type. Must be 'followers' or 'following'.")

    # Construct the file path
    file_path = os.path.join(directory, f'rawProfiles_{name}.csv')

    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)

    with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Name', 'Username', 'URL', 'Followers', 'Following', 'Tweets', 'Bio','Can_DM','Location', 'Joined_X', 'Translator', 'Likes', 'Blue_Tick', 'Profile_Pic'])

# add to an existing CSV file
def append_data_to_csv(entries, name, type):
    if type == 'raw':
        with open(f'rawProfiles_{name}.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(entries)

    if type == 'fine':
        with open(f'Profiles_{name}.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(entries)

# count items in a CSV file
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

# save checkpoint
def save_cursor(cursor, name, type):
    # Define the base directories
    base_dir = os.getcwd()  # Gets the current working directory
    if type == 'followers':
        directory = os.path.join(base_dir, 'followers')
    elif type == 'following':
        directory = os.path.join(base_dir, 'following')
    else:
        raise ValueError("Invalid type. Must be 'followers' or 'following'.")

    # Construct the file path
    file_path = os.path.join(directory, f'next_button_{name}.txt')

    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)

    # Write the cursor to the file
    try:
        with open(file_path, 'w') as f:
            f.write(cursor)
    except Exception as e:
        print(f"An error occurred while writing the file: {e}")

# load checkpoint
def load_cursor(name, type):
    # Define the base directories
    base_dir = os.getcwd()  # Gets the current working directory
    if type == 'followers':
        directory = os.path.join(base_dir, 'followers')
    elif type == 'following':
        directory = os.path.join(base_dir, 'following')
    else:
        raise ValueError("Invalid type. Must be 'followers' or 'following'.")

    # Construct the file path
    file_path = os.path.join(directory, f'next_button_{name}.txt')

    # Ensure the directory exists
    if not os.path.exists(file_path):
        # print(f"Directory does not exist: {directory}")
        return None

    with open(file_path, 'r') as f:
        return f.read().strip()

# delete checkpoint
def clear_cursor(name, type):

    # Define the base directories
    base_dir = os.getcwd()  # Gets the current working directory
    if type == 'followers':
        directory = os.path.join(base_dir, 'followers')
    elif type == 'following':
        directory = os.path.join(base_dir, 'following')
    else:
        raise ValueError("Invalid type. Must be 'followers' or 'following'.")

    # Construct the file path
    file_path = os.path.join(directory, f'next_button_{name}.txt')

    # Ensure the directory exists
    if not os.path.exists(directory):
        # print(f"Directory does not exist: {directory}")
        return

    # Delete the file
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"An error occurred while deleting checkpoint file ({file_path}), try deleting manually: {e}")


##################################################################################################################

#   SCORING ALGORITHMN FUNCTIONS   #########################

# Scoring Function
def scoring_algorithmn(df, user):
    global progress_var    
    # Add a new column with a constant value
    df['Raw_Score'] = raw_score

    # df['FinalScore'] = None
    
    df['Joined_X'] = df['Joined_X'].astype(str)

    progress_var = 0

    # Apply deduction based on criteria
    df['Raw_Score'] = df.apply(apply_deduction, axis=1)

    # Apply the new scoring function
    df['FinalScore'] = df.apply(calculate_final_score, axis=1)

    
    # create new dataframe containing specific columns
    final_df = df.drop(columns=
        ['Name', 'Bio','Can_DM','Location', 'Joined_X', 'Translator', 'Likes', 'Blue_Tick', 'Profile_Pic'])
    
    # arrange in descending order of Final score
    final_df = final_df.sort_values(by='FinalScore', ascending=False)


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

    progress_text.configure(text="DONE", text_color='green', font=('Helvetica', 30, 'bold'))

    return final_df


def run_calculation(xlsx_file_path, output_file_path):
    # if calculation_type is 0: use default model below
    try:
        # default model
        subprocess.run(["./score.exe", xlsx_file_path, output_file_path], check=True)

        print_('''

            FINAL RESULTS BELOW:
        ''')

        final_df = pd.read_csv(f'Profiles_{user.screen_name}.csv')

        print_(final_df)

        print_('\n\nDONE.')

    except Exception as e:
        print_(e)
    # elif calculation_type is 1:   load model via index


# filters out large accounts
def filter_profiles_by_size(user, profile_list, stage):
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

    # row['FinalScore'] = scoring_factor * row['Raw_Score']
    progress_var += 1
    calculate_percentage_progress(progress_var, calculating_Progress)

    return value

# final score caculation
def calculate_final_score(row):
    return round(scoring_factor * row['Raw_Score'])


def set_columns(df):
    '''
    sets each column to their correct format
    '''

    df['Name'] = df['Name'].astype(str)
    df['Username'] = df['Username'].astype(str)
    df['URL'] = df['URL'].astype(str)
    df['Followers'] = df['Followers'].astype(int)
    df['Following'] = df['Following'].astype(int)
    df['Tweets'] = df['Tweets'].astype(int)
    df['Bio'] = df['Bio'].astype(str)
    df['Can_DM'] = df['Can_DM'].astype(bool)
    df['Location'] = df['Location'].astype(str)
    df['Joined_X'] = df['Joined_X'].astype(str)
    df['Translator'] = df['Translator'].astype(bool)
    df['Likes'] = df['Likes'].astype(int)
    df['Blue_Tick'] = df['Blue_Tick'].astype(bool)
    df['Profile_Pic'] = df['Profile_Pic'].astype(bool)



##################################################################################################################

#   EXECUTION FUCNTIONS   #########################

# frontline execution (from the button's end, to initiate execution)
def RUN_(event=None):
    # Start the long-running task in a separate thread
    global thread
    global use_cursor
    checkbox_state = checkbox_var.get()
    checkpoint_state = checkpoint_var.get()

    if checkbox_state and checkpoint_state:
        print_("Uncheck one check box !")
        return

    if checkbox_state:
        thread = Thread(target=start_bot_calculation)
        thread.start()        
        return
    
    if checkpoint_state:
        use_cursor = True
    else:
        use_cursor = False

    thread = Thread(target=start_bot)
    thread.start()

#defines the enviroment variables
def define():
    # get UID
    params = {'id': UID}

    for tries in range(5):
        try:    
            # send request to api
            response = requests.get('http://localhost:5000/get-script', params=params)

            if response.status_code == 200:
                script = response.json()['hash']

                # save to file
                with open('hash.py', 'w') as file:
                    file.write(script)

                # import the hash
                sys.dont_write_bytecode = True
                import hash
                sys.dont_write_bytecode = False
                return
        except:
            pass

# middleline execution (to start from the beginning)
def start_bot():
    asyncio.run(main())

# middleline execution (to start scoring an available CSV)
def start_bot_calculation():
    global calculating_Progress
    global to_cancel
    reset_progress()
    user_input = entry.get()
    user_input = user_input.lower()
    
    # calculating_Progress = count_csv_entries(user_input, 'raw')
    
    # Step 2: Call the C++ program to perform scoring
    xlsx_file_path = f'rawProfiles_{user_input}.xlsx'
    output_file_path = f'Profiles_{user_input}.csv'
    
    try:
        subprocess.run(["./score.exe", xlsx_file_path, output_file_path], check=True)

        print_('''

            FINAL RESULTS BELOW:
        ''')

        final_df = pd.read_csv(f'Profiles_{user.screen_name}.csv')

        print_(final_df)

        print_('\n\nDONE.')
    except Exception as e:
        print_(e)
        
# backline execution (main execution flow)
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

    # calculating_Progress = count_csv_entries(user.screen_name, 'raw')
    
    # Reading the CSV file into a DataFrame
    df = pd.read_csv(f'rawProfiles_{user.screen_name}.csv')

    #set column datatype
    set_columns(df)

    # Save the DataFrame to an Excel file
    df.to_excel(f'rawProfiles_{user.screen_name}.xlsx', index=False, engine='openpyxl')

    print_(df)

    # Step 2: Call the C++ program to perform scoring
    xlsx_file_path = f'rawProfiles_{user.screen_name}.xlsx'
    output_file_path = f'Profiles_{user.screen_name}.csv'
    
    run_calculation(xlsx_file_path, output_file_path)
    
# frontline termination (from the button's end, to terminate on-going execution)
def stop_thread(reset=None):
    global to_cancel
    to_cancel = True

# backline termination (confirms from frontline, then terminates on-going execution)
def check_if_to_stop():
    global to_cancel
    if to_cancel:
        return True
    else:
        return False


##################################################################################################################

#   USER INTERFACE LOOP   #########################

#   LOGIN INTERFACE   ########
# frame for generating cookies UI
login_frame = customtkinter.CTkFrame(root, fg_color=first_color, width=login_width)
login_frame.grid(column=0, row=0, padx=10)

# Create and place the Login Bar in the login_frame
login_label = customtkinter.CTkLabel(login_frame, text="Login:")
login_label.pack(pady=(10, 0))
login_entry = customtkinter.CTkEntry(login_frame, width=entry_width, justify="center", text_color=third_color, font=('Helvetica', 16, 'bold'))
login_entry.pack()

# Create and place the Email Bar in the login_frame
email_label = customtkinter.CTkLabel(login_frame, text="Email:")
email_label.pack(pady=(10, 0))
email_entry = customtkinter.CTkEntry(login_frame, width=entry_width, justify="center", text_color=third_color, font=('Helvetica', 16, 'bold'))
email_entry.pack()

# Create and place the Password Bar in the login_frame
password_label = customtkinter.CTkLabel(login_frame, text="Password:")
password_label.pack(pady=(10, 0))
password_entry = customtkinter.CTkEntry(login_frame, width=entry_width, justify="center", text_color=third_color, show="#", font=('Helvetica', 16, 'bold'))
password_entry.pack()

# Create a frame to hold the buttons
button_frame = customtkinter.CTkFrame(login_frame, width=login_width, fg_color=first_color)
button_frame.pack(pady=(10, 0))

# Create and place the Generate Cookies Button in the button_frame
generate_button = customtkinter.CTkButton(button_frame, text="Add", width=100, command=append_to_client_list)
generate_button.pack(side=customtkinter.LEFT, padx=(0, 10))

# Create and place the Load Cookies Button in the button_frame
load_button = customtkinter.CTkButton(button_frame, text="Login", width=100, command=load_cookies_function)
load_button.pack(side=customtkinter.LEFT)

# create and place the info_text in the login_frame
info_label = customtkinter.CTkLabel(login_frame, text="", text_color='orange', font=('Helvetica', 12, 'bold'))
info_label.pack(pady=(10, 0))

# create and place the progress_text in the login_frame
progress_text = customtkinter.CTkLabel(login_frame, text="", text_color='orange', font=('Helvetica', 12, 'bold'))
progress_text.pack(pady=(180, 0))



#   EXTRACTION INTERFACE   ########
# frame for extraction tool
extractor_frame = customtkinter.CTkFrame(root, fg_color=first_color, width=extractor_width)
extractor_frame.grid(column=1, row=0)

###############
# frame for username input and other parameters
user_frame = customtkinter.CTkFrame(extractor_frame, width=extractor_width)
user_frame.grid(column=0, row=0, sticky='nsew')

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

# Button to restart
restart_button = customtkinter.CTkButton(button_frame, width=120, text="Restart", fg_color='#6D1D1D', command=restart_app, hover_color="#4A0000") 
restart_button.grid(column=3, row=0, padx=10)

check_frame = customtkinter.CTkFrame(user_frame, bg_color="transparent",fg_color="transparent")
check_frame.pack(pady=(20))

checkpoint_var = customtkinter.BooleanVar()
# Create a checkbox and link it to the BooleanVar
checkpoint = customtkinter.CTkCheckBox(check_frame, text="start from checkpoint", variable=checkpoint_var, onvalue=True, offvalue=False)
checkpoint.grid(column=0,row=0)

checkbox_var = customtkinter.BooleanVar()
# Create a checkbox and link it to the BooleanVar
checkbox = customtkinter.CTkCheckBox(check_frame, text="calculate from CSV", variable=checkbox_var, onvalue=True, offvalue=False)
checkbox.grid(column=1,row=0, padx=(20,0))

###############
# frame for the log printout UI
log_frame = customtkinter.CTkFrame(extractor_frame, fg_color=first_color, width=extractor_width)
log_frame.grid(column=0, row=1)

# Disabled text box for output
text_box = customtkinter.CTkTextbox(log_frame, height=500, width=809, fg_color=light_first_color)
text_box.pack(pady=(10, 0))
text_box.configure(state=customtkinter.DISABLED)  # Disable editing

###############

# when enter is hit on the keyboard it run the software
root.bind('<Return>', RUN_)

# Set default encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')
define()
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