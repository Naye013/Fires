import pandas as pd
import altair as alt
import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_vega_components as dvc

alt.data_transformers.enable("vegafusion")
dash.register_page(__name__, path='/showSecondPage.py', name="Causes of WildFire")
# Load data
df = pd.read_csv("https://raw.githubusercontent.com/Naye013/Fires/main/data/processed/output.csv", low_memory=False)

## -- Plot 1: altair-chart-1 --
wildfires_causes = df.groupby(['FIRE_YEAR', 'state_descriptions', 'FIRE_SIZE_CLASS', 'STAT_CAUSE_DESCR']).size().reset_index(name='COUNT')
fireSize = sorted([{'label': size, 'value': size} for size in df['FIRE_SIZE_CLASS'].unique()], key=lambda x: x['label'])

# Personalized scales from yellow to red
color_scale1 = alt.Scale(range=['#ffff00', '#ffd700', '#ffa500', '#d0320b', '#ff0000', '#8b0000', '#8b0000'])
def create_altair_chart(data):
    title = alt.TitleParams(
    text='Understanding Wildfires: Causes and Fire Size',
    color='white', fontSize=16)
    chart = alt.Chart(data, title=title).mark_square().encode(
        alt.X('FIRE_SIZE_CLASS:N', title=None, axis=alt.Axis(labelAngle=0, ticks=False, labelColor='white')),
        alt.Y('STAT_CAUSE_DESCR:N', title=None, sort='color', axis=alt.Axis(ticks=False, labels=True, labelColor='white')),
        alt.Color('count(FIRE_SIZE_CLASS)', title= 'Count', scale=color_scale1,
                  legend=alt.Legend(titleColor='white', labelColor='white')),
        size='count(FIRE_SIZE_CLASS)',
        tooltip=[
        alt.Tooltip('FIRE_SIZE_CLASS:N', title='Class'),
        alt.Tooltip('STAT_CAUSE_DESCR:N', title='Cause'),
        alt.Tooltip('count(FIRE_SIZE_CLASS)', title='Fires')
        ]
    ).properties(width=300, height=300
    ).configure_view(stroke='transparent'
    ).configure(background='#151515')
    return chart.to_dict(format="vega")

## -- Plot 2: "altair-chart-2" --
color_scale = alt.Scale(domain=['Human','Lightning'], range=['#9D0400', '#FF9900'])

causes_grouped = df[df['CAUSES'].isin(['Human', 'Lightning'])].groupby(['FIRE_YEAR', 'FIRE_SIZE_CLASS', 'state_descriptions', 'geographic_areas_desc', 'CAUSES']).size().reset_index(name='COUNT')
def create_altair_chart2(data):
    title2 = alt.TitleParams(
        text='Regional Fire Patterns: Proportion of Fires',
        color='white', fontSize=16)
    chart2 = alt.Chart(data, title=title2).mark_bar().encode(
        alt.X('sum(COUNT)', stack='normalize', title='', axis=alt.Axis(labelColor='white')),
        alt.Y('geographic_areas_desc:O', sort='y', title="", axis=alt.Axis(labelColor='white')),
        alt.Color('CAUSES', title="", scale=color_scale, legend=alt.Legend(orient='none',
            legendX=90, legendY=-20,
            direction='horizontal',
            titleAnchor='middle',
            titleColor='white',
            labelColor='white')),
        tooltip=[
            alt.Tooltip('sum(COUNT)', title='Fires', format=',d'),
            alt.Tooltip('geographic_areas_desc:O', title='Area'),
            alt.Tooltip('CAUSES', title='Cause')
        ]
    ).properties(width=300, height=270, background='#151515').configure_axis(grid=False)
    return chart2.to_dict(format="vega")

