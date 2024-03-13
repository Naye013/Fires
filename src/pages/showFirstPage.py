from dash import Dash, html, Input, Output, callback
import pandas as pd
import dash
from dash import html, dcc, Input, Output
import plotly.express as px

dash.register_page(__name__, path='/', name="Overview on WildFire")
df = pd.read_csv("https://raw.githubusercontent.com/andrewsarracini/DATA551_FireAnalysis/main/data/processed/output.csv", low_memory=False)
# df = pd.read_csv("../data/processed/output.csv", low_memory=False)
fire_data_grped = df.groupby(['state_descriptions','STATE', 'FIRE_YEAR', 'FIRE_SIZE_CLASS'])['FIRE_SIZE'].agg(['sum', 'count']).reset_index()
#fire_data_grped.rename(columns={'state_descriptions':'STATE'},inplace=True)

fire_data_grped.rename(columns={'sum': 'FIRE_SIZE', 'count': 'TotalFireCount'}, inplace=True)

# Options for filters
# states = sorted([{'label': state, 'value': state} for state in fire_data_grped['STATE'].unique()],
#                 key=lambda x: x['label'])
states = sorted([
    {'label': state_label, 'value': state_value}
    for state_value,state_label in zip(fire_data_grped['STATE'].unique(), fire_data_grped['state_descriptions'].unique())
], key=lambda x: x['label'])
fireSize = sorted([{'label': size, 'value': size} for size in fire_data_grped['FIRE_SIZE_CLASS'].unique()],
                  key=lambda x: x['label'])

all_dict = {"label": "All", "value": "All"}
states.insert(0, all_dict)
fireSize.insert(0, all_dict)

default_state = 'All'
default_fire_size = 'All'

# Define layout
layout = html.Div([
    # Filters sidebar
    html.Div([
        html.Label('Fire Year', className="filter-label"),
        dcc.RangeSlider(
            id='year-slider',
            min=int(fire_data_grped['FIRE_YEAR'].min()),
            max=int(fire_data_grped['FIRE_YEAR'].max()),
            step=1,
            value=[fire_data_grped['FIRE_YEAR'].min(), fire_data_grped['FIRE_YEAR'].max()],
            marks={int(fire_data_grped['FIRE_YEAR'].min()): str(fire_data_grped['FIRE_YEAR'].min()),
                   int(fire_data_grped['FIRE_YEAR'].max()): str(fire_data_grped['FIRE_YEAR'].max())}
        ),
        html.Div(id='slider-output-container-map', className="slider-output"),
        html.Label('State', className="filter-label"),
        dcc.Dropdown(
            id='state-dropdown',
            options=states,
            multi=True,
            value=[default_state],
            className="shadow-style"
        ),
        html.Br(),
        html.Label('Fire Size', className="filter-label"),
        dcc.Dropdown(
            id='size-class-dropdown',
            options=fireSize,
            multi=True,
            value=[default_fire_size],
            className="shadow-style"
        ),
        html.Br(),
        html.Div([
            html.Label('Fire Size Description', className="filter-label"),
            html.Div([
                html.P('A = 0 - 0.25 acres (minimal)'),
                html.P('B = 0.26-9.9 acres (minor)'),
                html.P('C = 10.0-99.9 acres (low-moderate)'),
                html.P('D = 100-299 acres (moderate)'),
                html.P('E = 300 to 999 acres (high-moderate)'),
                html.P('F = 1000 to 4999 acres (major)'),
                html.P('G = 5000+ acres (extreme)')
            ], className='fire-size-info')
        ]),
    ], className="sidebar"),
    # Maps section
    html.Div([
        dcc.Graph(id='us_maps', figure={}, className="mapStyle"),
        html.Div([
            html.Div([
                html.Div([
                    html.Div(id='total-area-damaged', className="count"),
                    html.Label('Total Area Damaged', className="count-label"),
                ], className="countLabel"),
                html.Div([
                    html.Div(id='total-wildfire-incidents', className="count"),
                    html.Label('Total Wildfire Incidents', className="count-label"),
                ], className="countLabel")
            ], className="Container"),
            dcc.Graph(id='bar_plot', figure={}, style={'height': '65%', 'margin-left': '10px'})
        ])
        ,
    ], className="Container"),  # , 'justify-content': 'space-between','margin-top': '20px', 'margin-left': '20px'
    # Charts section
    html.Div([
        html.Br(),
        dcc.Graph(id='count-chart', className="chart_1"),
        dcc.Graph(id='area-chart', className="chart_2")
    ], className="Container")
])


