import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import os
#read data
data = pd.read_csv('C:\\Users\\User\\Documents\\GitHub\\Springboard Capstone BoxingPredictionWebApp\\boxingdata\\visuals.csv')
data['division'] = data['division'].fillna('unknown')
data['bouts_fought'] = data['w'].astype('float')+data['l'].astype('float')+data['d'].astype('float')
WEIGHT_CLASS = data['division'].unique()
GENDER = data['sex'].unique()
#uploading data for heatmap
long_data = pd.read_csv('C:\\Users\\User\\Documents\\GitHub\\Springboard Capstone BoxingPredictionWebApp\\boxingdata\\longformateddata2.csv')
#count wins by stance
df = long_data[long_data['outcome'].str.contains('win',na=False)].groupby(['stance1', 'stance.y','division','sex'])['outcome'].count().reset_index()
#dataframe of total wins,losses and draws by age range
wins = long_data[long_data['outcome'].str.contains('win',na=False)].groupby(['age_range', 'opp_age_range','division','sex'])['outcome'].count().reset_index()
loss = long_data[long_data['outcome'].str.contains('loss',na=False)].groupby(['age_range', 'opp_age_range','division','sex'])['outcome'].count().reset_index()
draw = long_data[long_data['outcome'].str.contains('draw',na=False)].groupby(['age_range', 'opp_age_range','division','sex'])['outcome'].count().reset_index()
#other fight outcomes - nan, unknown etc
outcomes = ['win','draw','loss']
outcomeslist = '|'.join(outcomes)
other = long_data[~long_data['outcome'].str.contains(outcomeslist,na=False)].groupby(['age_range', 'opp_age_range','division','sex'])['outcome'].count().reset_index()
#merge all outcomes
fight_outcomes = pd.DataFrame()
fight_outcomes[['age_range','opp_age_range','division','sex','wins']] = wins[['age_range','opp_age_range','division','sex','outcome']]
fight_outcomes = fight_outcomes.merge(loss, on=['age_range','opp_age_range','division','sex']).rename(columns={'outcome':'loss'}).merge(draw, on=['age_range','opp_age_range','division','sex']).rename(columns={'outcome':'draw'}).merge(other, on=['age_range','opp_age_range','division','sex']).rename(columns={'outcome':'other'})
#calculate win rates by different age groups
fight_outcomes['total_fights'] = fight_outcomes[['wins','loss','draw','other']].sum(axis=1)
fight_outcomes['win_rate']=(fight_outcomes['wins']/fight_outcomes['total_fights'])*100
#count total fights by stance
df2 = long_data[['division','outcome']].groupby('division').count().reset_index()
df2.rename(columns={'outcome':'total'},inplace=True)
df = df.merge(df2,on='division')
#calculate wins in percentages
df['win_rate'] =df['outcome']/df['total'] *100
#filter out where stance1 is unknown
df = df[df.stance1 != 'unknown']
#cleaning data for top boxer table
firstBoxer = ['firstBoxerWeight'+str(i) for i in range(1,85)]
secondBoxer = ['secondBoxerWeight'+str(i) for i in range(1,85)]
opp_rating = ['secondBoxerRating'+str(i) for i in range(1,85)]
#average weight of boxer
data['average_weight'] = data[firstBoxer].mean(axis=1)
#average opponent weight
data['average_opponent_weight'] = data[secondBoxer].mean(axis=1)
#extract wins and losses
def wins(col):
    return data[col].astype(str).str.extract('win(?P<win>.*?)}')
def draws(col):
    return data[col].astype(str).str.extract('draw(?P<draw>.*?)l')
opp_rank = ['secondBoxerRecord'+str(i) for i in range(1,85)]
#update columns with wins and losses
for i in opp_rank:
    data['opp_wins'+str(i)] = wins(i)
for i in opp_rank:
    data['opp_draws'+str(i)] = draws(i)
