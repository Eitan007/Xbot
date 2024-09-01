import pandas as pd

df = pd.read_csv('rawProfiles_odukoyaisaac.csv')

df['Joined_X'] = df['Joined_X'].astype(str)

df.to_csv('rawProfiles_odukoyaisaac.csv', index=False)