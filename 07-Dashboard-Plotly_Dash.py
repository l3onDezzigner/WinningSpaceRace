import pandas as pd
import dash
from dash import html, dcc  # Updated imports from Dash
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create a list of launch sites from the DataFrame
launch_sites = spacex_df['Launch Site'].unique()

# Create options for the dropdown
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
                   [{'label': site, 'value': site} for site in launch_sites]

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(id='site-dropdown',
                                options=dropdown_options,
                                value='ALL',  # default value
                                placeholder="Select a Launch Site here",
                                searchable=True
                                ),
    
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                min=0, 
                                max=10000, 
                                step=1000,
                                marks={i: str(i) for i in range(0, 11000, 1000)},
                                value=[min_payload, max_payload]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # For all sites, calculate the total success and failed counts
        success_counts = spacex_df['class'].value_counts()
        fig = px.pie(values=success_counts,
                     names=success_counts.index.map({1: 'Success', 0: 'Failed'}),
                     title='Total Launch Success Counts for All Sites')
        return fig
    else:
        # For a specific site, filter the DataFrame
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_counts = filtered_df['class'].value_counts()
        fig = px.pie(values=success_counts,
                     names=success_counts.index.map({1: 'Success', 0: 'Failed'}),
                     title=f'Launch Success Counts for {entered_site}')
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'), 
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(selected_site, payload_range):
    # Filter the DataFrame based on the selected site and payload range
    filtered_df = spacex_df
    
    # Check if a specific site is selected
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    # Further filter based on the payload range
    filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= payload_range[0]) & 
                              (filtered_df['Payload Mass (kg)'] <= payload_range[1])]

    # Create the scatter plot
    fig = px.scatter(filtered_df, 
                     x='Payload Mass (kg)', 
                     y='class', 
                     color='Booster Version Category',
                     title=f'Payload vs. Launch Success for {selected_site if selected_site != "ALL" else "All Sites"}',
                     labels={'class': 'Launch Outcome (0 = Failed, 1 = Success)'})
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