opp_drawsd = ['opp_draws'+str(i) for i in opp_rank]
opp_winsd = ['opp_wins'+str(i) for i in opp_rank]
#remove quotation marks
data[opp_drawsd] = data[opp_drawsd].apply(lambda x: x.str.replace('"',''))
data[opp_winsd] = data[opp_drawsd].apply(lambda x: x.str.replace('"',''))
#replace all letters with number 0
data[opp_drawsd] = data[opp_drawsd].replace(regex='([a-zA-Z])', value=0)
data[opp_winsd] = data[opp_winsd].replace(regex='([a-zA-Z])', value=0)
#assume win is 10 points and draw is 5 points
data[opp_winsd] = data[opp_winsd].astype(float)*10
data[opp_drawsd] = data[opp_drawsd].astype(float)*5
#new column with total points
data['opp_points'] = data[opp_winsd].sum(axis=1) + data[opp_drawsd].sum(axis=1)
#divide points by number of bouts fought
data['opp_points'] = data['opp_points']/data['bouts_fought']
#get type of wins from referee column
ref_outcome = ['referee'+str(i) for i in range(1,85)]
topten = pd.concat([data,data[ref_outcome].astype(str).stack().str.replace('\[|\"','').str.extract('(\w+\s\w+)').groupby(level=0)[0].apply(pd.Series.value_counts).unstack(fill_value=0)],axis=1)
topten = topten[['name','w','d','l','location','division','average_weight','average_opponent_weight','opp_points','bouts_fought','win KO','win SD', 'win TKO', 'win UD','sex']]
topten.rename(columns={'w':'wins','d':'draws','l':'losses','win KO':'win by knockout','win SD':'win by split decision','win TKO':'win by technical knockout','win UD':'win by unanimous decision'},inplace=True)
topten['total_points'] = ((topten['wins']*10 +(topten['draws']*5) - (topten['losses']*5)))+topten['opp_points']
topten = topten
app = dash.Dash()
colors = {
    'background': '##111111',
    'text': '#FFFFFF'
}
app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})
# layout
app.layout = html.Div(children=[
    html.H1(children="Emmanuel's boxing dashboard", style={
        'textAlign': 'left',
        'color':colors['text'],
        'height': '10'
    }),
    html.Section(id='slideshow',children=[
        html.Div(style={'backgroundColor':colors['background'],
                        'textAlign':'center'},id='slideshow-container',children=[
            html.Div(id='image'),
            dcc.Interval(id='interval',interval=3000),
        ])
    ]),
    dcc.Dropdown(
        id='weight_class',
        options=[{'label': i, 'value': i} for i in data['division'].unique()],
        multi=True
    ),
    dcc.Dropdown(
        id='gender',
        options=[{'label': i, 'value':i} for i in fight_outcomes['sex'].unique()],
        multi=True
    ),
    dcc.Graph(
        id='total-bouts-v-bouts-won',
    ),
    dcc.Graph(
        id='stance_comparison',
    ),
    dcc.Graph(
        id='top-boxers',
    ),
    dcc.Graph(
        id='age_groups',
    )
])
#creating function for slideshow
@app.callback(dash.dependencies.Output('image','children'),
              [dash.dependencies.Input('interval','n_intervals')])
def slideshow_display(image):
    if image == None or image % 3 ==1:
        img = html.Img(src='https://photo.boxingscene.com/uploads/wilder-fury%20(1)_5.jpg')
    elif image % 3 == 2:
        img = html.Img(src='https://ringsidereport.com/wp-content/uploads/2016/12/berita-tinju-menebak-lawan-pacquaio-selanjutnya-terence-crawford-dan-vasyl-lomachenko.jpg')
    elif image % 3 == 0:
        img = html.Img(src='https://www.dailybreeze.com/wp-content/uploads/2017/09/sports_170929844_ar_0_aemghshhaiqq.jpg?w=620')
    else:
        img ="None"
    return img
@app.callback(
    dash.dependencies.Output('total-bouts-v-bouts-won', 'figure'),
    [dash.dependencies.Input('weight_class', 'value'),
     dash.dependencies.Input('gender','value')])
