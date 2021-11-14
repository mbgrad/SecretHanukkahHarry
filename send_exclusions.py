# send out exclusions

import pandas as pd
import random

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *

sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))

# here is the list of all players and their email addresses:
allnames =[

        ['John','john@gmail.com'],
        ['Paul','paul@gmail.com'],
        ['George','george@gmail.com'],
        ['Ringo','ringo@gmail'],
        ['Oprah','oprah@gmail'],
        ['Madonna','madonna@gmail'],

    ]

# the first set of impossible pairs. Note: these are bidirectional, so name1 cannot be assigned to name2 and name2 cannot be assigned to name1
# IMPORTANT: the impossible pairs must be mutually exclusive (each name can only appear once). If you want to assign a second impossible relationship for the same person, use the next list.
impossible_pairs = [
    ['John','Ringo'],
    ['Oprah','Paul']
]

# if you want to assign a second set of impossible pairs for the same person as above.
another_impossible_pair = [
     ['','']
]

####################3

def process_pairs (allnames, impossible_pairs, another_impossible_pair):
    num_impossible_pairs = 1

    while num_impossible_pairs > 0 :

        impossibledf = pd.DataFrame(impossible_pairs,columns=['name1','name2'])
        impossibledf2 = pd.DataFrame(another_impossible_pair,columns=['name1','name2'])

        df = pd.DataFrame(allnames, columns=['name','email'])

        df['rand']=[random.randint(0,100) for x in range(len(df))]

        df = df.sort_values(by='rand')

        df['paired_name'] = df['name'].shift(1)[0:len(df)]

        df['paired_email'] = df['email'].shift(1)[0:len(df)]

        df['paired_name'].iloc[0] = df['name'].iloc[-1]

        df['paired_email'].iloc[0] = df['email'].iloc[-1]
        

        df = pd.merge(left=df,right=impossibledf,left_on='name',right_on='name1',how='left')[list(df.columns) + ['name2']]

        df.rename(mapper={'name2':'impossible_name1'},axis=1,inplace=True)

        df = pd.merge(left=df,right=impossibledf,left_on='name',right_on='name2',how='left')[list(df.columns) + ['name1']]

        df.rename(mapper={'name1':'impossible_name2'},axis=1,inplace=True)

        #

        df = pd.merge(left=df,right=impossibledf2,left_on='name',right_on='name1',how='left')[list(df.columns) + ['name2']]

        df.rename(mapper={'name2':'impossible_name3'},axis=1,inplace=True)

        df = pd.merge(left=df,right=impossibledf2,left_on='name',right_on='name2',how='left')[list(df.columns) + ['name1']]

        df.rename(mapper={'name1':'impossible_name4'},axis=1,inplace=True)


        df = pd.merge(left=df,right=df,left_on='paired_name',right_on='name',how='left',suffixes=['','_joined'])[list(df.columns) + ['paired_name_joined']]

        df['impossible'] = (df['paired_name'] == df['impossible_name1']) | ( df['paired_name'] == df['impossible_name2']) |  (df['paired_name'] == df['impossible_name3']) | ( df['paired_name'] == df['impossible_name4'])


        num_impossible_pairs = df['impossible'].sum()

    return df

df = process_pairs (allnames, impossible_pairs, another_impossible_pair)


####################################################
# send out emails
####################################################


for i, each_name, each_email, each_paired_name in df[['name','email','paired_name']].to_records():

    message = Mail(
        from_email=Email(name="Secret Hanukkah Harry",email='do-not-reply@i-made-up-a-fake-email.com'),
        to_emails=each_email,
        subject='Here is your secret Hanukkah Harry match',
        html_content=f'''Hello <strong>{each_name}</strong>,<br>
        Your SECRET HANUKKAH HARRY match is: <strong>{each_paired_name}</strong>!<br>
        Please bring a gift for them to the party.<br><br>
        Thanks!
        ''',
        plain_text_content = f'Hello {each_name} your match is {each_paired_name}'
        )

    response = sg.send(message)
    