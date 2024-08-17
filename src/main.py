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


# load_dotenv()

# # Access variables
# username = os.getenv('USERNAME')
# email = os.getenv('EMAIL')
# password = os.getenv('PASSWORD')





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

# params
minimum_users = 1
query = input('Type in username: ')
#query = f'@{query}'

user_profile_results = asyncio.run(search_user_0(query, 20))

#print(user_profile_results)
#print(user_profile_results)
print(len(user_profile_results))

# # get point-zero username profile
for user in user_profile_results:
    print(vars(user))
    break
























# async def login_user():
#     client = Client(language='en-US')
#     await client.login(auth_info_1=username, 
#                     auth_info_2=email, 
#                     password=password
#     )
#     return client

# client = 

# client.save_cookies('cookies.json')


# #login function
# def login_user(username, email, password):
#     #login credentials              
#     #config = ConfigParser()
#     #config.read('config.ini')
#     #username = config['X']['username']
#     #email = config['X']['email']
#     #password = config['X']['password']

#     # authenticate to X
#     client = Client(language='en-US')

#     # TO BE COMMENTED OUT WHEN WE GET COOKIES
#     client.login(auth_info_1=username, auth_info_2=email, password=password)
#     client.save_cookies('cookies.json')
#     # TO BE COMMENTED OUT WHEN WE GET COOKIES

#     client.load_cookies('cookies.json')

#     return client


# # main function
# def main():
#     # Access variables
#     username = os.getenv('USERNAME')
#     email = os.getenv('EMAIL')
#     password = os.getenv('PASSWORD')

#     #print(f'API Key: {api_key}')
#     #print(f'Database URL: {database_url}')

#     client = login_user(username, email, password)

#     #get point-zero username profile
#     user_profile_results = client.search_user(query=query, count=1)

#     for user in user_profile_results:
#         print(user)



# if __name__ == "__main__":
#     #params
#     minimum_users = 1
#     query = input('Type in username')

#     #run main function
#     main()


