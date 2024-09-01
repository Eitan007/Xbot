from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

app = FastAPI()

# Simulated database of valid IDs
VALID_IDS = {"user123", "user456", "user789"}

@app.get("/get-script")
async def get_script(user_id: str = Query(..., alias="id")):
    if user_id in VALID_IDS:
        
        script_content = """

# retrieve user by their username
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

# retrieve user's followers in safe batches and save to csv
async def get_user_follower(user):
    global progress_var
    print_(f'\n\n{user.screen_name}: GETTING FOLLOWERS')
    global use_cursor
    global follower_list
    global no_of_follower_profiles
    
    next_button = load_cursor(user.screen_name, 'followers')
    print_(f'Checkpoint: {next_button}')
    while True:
        if to_cancel:
            return
        # NETWORK REQUEST
        # first results search
        if follower_list is None:
            # sleep before making request
            random_wait()
            try:
                if use_cursor:########### get from last check point
                    if next_button is None:
                        return
                    follower_list = await client.get_user_followers(user.id, cursor=next_button)
                else:
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

                    #save next page for checkpoint reasons
                    next_button = follower_list.next_cursor
                    save_cursor(next_button, user.screen_name, 'followers')
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
                clear_cursor(user.screen_name, 'followers')
                break
        
        # add to filtered users to csv
        filter_profiles_by_size(user, follower_list, 'followers')

# retrieve user's followers in safe batches and save to csv
async def get_user_following(user):
    global progress_var
    print_(f'\n\n{user.screen_name}: GETTING FOLLOWINGS')
    global following_list
    global no_of_follower_profiles
    next_button = load_cursor(user.screen_name, 'following')
    print_(f'Checkpoint: {next_button}')
    while True:
        if to_cancel:
            return

        # NETWORK REQUEST
        # first results search
        if following_list is None:
            # sleep before making request
            random_wait()
            try:
                if use_cursor:########### get from last check point
                    if next_button is None:
                        return
                    following_list = await client.get_user_following(user.id, cursor=next_button)
                else:
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
                    
                    #save next page for checkpoint reasons
                    next_button = following_list.next_cursor
                    save_cursor(next_button, user.screen_name, 'following')
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
                print_(f'{user.screen_name}: {no_of_following_profiles} Following Profiles collected\n\n')
                clear_cursor(user.screen_name, 'following')
                progress_var = 0
                break
        
        # add to filtered users to csv
        filter_profiles_by_size(user, following_list, 'following')

    """
   
        return JSONResponse(content={'hash': script_content})
    else:
        script_content = """

hash = '#29892cc111///###'

        """

        return JSONResponse(content={'hash': script_content})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)



"""

async def get_patient_0_ID():
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

# Search for user via query function
async def search_for_profile():
    query = input('Type in username: ').lower()
    user_profile_results = await client.search_user(query, count=20, cursor=None)
    return user_profile_results, query

# Search for user via query function
async def search_for_tweet():
    query = input('Type in username: ').lower()
    user_profile_results = await client.search_tweet(query,'Top', count=20, cursor=None)
    return user_profile_results, query

async def get_user_by_username_old(username):
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


"""