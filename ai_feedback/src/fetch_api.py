import requests
import pandas as pd

API_URL = "https://jsonplaceholder.typicode.com/comments"

def fetch_comments(limit: int = 20) -> pd.DataFrame:
    #fetch comment fra api og return pandas Dataframe
    response = requests.get(API_URL)
    response.raise_for_status #stoppa ef api villa

    data = response.json()

    #convert yfir í DataFrame
    df = pd.DataFrame(data)
    #geyma fyrstu 20 bara 
    df = df.head(limit)

    #bara geyma þessa dalka
    return df[['name', 'email', 'body']]

#print(fetch_comments(2))