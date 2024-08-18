#import all packages
from twikit import Client, TooManyRequests
import asyncio
import time
from datetime import datetime
import csv
from configparser import ConfigParser
from random import randint
from dotenv import load_dotenv
import os

follower_count_limit = 10000
following_count_limit = 5000
ask_for_username = True
patient_0_ID = ''
patient_0_username = ''
user_profile_results = None
no_Results = False


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
    for follower in profile_list:
        if follower.followers_count > follower_count_limit or follower.following_count > following_count_limit:
            continue
        else:
            follower_url = f'https://x.com/{follower.screen_name}'
            user_data = [follower.name, follower.screen_name, follower_url, follower.followers_count, follower.following_count, follower.statuses_count, follower.can_dm, follower.location, follower.created_at, follower.is_translator, follower.favourites_count, follower.is_blue_verified, follower.default_profile_image]
            append_data_to_csv(user_data, patient_0_username, 'raw')



# login credentials              
config = ConfigParser()
config.read('config.ini')
username = config['X']['username']
email = config['X']['email']
password = config['X']['password']


# create client
client = Client(language='en-US')

# Run the main function with asyncio
#asyncio.run(login_save_cookies(client, username, email, password))
load_cookies_0(client)

# search user profile


while ask_for_username:
    # reset search
    if no_Results:
        user_profile_results = None

    # NETWORK REQUEST
    # first results search
    if user_profile_results is None:
        # get point-zero username ID

        # sleep before making request
        random_wait()
        try:
            Results_and_query = search_for_profile()    # A REQUEST
        except TooManyRequests as e:
            limit_reset = datetime.fromtimestamp(e.limit_reset)
            print(f'Rate limit reached - {datetime.now()}')
            print(f'Waiting until - {limit_reset}')
            wait_time = limit_reset - datetime.now()
            time.sleep(wait_time.total_seconds())
            continue

        user_profile_results = Results_and_query[0]
        query = Results_and_query[1]
        
        #create csv to store raw data
        create_CSVs(query, 'raw')

    else:
        # if there were prev results let scheck for more results 
        if len(user_profile_results) > 0:

            # sleep before making request
            random_wait()
            try:
                user_profile_results = asyncio.run(user_profile_results.next())  # A REQUEST
            except TooManyRequests as e:
                limit_reset = datetime.fromtimestamp(e.limit_reset)
                print(f'Rate limit reached - {datetime.now()}')
                print(f'Waiting until - {limit_reset}')
                wait_time = limit_reset - datetime.now()
                time.sleep(wait_time.total_seconds())
                continue
            
        else:
            no_Results = True
        
    # POST NETWORK REQUEST
    if len(user_profile_results) > 0:
        for user in user_profile_results:
            # check if username matches with user found in search then get id
            screen_name = user.screen_name

            if query == screen_name:
                patient_0_ID = user.id
                patient_0_username = user.screen_name
                ask_for_username = False
                print(vars(user))
                break
        if ask_for_username:
            print("Results don't match username")

    else:
        print('No Profile Results')


#use patient_0_ID to get followers
random_wait()
follower_list = asyncio.run(client.get_user_followers(patient_0_ID)) # REQUEST

filter_profiles_by_Followers_following(follower_list)