## -- Plot 3: "altair-chart-3" --
# Group by FIRE_YEAR, STATE, and MONTH, calculate the count, and reset the index
grouped_df = df[df['CAUSES'].isin(['Human', 'Lightning'])].groupby(['FIRE_YEAR', 'FIRE_SIZE_CLASS', 'state_descriptions', 'CAUSES', 'MONTH']).size().reset_index(name='COUNT')
# Define the sort order
sort_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun','Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
# Sorting dataframe by the desired order
grouped_df['MONTH'] = pd.Categorical(grouped_df['MONTH'], categories=sort_order, ordered=True)
grouped_df = grouped_df.sort_values(by='MONTH')
def create_altair_chart3(data):
    title3 = alt.TitleParams(
                text='Comparing Monthly Fire Frequencies',
                color='white', fontSize=16)
    chart3_1 = alt.Chart(data, title=title3).mark_line().encode(
    alt.X('MONTH:O', title=None, sort=sort_order, axis=alt.Axis(labelAngle=0, labelColor='white')),
    alt.Y('average(COUNT)', title=None, axis=alt.Axis(labelColor='white')),
    alt.Color('CAUSES:O', title= '', scale=color_scale, legend=alt.Legend(orient='none',
    legendX=120, legendY=-20, direction='horizontal', titleAnchor='middle', titleColor='white',
    labelColor='white'))
    ).properties(width=355, height=270
    )
    chart3_2 = alt.Chart(data).mark_point().encode(
    alt.X('MONTH:O', title=None, sort=sort_order),
    alt.Y('average(COUNT)'),
    alt.Color('CAUSES:O', title='', scale=alt.Scale(scheme='darkred')),
    tooltip=[
    alt.Tooltip('MONTH:O', title='Month'),
    alt.Tooltip('average(COUNT):Q', title='Mean', format='.2f'),
    alt.Tooltip('CAUSES:O', title='Cause')]
    ).properties(width=355, height=270)

    chart3 = alt.layer(chart3_1, chart3_2).configure(background='#151515')
    return chart3.to_dict(format="vega")

## -- Plot 4: "altair-chart-4" --
# Total acres burned
causes_grouped2 = df[df['CAUSES'].isin(['Human', 'Lightning'])].groupby(['FIRE_YEAR', 'FIRE_SIZE_CLASS','state_descriptions', 'geographic_areas_desc', 'CAUSES'])['FIRE_SIZE'].sum().reset_index(name='SUM')
def create_altair_chart4(data):
    title4 = alt.TitleParams(
        text='Regional Fire Patterns: Proportion of Acres Burned',
        color='white', fontSize=16)
    chart4 = alt.Chart(data, title=title4).mark_bar().encode(
        alt.X('sum(SUM)', stack='normalize', title='', axis=alt.Axis(labelColor='white')),
        alt.Y('geographic_areas_desc:O', sort='y', title="", axis=alt.Axis(labelColor='white')),
        alt.Color('CAUSES', title="", scale=color_scale, legend=alt.Legend(orient='none',
            legendX=90, legendY=-20,
            direction='horizontal',
            titleAnchor='middle',
            titleColor='white',
            labelColor='white')),
        tooltip=[
            alt.Tooltip('sum(SUM)', title='Acres', format=',d'),
            alt.Tooltip('geographic_areas_desc:O', title='Area'),
            alt.Tooltip('CAUSES', title='Cause')
        ]
    ).properties(width=300, height=277, background='#151515').configure_axis(grid=False)
    return chart4.to_dict(format="vega")
## -- End of plots --

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Filters
all_dict = {"label": "All", "value": "All"}
fireSize.insert(0, all_dict)
default_fire_size = 'All'

# Options for filters (New version)
states = sorted([{'label': state, 'value': state} for state in df['state_descriptions'].unique()], key=lambda x: x['label'])
all_dict = {"label": "All", "value": "All"}
states.insert(0, all_dict)
default_state = 'All'

# Footnotes
text = """ * Regions of the United States: The 52 states are grouped into 10 major areas: 1. Alaska stands alone in its geographic category. 2. California and Hawaii constitute a distinct region. 3. The Eastern Area consists of Virginia, West Virginia, Pennsylvania, Maryland, New York, Delaware.
4. The Great Basin includes Nevada and Idaho. 5. The National Group encompasses North Carolina, New Hampshire, Maine, the District of Columbia, Connecticut, Massachusetts, Rhode Island, New Jersey, and Vermont. 6. The Northern Rockies include South Dakota, Minnesota, Michigan, Ohio, Indiana, Illinois, Wisconsin, North Dakota, and Iowa. 7. The Northwest encompasses Oregon and Washington. 8. The Rocky Mountain region comprises Wyoming, Colorado, Montana, and Utah.
9. The Southern Area encompasses Arkansas, Texas, Florida, South Carolina, Louisiana, Oklahoma, Kansas, Missouri, Nebraska, Kentucky, Tennessee, Georgia, Alabama, Mississippi, and Puerto Rico. 10. Lastly, the Southwest region includes New Mexico and Arizona."""
text2="""* Human Causes include Debris Burning, Campfire, Equipment Use, Arson, Children, Railroad, Smoking, Powerline, Structure, Fireworks"""

