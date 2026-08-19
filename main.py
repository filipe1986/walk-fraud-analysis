import pandas as pd

url = 'https://gist.githubusercontent.com/cloudwalk-tests/76993838e65d7e0f988f40f1b1909c97/raw/295d9f7cb8fdf08f3cb3bdf1696ab245d5b5c1c9/transactional-sample.csv'

df = pd.read_csv(url)

df['transaction_date'] = pd.to_datetime(df['transaction_date']) # making the transaction_date a proper type

"""
Data columns (total 8 columns):
 #   Column              Non-Null Count  Dtype         
---  ------              --------------  -----         
 0   transaction_id      3199 non-null   int64         
 1   merchant_id         3199 non-null   int64         
 2   user_id             3199 non-null   int64         
 3   card_number         3199 non-null   str           
 4   transaction_date    3199 non-null   datetime64[us]
 5   transaction_amount  3199 non-null   float64       
 6   device_id           2369 non-null   float64       
 7   has_cbk             3199 non-null   bool          
dtypes: bool(1), datetime64[us](1), float64(2), int64(3), str(1)
"""
'''
transaction_id  merchant_id  user_id       card_number           transaction_date  transaction_amount  device_id  has_cbk
0        21320398        29744    97051  434505******9116 2019-12-01 23:16:32.812632              374.56   285475.0    False
1        21320399        92895     2708  444456******4210 2019-12-01 22:45:37.873639              734.87   497105.0     True
2        21320400        47759    14777  425850******7024 2019-12-01 22:22:43.021495              760.36        NaN    False
3        21320401        68657    69758  464296******3991 2019-12-01 21:59:19.797129             2556.13        NaN     True
4        21320402        54075    64367  650487******6116 2019-12-01 21:30:53.347051               55.36   860232.0    False
'''

# Let's oder by user_id so we can check if the same user is testing different cards

df_sorted = df.sort_values(by=['user_id', 'transaction_date'])
#print(df_sorted[['user_id', 'transaction_date']].head(15))
'''
      user_id           transaction_date
11          6 2019-12-01 20:44:48.109011
3197        7 2019-11-01 01:29:45.799767
3198        8 2019-11-01 01:27:15.811098
3189       19 2019-11-01 17:52:57.071163
390       132 2019-11-30 10:36:29.122871
555       136 2019-11-29 18:18:03.840585
609       153 2019-11-29 16:21:44.370055
1013      163 2019-11-28 13:00:17.797337
2994      167 2019-11-07 22:02:33.150491
29        184 2019-12-01 19:23:45.202875
1621      208 2019-11-23 13:00:53.469234
875       244 2019-11-28 19:08:12.611753
3124      266 2019-11-03 20:24:50.039652
3123      266 2019-11-03 20:25:23.212894
2796      276 2019-11-11 15:53:21.076379
'''

# Checking the time difference between transactions for the same user

df_sorted['time_delta'] = df_sorted.groupby('user_id')['transaction_date'].diff()

user_266_data = df_sorted[df_sorted['user_id'] == 266] # checking a specific and suspicious user
'''
user_id           transaction_date             time_delta
3124      266 2019-11-03 20:24:50.039652                    NaT
3123      266 2019-11-03 20:25:23.212894 0 days 00:00:33.173242
'''
# Converting the time difference into total seconds
df_sorted['seconds_since_last'] = df_sorted['time_delta'].dt.total_seconds()

# Let's filter the dataset to only keep transactions that happened within 60 seconds of a previous one
fast_transactions = df_sorted[df_sorted['seconds_since_last'] < 60]

# checking the chargeback summary for these rapid transactions
'''
Chargbacks for transactions under 60 seconds: 
has_cbk
False    9
True     9
Name: count, dtype: int64
'''

# checking for transactions between 60 and 120 seconds

medium_fast_transactions = df_sorted[(df_sorted['seconds_since_last'] >= 60) & (df_sorted['seconds_since_last'] <= 120)]

# checking the chargeback summary for this bucket
'''
Chargebacks for transactions between 60 and 120 seconds: 
has_cbk
False    11
True      9
Name: count, dtype: int64
'''

# Let's look at the user, device and cards used for these impossibly fast transactions

#print(fast_transactions[['user_id', 'device_id', 'card_number', 'has_cbk']])

'''
Inspecting the bots (fast transactions): 
      user_id  device_id       card_number  has_cbk
3123      266        NaN  482425******1320    False
964     10378    17372.0  415944******1540     True
2573    10405   856642.0  515894******4290    False
3102    16781        NaN  546056******2924     True
2943    42677        NaN  515601******8618     True
2791    49106        NaN  651660******3628    False
1103    53850    20098.0  527468******1757     True
337     56877   866529.0  406655******8217     True
1484    67903   321795.0  478308******3072    False
2931    75710        NaN  554482******7640     True
2929    75710        NaN  554482******7640     True
2355    76708   760553.0  544731******4582    False
3140    76819        NaN  552289******8870     True
130     77959   589318.0  432957******7262    False
129     77959   589318.0  432957******7262    False
628     88553    27250.0  410863******7755    False
147     90176   705388.0  545368******9514     True
1411    98739   422057.0  606282******2118    False

Here we have fast operations. Looks like users 75710 and 77959 are trying to extract money before the bank's automated system locks the card.

device_id missing (NaN) is a strong signal that an API is being used, because automated scripts don't generate device fingerprints like a regular web browsers or mobile phones do.
'''

# Filtering the entire dataset for rows where device_id is missing (NaN)

missing_device_data = df_sorted[df_sorted['device_id'].isna()]

# Checking the total amount of normal vs fraud transactions for these ghost devices

#print(missing_device_data['has_cbk'].value_counts())
'''
Chargebacks for missing device ids (ghosts devices):
has_cbk
False    763
True      67
Name: count, dtype: int64
'''

# global high amounts: checking transactions in the top 5% of all spending
high_amount_threshold = df_sorted['transaction_amount'].quantile(0.95)
global_high_amounts = df_sorted[df_sorted['transaction_amount'] > high_amount_threshold]

#print(f"\nChargebacks for Global High Amounts (Top 5% over {high_amount_threshold:.2f}):")
#print(global_high_amounts['has_cbk'].value_counts())
'''
Chargebacks for Global High Amounts (Top 5% over 2775.27):
has_cbk
False    98
True     62
Name: count, dtype: int64
'''

# Behavioral Spikes: Checking transactions that are 3x larger than the user's personal average
# Using .transform('mean') neatly to assign the user's average back to each of their transaction rows
df_sorted['user_avg_amount'] = df_sorted.groupby('user_id')['transaction_amount'].transform('mean')

# Flaging transactions that spike 3x higher than the user's norm
df_sorted['is_spike'] = df_sorted['transaction_amount'] > (df_sorted['user_avg_amount'] * 3)
user_spikes = df_sorted[df_sorted['is_spike']]

print("\nChargebacks for Sudden Spikes (3x higher than user average):")
print(user_spikes['has_cbk'].value_counts())

