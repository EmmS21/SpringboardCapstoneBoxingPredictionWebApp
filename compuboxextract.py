import pandas as pd
import requests
import urllib.request
import json
import numpy as np
import re
from itertools import islice
import time
# extacting boxer ids from compubox
def func():
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Host": "beta.compuboxdata.com",
        "Origin": "http://beta.compuboxdata.com.com",
        "Referer": "http://beta.compuboxdata.com/fighter",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    dataload = {
        "q": '',
        "page_limit": 10000,
        "page": 1,
        "_": 1575596211029
    }
    # requests.get(http://beta.compuboxdata.com/front/fighter/get_fighters_name?q=&page_limit=10000&page=2&_=1575596211029)
    r = requests.get('http://beta.compuboxdata.com/front/fighter/get_fighters_name', params=dataload)
    r = r.json()
    fighters = r['fighters']
    fighters = [fighter['fighter_id'] for fighter in fighters]
    return fighters
# extract boxer fights from compubox
def fights(list_of_boxers):
    dataframe = pd.DataFrame()
    for boxer in list_of_boxers:
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Content-Length": "28",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "beta.compuboxdata.com",
            "Origin": "http://beta.compuboxdata.com.com",
            "Referer": "http://beta.compuboxdata.com/fighter",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        dataload = {"page": "0",
                    "result": "10000",
                    "fighter": boxer}
        t0 = time.time()
        r = requests.post('http://beta.compuboxdata.com/front/fighter/search', headers=headers, data=dataload)
        r = r.json()
        # grab the column names from the dictionary keys of one event
        if len(r) > 0:
            col_titles = r[0].keys()
            # create a list of values (remove the keys from the dictionary of each instance)
            event_values = [list(event.values()) for event in r]
            # create a dataframe from the list of values
            df = pd.concat([pd.DataFrame([i], columns=col_titles) for i in event_values], ignore_index=True)
            dataframe = dataframe.append(df)
            response_delay = time.time() - t0
            time.sleep(0.5 * response_delay)
    return dataframe
fighters = func()
# get punch stats per fight
def punch_stats(df):
    final_rounds_df = pd.DataFrame()
    final_df = pd.DataFrame()
    stats_pattern = re.compile('\d+\.?\d?(?=%)|\d+\/\d+')
    for index, row in df.iterrows():
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Content-Length": "86",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "beta.compuboxdata.com",
            "Origin": "http://beta.compuboxdata.com.com",
            "Referer": "http://beta.compuboxdata.com/fighter",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        # create the data/parameters for each request
        dataload = {"event_id": row['event_id'],
                    "fighter1_id": row['fighter1id'],
                    "fighter2_id": row['fighter2id'],
                    "fighter1_name": row['fighter1ln'],
                    "fighter2_name": row['fighter2ln']
                    }
        t0 = time.time()
        # request the info
        r = requests.post('http://beta.compuboxdata.com/front/fighter/get_fight_report', headers=headers, data=dataload)
        # scrape all the round data from the response
        stats = re.findall(stats_pattern, r.text)
        slice1 = []
        for no in range(78):
            slice1.append(2)
        data_input = iter(stats)
        stats = [list(islice(data_input, elem)) for elem in slice1]
        slice2 = [12, 12, 12, 12, 12, 12, 3, 3]
        input2 = iter(stats)
        stats = [list(islice(input2, elem)) for elem in slice2]
        # final punch stats
        for idx, fighter in enumerate(stats[-2:]):
            total_df = pd.DataFrame(fighter)
            # add the fight / event_id
            total_df['event_id'] = row['event_id']
            # add the fighters name
            if idx % 2 == 0:
                total_df['fighter'] = row['fighter1ln']
            else:
                total_df['fighter'] = row['fighter2ln']
            # add the stat titles
            total_df['punch_stat'] = ['Total Punches', 'Jabs', 'Power Punches']
            # append the dataframes to the corresponding dataframes
            final_df = final_df.append(total_df)
            response_delay = time.time() - t0
            time.sleep(0.5 * response_delay)
    # renaming columns
    final_df.rename(columns={0: 'punches', 1: 'pct_landed'}, inplace=True)
    # dropping duplicates
    final_df.drop_duplicates(inplace=True)
    return final_df
df = fights(fighters)
punches_df = punch_stats(df)
def clean_up(fight_stats=punches_df, fights_df=df):
    # split by / to get punches landed v thrown
    fight_stats[['punches_landed', 'punches_thrown']] = fight_stats['punches'].str.split('/', 2, expand=True).astype(
        int)
    fight_stats = fight_stats.drop(columns='punches')
    # long to wide
    fight_stats = fight_stats.pivot_table(['punches_landed', 'punches_thrown'], ['event_id', 'fighter'],
                                          'punch_stat').reset_index()
    # concate multilevel column names and flatten
    fight_stats.columns = fight_stats.columns.map('|'.join).str.strip('|')
    fight_stats = fight_stats.set_index(
        ['event_id', fight_stats.groupby('event_id').cumcount().add(1)]).unstack().sort_index(axis=1, level=1)
    fight_stats.columns = fight_stats.columns.map('{0[0]}{0[1]}'.format)
    fight_stats.reset_index(inplace=True)
    # merge with first dataset to get full fighter names
    fight_stats = fight_stats.merge(fights_df[['event_id', 'fighter1', 'fighter2']], on='event_id').rename(
        columns={'fighter1_y': 'fighter1', 'fighter2_y': 'fighter-opp'}).drop(
        columns=['fighter1_x', 'fighter2_x']).set_index(['event_id', 'fighter1', 'fighter-opp']).reset_index()
    # capitalize name and surname
    fight_stats['fighter1'] = fight_stats.fighter1.str.title()
    fight_stats['fighter-opp'] = fight_stats['fighter-opp'].str.title()
    return fight_stats
clean_up().to_csv(
    'C://Users//User//Documents//GitHub//SpringboardCapstoneBoxingPredictionWebApp//boxingdata//punch_stats11.csv')
