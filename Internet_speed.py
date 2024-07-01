import pandas as pd
import re
from scipy import stats
import scikit_posthocs as sp
import matplotlib.pyplot as plt
import seaborn as sns
 
# Load dataset, convert bit/s to Mbit/s, split timestamp and remove measurements from incomplete first and last days
df = pd.read_csv('speed.csv')
df['Download'] = df.apply(lambda row: row.Download/1e6, axis=1)
df['Upload'] = df.apply(lambda row: row.Upload/1e6, axis=1)
df['Date'] = df['Timestamp'].apply(lambda x: re.findall('2021-12-..', x)[0])
df['Time'] = df['Timestamp'].apply(lambda x: re.findall('\d\d:\d\d', x)[0])
df.drop(columns=['Server ID', 'Sponsor', 'Server Name', 'Timestamp', 'Distance'], axis=1, inplace=True)
df = df[(df['Date'] > '2021-12-05') & (df['Date'] < '2021-12-30')]
 
# Analysis of clean dataset
print(f"The mean download speed was {round(df['Download'].mean(), 1)} Mbit/s.")
print(f"The mean upload speed was {round(df['Upload'].mean(), 1)} Mbit/s.")
print(f"The mean ping time was {round(df['Ping'].mean(), 1)} ms.")

# Visualise results
fig, axes = plt.subplots(1,3, figsize=(15, 3))
sns.violinplot(ax=axes[0], data=df.rename(columns={'Download': 'Download / Mbit/s'}), y='Download / Mbit/s', color='#6a00a8')
sns.violinplot(ax=axes[1], data=df.rename(columns={'Upload': 'Upload / Mbit/s'}), y='Upload / Mbit/s', color='#b12a90')
sns.violinplot(ax=axes[2], data=df.rename(columns={'Ping': 'Ping / ms'}), y='Ping / ms', color='#e16462')

# Calculate averages
df1 = df.groupby('Date')['Download'].apply(lambda x: (x < 6).sum()).reset_index(name='count')
down_min = df1[df1['count'] > 0]['count'].count()
print(f"The min download speed was undercut on {down_min} out of 24 days.")
 
df2 = df.groupby('Date')['Download'].apply(lambda x: (x >= 14.4).sum()).reset_index(name='count')
down_max = df2[df2['count'] > 0]['count'].count()
print(f"90% of the max download speed was reached on {down_max} out of 24 days.")
 
avgdown = df[df['Download'] >= 9.8]['Download'].count() / len(df) * 100
print(f"The avg download speed was reached in {round(avgdown, 1)}% of the measurements.")
 
df3 = df.groupby('Date')['Upload'].apply(lambda x: (x < 1).sum()).reset_index(name='count')
up_min = df3[df3['count'] > 0]['count'].count()
print(f"The min upload speed was undercut on {up_min} out of 24 days.")
 
df4 = df.groupby('Date')['Upload'].apply(lambda x: (x >= 2.16).sum()).reset_index(name='count')
up_max = df4[df4['count'] > 0]['count'].count()
print(f"90% of the max upload speed was reached on {up_max} out of 24 days.")
 
avgup = df[df['Upload'] >= 0.7]['Upload'].count() / len(df) * 100
print(f"The avg upload speed was reached in {round(avgup, 1)}% of the measurements.")
 
# Sort by daytime and perform statistics
start_m = '06:15'
end_m = '11:45'
morning = df[(df['Time'] >= start_m) & (df['Time'] <= end_m)]
 
start_a = '12:15'
end_a = '17:45'
afternoon = df[(df['Time'] >= start_a) & (df['Time'] <= end_a)]
 
start_e = '18:15'
end_e = '23:45'
evening = df[(df['Time'] >= start_e) & (df['Time'] <= end_e)]
 
start_n = '00:15'
end_n = '05:45'
night = df[(df['Time'] >= start_n) & (df['Time'] <= end_n)]
 
df5 = pd.concat([morning['Download'], evening['Download'], afternoon['Download'],
                 night['Download']], keys=['m', 'e', 'a', 'n'])
 
totest = [df5['m'], df5['e'], df5['a'], df5['n']]
dunns = sp.posthoc_dunn(totest, p_adjust='bonferroni')
print(dunns)

# Display daytime results in a raincloud plot
series_1 = pd.Series(list(morning['Download']))
series_2 = pd.Series(list(afternoon['Download']))
series_3 = pd.Series(list(evening['Download']))
series_4 = pd.Series(list(night['Download']))
df6 = pd.DataFrame(columns = ['morning', 'afternoon', 'evening', 'night'])
df6['morning'] = series_1
df6['afternoon'] = series_2
df6['evening'] = series_3
df6['night'] = series_4
df6 = df6.melt(ignore_index=False).reset_index()

fig = plt.figure(figsize=(4,6))
sns.boxplot(data=df6, x='variable', y='value', palette='magma')
plt.ylabel('Download / Mbit/s')
plt.xlabel('Daytime')
