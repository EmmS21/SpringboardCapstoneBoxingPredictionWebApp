import pandas as pd
import glob
punches = pd.concat([pd.read_csv(f, index_col=None,header=0) for f in glob.glob('C:\\Users\\User\\Documents\\datasets\\punch_stats*.csv')])
topten = pd.read_csv('C:\\Users\\User\\Documents\\GitHub\\SpringboardCapstoneBoxingPredictionWebApp\\boxingdata\\topten.csv')
#drop duplicate fights
punches = punches.drop_duplicates(subset='event_id')
#create a new dataframe
fighters= pd.DataFrame()
fighters = pd.DataFrame(punches.groupby('fighter1').sum().pipe(lambda df: (df['punches_landed|Jabs1'] / df['punches_thrown|Jabs1'])*100)).reset_index()
fighters.rename(columns={0:'Jab accuracy'},inplace=True)
fighters['Power punch accuracy'] = punches.groupby('fighter1').sum().pipe(lambda df: (df['punches_landed|Power Punches1'] / df['punches_thrown|Power Punches1'])*100).values
fighters['Total punch accuracy'] = punches.groupby('fighter1').sum().pipe(lambda df: (df['punches_landed|Total Punches1'] / df['punches_thrown|Total Punches1'])*100).values
fighters['Avg Jabs landed'] = punches.groupby('fighter1')['punches_landed|Jabs1'].mean().values
fighters['Avg Power punches landed'] = punches.groupby('fighter1')['punches_landed|Power Punches1'].mean().values
fighters['Avg Total punches landed'] = punches.groupby('fighter1')['punches_landed|Total Punches1'].mean().values
#punches landed against
fighters['% of Power punches landed against'] = punches.groupby('fighter1').sum().pipe(lambda df: (df['punches_landed|Power Punches2'] / df['punches_thrown|Power Punches2']*100)).values
fighters['% of Jabs landed against'] = punches.groupby('fighter1').sum().pipe(lambda df: (df['punches_landed|Jabs2'] / df['punches_thrown|Jabs2'])*100).values
fighters['% of Total punches landed against'] = punches.groupby('fighter1').sum().pipe(lambda df: (df['punches_landed|Total Punches2'] / df['punches_thrown|Total Punches2'])*100).values
fighters['Avg Jabs landed against'] = punches.groupby('fighter1')['punches_landed|Jabs2'].mean().values
fighters['Avg Power punches landed against'] = punches.groupby('fighter1')['punches_landed|Power Punches2'].mean().values
fighters['Avg Total punches landed against'] = punches.groupby('fighter1')['punches_landed|Total Punches2'].mean().values
#change order of names
fighters['fighter1'] = fighters['fighter1'].str.split().apply(lambda x: ' '.join(x[::-1]))
fighters2 = fighters.merge(topten[['name','wins','draws','losses','division','average_weight','sex']],left_on='fighter1',right_on='name')
fighters2.to_csv('C://Users//User//Documents//GitHub//SpringboardCapstoneBoxingPredictionWebApp//boxingdata//punchingstats.csv')
