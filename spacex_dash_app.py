# Import required libraries
import pandas as pd
import dash
from dash import dcc, html
#import dash_html_components as html
#import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Dropdown Menu
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}]
launch_sites = spacex_df['Launch Site'].unique()
dropdown_options.extend([{'label': ls, 'value': ls} for ls in launch_sites])

# 

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id = 'site-dropdown',
                                             options = [
                                                {'label': 'All Sites', 'value': 'ALL'},
                                                {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                                ],
                                             value = 'ALL',
                                             placeholder = 'Select a Launch Site',
                                             searchable = True
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(min = 0, max = 10000, step = 500,
                                                value = [min_payload, max_payload],
                                                marks = {n: str(n) for n in range(0, 10001, 2500)},
                                                id = 'payload-slider'),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def update_output_pie(entered_site):
    filtered_df = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
    if entered_site == 'ALL':
        fig = px.pie( 
        names = launch_sites,
        values = filtered_df['class'], 
        title='Total Success Launches By Site')
    
    else:
        site_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_count = site_df[site_df['class'] == 1].shape[0]
        failure_count = site_df[site_df['class'] == 0].shape[0]
        
        fig = px.pie(
            names=['Success', 'Failure'],
            values=[success_count, failure_count],
            title=f'Successful Launches at {entered_site}')
    
    return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id = 'success-payload-scatter-chart', component_property = 'figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value')])
def update_output_scatter(entered_site, payload_range):
    spacex_scatter_df = spacex_df[spacex_df['Payload Mass (kg)'].between(payload_range[0], payload_range[1]).reset_index(drop = True)]
    if entered_site == 'ALL':
        fig = px.scatter(spacex_scatter_df,
                         x = 'Payload Mass (kg)',
                         y = 'class',
                         color = 'Booster Version Category',
                         title = 'Correlation Between Payload and Success for All Sites')

    else:
        scatter_site_df = spacex_scatter_df[spacex_scatter_df['Launch Site'] == entered_site]
        fig = px.scatter(scatter_site_df,
                         x = 'Payload Mass (kg)',
                         y = 'class',
                         color = 'Booster Version Category',
                         title = f'Correlation Between Payload and Success for Site {entered_site}')

    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
