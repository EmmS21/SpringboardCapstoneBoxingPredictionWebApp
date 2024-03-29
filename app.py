import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output
import dash_table
import plotly.graph_objs as go
import pandas as pd
import os
#read data
path = 'https://raw.githubusercontent.com/EmmS21/SpringboardCapstoneBoxingPredictionWebApp/master/boxingdata/vizdata.csv'
path_two = 'https://raw.githubusercontent.com/EmmS21/SpringboardCapstoneBoxingPredictionWebApp/master/boxingdata/topten.csv'
path_three = 'https://raw.githubusercontent.com/EmmS21/SpringboardCapstoneBoxingPredictionWebApp/master/boxingdata/df.csv'
path_four = 'https://raw.githubusercontent.com/EmmS21/SpringboardCapstoneBoxingPredictionWebApp/master/boxingdata/fightoutcomes.csv'
path_five = 'https://raw.githubusercontent.com/EmmS21/SpringboardCapstoneBoxingPredictionWebApp/master/boxingdata/punchingstats.csv'
data = pd.read_csv(path)
topten = pd.read_csv(path_two)
df = pd.read_csv(path_three)
fight_outcomes = pd.read_csv(path_four)
punch_stats = pd.read_csv(path_five)
punch_stats = punch_stats.drop(columns=['Unnamed: 0'])
punch_stats = punch_stats[['name','sex','division','wins','draws','losses','average_weight','Jab accuracy','Power punch accuracy','Total punch accuracy','Avg Total punches landed','% of Total punches landed against','Avg Total punches landed against']]
WEIGHT_CLASS = data['division'].unique()
GENDER = data['sex'].unique()
app = dash.Dash()
def getData():
    return punch_stats.to_dict('records')
server = app.server
#punching stats datatable
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
    ),
    html.Div([
        dash_table.DataTable(
            id='punchstats',
            columns= [{'name': 'name', 'id': 'name'},
                     {'name':'sex','id':'sex'},
                     {'name':'division','id':'division'},
                     {'name':'wins','id':'wins'},
                     {'name':'draws','id':'draws'},
                     {'name':'losses','id':'losses'},
                     {'name':'average_weight','id':'average_weight'},
                     {'name':'Jab accuracy','id':'Jab accuracy'},
                     {'name':'Power punch accuracy','id':'Power punch accuracy'},
                     {'name':'Total punch accuracy','id':'Total punch accuracy'},
                     {'name':'Avg Total punches landed','id':'Avg Total punches landed'},
                     {'name':'% of Total punches landed against','id':'% of Total punches landed against'},
                     {'name':'Avg Total punches landed against','id':'Avg Total punches landed against'}],
            data = punch_stats.to_dict('records'),
            filter_action ='native',
            page_current=0,
            page_size=5,
            page_action='native',
            sort_action='native',
            column_selectable="single",
            sort_mode='multi',
            style_table={'overflowX':'scroll',
                         'maxHeight':'300px'},
            style_header={'backgroundColor':'rgb(30,30,30)'},
            style_cell={'backgroundColor':'rgb(250,250,250)',
                        'color':'grey'},
            sort_by=[]),
    ]),
    html.Div(id='filteringaction')
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
    top_boxer = top_boxer.drop(columns ='Unnamed: 0')
    top_boxer = top_boxer.drop_duplicates('name', keep='last')
    # limit to top 10
    top_boxer = top_boxer.nlargest(10, 'total_points').sort_values(by='total_points', ascending=False)
    top_boxer=top_boxer[['name','wins','draws','losses','location','division','average_weight','average_opponent_weight','bouts_fought','win by knockout','win by split decision','win by technical knockout','win by unanimous decision','sex','total_points']]
    return {
        'data': [
            go.Table(
                header=dict(values=list(top_boxer.columns),fill_color='paleturquoise',align='left'),
                cells=dict(values=[top_boxer['name'],top_boxer['wins'],top_boxer['draws'],top_boxer['losses'],top_boxer['location'],top_boxer['division'],top_boxer['average_weight'],top_boxer['average_opponent_weight'],
                                   top_boxer['bouts_fought'],top_boxer['win by knockout'],
                                   top_boxer['win by split decision'],top_boxer['win by technical knockout'],top_boxer['win by unanimous decision'],top_boxer['sex'],top_boxer['total_points']],
                           fill_color ='lavender',align='left'))
        ],
        'layout': go.Layout(
            title='Top 10 boxers by wins',
            paper_bgcolor='black',
        )
    }
#punch states data table
@app.callback(
    dash.dependencies.Output('filteringaction','children'),
    [dash.dependencies.Input('punchstats','data')])
def update_punchstats(rows):
    if rows is None:
        df_frame = punch_stats
    else:
        df_frame = pd.DataFrame(rows)
    return html.Div()
#age group heatmap
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
    order = ['15-20', '20-25', '25-30', '30-35', '35-40']
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
            xaxis={'title':'Opposition age range','categoryarray': order},
            yaxis={'title': 'Boxer age range'},
            hovermode='closest',
            paper_bgcolor='black',
        )
    }
if __name__ == '__main__':
    app.server.run(debug=True)