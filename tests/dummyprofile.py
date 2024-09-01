import random
from faker import Faker
import json

# Initialize the Faker library
fake = Faker()

# Function to generate a random user
def generate_random_user():
    return {
        'name': fake.name(),
        'screen_name': fake.user_name(),
        'followers_count': random.randint(100, 10000),
        'following_count': random.randint(100, 10000),
        'statuses_count': random.randint(0, 5000),
        'can_dm': random.choice([True, False]),
        'location': fake.city() + ', ' + fake.country(),
        'created_at': fake.date_this_decade().strftime('%d %B %Y'),
        'is_translator': random.choice([True, False]),
        'favourites_count': random.randint(0, 2000),
        'is_blue_verified': random.choice([True, False]),
        'default_profile_image': random.choice([True, False])
    }

# Number of lists to generate
num_lists = 10
num_users_per_list = 6

# Open the file in write mode
with open('dummyUserProfile.txt', 'w') as file:
    for _ in range(num_lists):
        # Generate a list of random users
        users = [generate_random_user() for _ in range(num_users_per_list)]
        
        # Convert the list of users to a JSON string
        users_json = json.dumps(users)
        
        # Write the JSON string to a new line in the file
        file.write(users_json + '\n')

print("Users have been written to 'dummyUserProfile.txt', each list on a new line.")