# Define layout
layout = html.Div([
    # Main container for the entire layout
    html.Div([
        # Filters sidebar (dbc.Col with width=3)
        dbc.Col([
            html.Label('Fire Year', className="filter-label"),
            dcc.RangeSlider(
                id='year-slider',
                min=int(df['FIRE_YEAR'].min()),
                max=int(df['FIRE_YEAR'].max()),
                step=1,
                value=[df['FIRE_YEAR'].min(), df['FIRE_YEAR'].max()],
                marks={int(df['FIRE_YEAR'].min()): str(df['FIRE_YEAR'].min()),
                       int(df['FIRE_YEAR'].max()): str(df['FIRE_YEAR'].max())}
            ),
            html.Div(id='slider-output-container', className="slider-output"),
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
            #html.Button("SELECT ALL", id="select-all", n_clicks=0, style={'margin-top': '10px'}),
            html.Br()
        ], width=3, className="sidebar"),  # End of Filters sidebar
        html.Br(),
        # First column of plots (dbc.Col with width=6)
        dbc.Col([
            html.Br(),
            dvc.Vega(
                id="altair-chart-1",
                opt={"renderer": "svg", "actions": False},
                spec=create_altair_chart(wildfires_causes),
                className="altair-chart-1"  # Adding class name
            ),
            html.Br(),
            html.Br(),
            dvc.Vega(
                id="altair-chart-3",
                opt={"renderer": "svg", "actions": False},
                spec=create_altair_chart2(causes_grouped),
                className="altair-chart-2"
            ),
        ], width=3),  # End of first column
        # Second column of plots (dbc.Col with width=6)
        dbc.Col([
            html.Br(),
            dvc.Vega(
                id="altair-chart-2",
                opt={"renderer": "svg", "actions": False},
                spec=create_altair_chart3(grouped_df),
                className="altair-chart-3"
            ),
            html.Br(),
            html.Br(),
            dvc.Vega(
                id="altair-chart-4",
                opt={"renderer": "svg", "actions": False},
                spec=create_altair_chart4(causes_grouped2),
                className="altair-chart-4"
            ),
        ],width=5)  # End of second column
    ], className="Container"),
    html.Br(),
    html.P(text, className='paragraph-text'),
    html.P(text2, className='paragraph-text'),
    html.Br()# End of Main container
])

@callback(
    [Output('slider-output-container', 'children'),
    Output('altair-chart-1', 'spec'),
     Output('altair-chart-2', 'spec'),
     Output('altair-chart-3', 'spec'),
     Output('altair-chart-4', 'spec')],
    [Input('year-slider', 'value'),
     Input('state-dropdown', 'value'),
     Input('size-class-dropdown', 'value')]
)

def update_altair_chart(year_range, selected_states, selected_sizes):
    dff = wildfires_causes.copy()
    dff2 = causes_grouped.copy()
    dff3 = grouped_df.copy()
    dff4 = causes_grouped2.copy()

    dff = wildfires_causes[(wildfires_causes['FIRE_YEAR'] >= year_range[0]) & (wildfires_causes['FIRE_YEAR'] <= year_range[1])]
    dff2 = causes_grouped[(causes_grouped['FIRE_YEAR'] >= year_range[0]) & (causes_grouped['FIRE_YEAR'] <= year_range[1])]
    dff3 = grouped_df[(grouped_df['FIRE_YEAR'] >= year_range[0]) & (grouped_df['FIRE_YEAR'] <= year_range[1])]
    dff4 = causes_grouped2[(causes_grouped2['FIRE_YEAR'] >= year_range[0]) & (causes_grouped2['FIRE_YEAR'] <= year_range[1])]

    if 'All' not in selected_states:
        dff = dff[dff['state_descriptions'].isin(selected_states)]
        dff2 = dff2[dff2['state_descriptions'].isin(selected_states)]
        dff3 = dff3[dff3['state_descriptions'].isin(selected_states)]
        dff4 = dff4[dff4['state_descriptions'].isin(selected_states)]

    if 'All' not in selected_sizes:
        dff = dff[dff['FIRE_SIZE_CLASS'].isin(selected_sizes)]
        dff2 = dff2[dff2['FIRE_SIZE_CLASS'].isin(selected_sizes)]
        dff3 = dff3[dff3['FIRE_SIZE_CLASS'].isin(selected_sizes)]
        dff4 = dff4[dff4['FIRE_SIZE_CLASS'].isin(selected_sizes)]

    updated_chart1 = create_altair_chart(dff)
    updated_chart2 = create_altair_chart2(dff2)
    updated_chart3 = create_altair_chart3(dff3)
    updated_chart4 = create_altair_chart4(dff4)
    slider_output = dcc.Markdown(f'Selected years: {year_range[0]} - {year_range[1]}')
    return slider_output, updated_chart1, updated_chart2, updated_chart3, updated_chart4