def update_scatterplot(weight_class,gender):
    if weight_class is None or weight_class == []:
        weight_class = WEIGHT_CLASS
    if gender is None or gender == []:
        gender = GENDER

    weight_df = data[(data['division'].isin(weight_class))]
    weight_df = weight_df[(weight_df['sex'].isin(gender))]
    return {
        'data': [
            go.Scatter(
                x=weight_df['bouts_fought'],
                y=weight_df['w'],
                text=weight_df['name'],
                mode='markers',
                opacity=0.5,
                marker={
                    'size': 14,
                    'line': {'width': 0.5, 'color': 'blue'}
                },
            )
        ],
        'layout': go.Layout(
            xaxis={'title': 'Bouts fought'},
            yaxis={'title':'Bouts won'},
            legend={'x': 0, 'y': 1},
            hovermode='closest',
            paper_bgcolor='black',
        )
    }
@app.callback(
    dash.dependencies.Output('stance_comparison','figure'),
    [dash.dependencies.Input('weight_class','value'),
     dash.dependencies.Input('gender','value')])
def update_heatmap(weight_class,gender):
    if weight_class is None or weight_class == []:
        weight_class = WEIGHT_CLASS
    if gender is None or gender == []:
        gender = GENDER

    stance_compare = df[(df['division'].isin(weight_class))]
    stance_compare = stance_compare[(stance_compare['sex'].isin(gender))]
    return {
        'data': [
            go.Heatmap(
                z=stance_compare['win_rate'],
                y=stance_compare['stance1'],
                x=stance_compare['stance.y'],
                showscale=True)
        ],
        'layout': go.Layout(
            title='Wins rate by boxer stance',
            xaxis={'title':'Opposition stance'},
            yaxis={'title': 'Boxer stance'},
            hovermode='closest',
            paper_bgcolor='black',
        )
    }
@app.callback(
    dash.dependencies.Output('top-boxers','figure'),
    [dash.dependencies.Input('weight_class','value'),
     dash.dependencies.Input('gender','value')])
def update_heatmap(weight_class,gender):
    if weight_class is None or weight_class == []:
        weight_class = WEIGHT_CLASS
    if gender is None or gender == []:
        gender = GENDER
    top_boxer = topten[(topten['division'].isin(weight_class))]
    top_boxer = top_boxer[(top_boxer['sex'].isin(gender))]
    # limit to top 10
    top_boxer = top_boxer.nlargest(10, 'total_points').sort_values(by='total_points', ascending=False)
    return {
        'data': [
            go.Table(
                header=dict(values=list(top_boxer.columns),fill_color='paleturquoise',align='left'),
                cells=dict(values=[top_boxer['name'],top_boxer['wins'],top_boxer['draws'],top_boxer['losses'],top_boxer['location'],top_boxer['division'],top_boxer['average_weight'],top_boxer['average_opponent_weight'],
                                   top_boxer['opp_points'],top_boxer['bouts_fought'],top_boxer['win by knockout'],
                                   top_boxer['win by split decision'],top_boxer['win by technical knockout'],top_boxer['win by unanimous decision'],top_boxer['sex'],top_boxer['total_points']],
                           fill_color ='lavender',align='left'))
        ],
        'layout': go.Layout(
            title='Top 10 boxers by wins',
            paper_bgcolor='black',
        )
    }
@app.callback(
    dash.dependencies.Output('age_groups','figure'),
    [dash.dependencies.Input('weight_class','value'),
     dash.dependencies.Input('gender','value')])
def update_heatmap(weight_class,gender):
    if weight_class is None or weight_class == []:
        weight_class = WEIGHT_CLASS
    if gender is None or gender == []:
        gender = GENDER

    fights = fight_outcomes[(fight_outcomes['division'].isin(weight_class))]
    fights = fights[(fights['sex'].isin(gender))]
    order = ['15-20', '20-25', '25-30', '30-35', '35-40', '40-45', '45-50']
    return {
        'data': [
            go.Heatmap(
                z=fights['win_rate'],
                y=fights['age_range'],
                x=fights['opp_age_range'],
                showscale=True)
        ],
        'layout': go.Layout(
            title='Wins rate by boxer age range',
            xaxis={'title':'Opposition age range'},
            yaxis={'title': 'Boxer age range'},
            hovermode='closest',
            paper_bgcolor='black',
        )
    }
if __name__ == '__main__':
    app.run_server(debug=True)