@callback(
    [Output('slider-output-container-map', 'children'),
     Output(component_id='us_maps', component_property='figure'),
     Output('count-chart', 'figure'),
     Output('area-chart', 'figure'),
     Output('total-area-damaged', 'children'),
     Output('total-wildfire-incidents', 'children'),
     Output('bar_plot', 'figure')],
    [Input('year-slider', 'value'),
     Input('state-dropdown', 'value'),
     Input('size-class-dropdown', 'value')]
)
def update_graph(year_range, selected_states, selected_sizes):
    min_year, max_year = year_range
    slider_output = dcc.Markdown(f'Selected years: {min_year} - {max_year}')
    dff = fire_data_grped.copy()
    dff = dff[(dff['FIRE_YEAR'] >= year_range[0]) & (dff['FIRE_YEAR'] <= year_range[1])]
    if 'All' not in selected_states:
        dff = dff[dff['STATE'].isin(selected_states)]
    if 'All' not in selected_sizes:
        dff = dff[dff['FIRE_SIZE_CLASS'].isin(selected_sizes)]

    mapdata = dff.groupby(['STATE'])['FIRE_SIZE'].sum().reset_index()

    count_area_data = dff[['FIRE_YEAR', 'FIRE_SIZE_CLASS', 'FIRE_SIZE','TotalFireCount']]
    count_area_data = count_area_data.groupby(['FIRE_YEAR', 'FIRE_SIZE_CLASS']).agg({'FIRE_SIZE': 'sum', 'TotalFireCount': 'sum'}).reset_index()
    count_area_data.rename(columns={'sum': 'TotalFireSize', 'count': 'TotalFireCount'}, inplace=True)

    fig = px.choropleth(
        data_frame=mapdata,
        locationmode='USA-states',
        locations='STATE',
        scope="usa",
        color='FIRE_SIZE',
        hover_data=['STATE', 'FIRE_SIZE'],
        color_continuous_scale= px.colors.sequential.YlOrRd,
        template='plotly_dark',
        labels={'FIRE_SIZE': 'Fire Size Class', 'STATE': 'State'}
    )
    color_scale = px.colors.sequential.YlOrRd

    count_chart = px.area(count_area_data, x='FIRE_YEAR', y='TotalFireCount', line_shape='linear',
                          color='FIRE_SIZE_CLASS',
                          color_discrete_sequence=color_scale, title='Annual Count of Wildfires',
                          template='plotly_dark')
    count_chart.update_layout(
        xaxis_title='',
        yaxis_title='Count of Wildfires',
        legend_title_text="Fire Size Class"
    )
    area_chart = px.area(count_area_data, x='FIRE_YEAR', y='FIRE_SIZE', line_shape='linear', color='FIRE_SIZE_CLASS',
                         color_discrete_sequence=color_scale, title='Annual Area Damaged by Wildfires',
                         template='plotly_dark')
    area_chart.update_layout(
        xaxis_title='',
        yaxis_title='Area Damaged (Acres)',
        legend_title_text="Fire Size Class"
    )

    total_area = round(dff['FIRE_SIZE'].sum(), 3)
    total_count = dff['TotalFireCount'].sum()

    top10_grouped = dff.groupby('STATE')['FIRE_SIZE'].sum().reset_index()
    top10 = top10_grouped.head(10)

    top10_sorted = top10.sort_values(by='FIRE_SIZE', ascending=False)

    color_scale = px.colors.sequential.YlOrRd

    barPlot = px.bar(
        top10_sorted,
        y='STATE',
        x='FIRE_SIZE',
        color='FIRE_SIZE',
        color_continuous_scale=color_scale,
        labels={'FIRE_SIZE': 'Total Area Damaged (Acres)'},
        template='plotly_dark',
        #marker_opacity=0.3,
        #marker_line_width=0
    )

    barPlot.update_layout(
        yaxis=dict(title=None),
        title="Top10 Wildfire Damage States"
    )

    # Manually hiding the legend to save space
    barPlot.update_layout(
        showlegend=False,
        coloraxis_showscale=False
    )
    return slider_output, fig, count_chart, area_chart, total_area, total_count, barPlot
