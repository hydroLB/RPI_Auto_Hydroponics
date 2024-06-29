import plotly
from flask import Flask, send_from_directory
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash_daq as daq
import time
from threading import Thread, Lock
import plotly.graph_objs as go
import datetime
import pytz
import os
import pandas as pd
import plotly.express as px
import json
import glob

# Create a Flask server
server = Flask(__name__)

# Create a Dash app and pass the Flask server
app = Dash(__name__, server=server)
# Customize the HTML head with viewport meta tag
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <title>Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.4">
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Get the directory of the current script
script_dir = os.path.dirname(__file__)

# Construct the full path to the action_log.txt file
action_log_path = os.path.join(script_dir, 'website_vals', 'action_log.txt')

# Ensure the file exists or handle the error appropriately
if not os.path.exists(action_log_path):
    print(f"File not found: {action_log_path}")
    # You can create the file or raise an error here
    open(action_log_path, 'w').close()

# Global variables and locks for pH value, water level, PPM, and temperature
ph_value = 7.0
water_level = 4.0
ppm_value = 0.0
temperature_value = 77.0  # Initial temperature value in Fahrenheit
ph_value_lock = Lock()
water_level_lock = Lock()
ppm_value_lock = Lock()
temperature_value_lock = Lock()

# Custom marks for pH and PPM
custom_marks_ph = {i / 4: '' for i in range(0, 57)}  # Ticks every 0.25, no labels, stop at 14
custom_marks_ph.update({i: str(i) for i in range(0, 15)})

custom_marks_ppm = {i: '' for i in range(0, 200, 2)}  # Ticks every 2 PPM, no labels
custom_marks_ppm.update({i: str(i) for i in range(0, 201, 10)})


def convert_ppm_to_scale(ppm_valu):
    """Convert PPM value to a 0-200 scale with one decimal place accuracy."""
    return round(ppm_valu / 10, 1)


def read_value_from_file(file_path):
    """Read a float value from a file."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return float(file.read().strip())
    return None


def read_last_entries(filename, num_entries):
    """Read the last num_entries from the specified log file."""
    try:
        file_path = os.path.join(script_dir, 'website_vals', filename)
        # Read the file into a DataFrame
        df = pd.read_csv(file_path)
        # Get the last num_entries rows
        df = df.tail(num_entries)
        return df
    except Exception as e:
        print(f"Error reading the last {num_entries} entries from the file: {e}")
        return None


def create_plot(df, column, title, yaxis_title):
    fig = px.line(df, x='Timestamp', y=column, title=title)
    fig.update_layout(
        xaxis_title='Timestamp',
        yaxis_title=yaxis_title,
        template='plotly_dark'
    )
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def create_layout():
    """Create the layout for the Dash app."""
    return html.Div([
        html.Div([
            create_ph_gauge(),
            create_water_level_bar(),
            create_ppm_gauge()
        ], style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'margin-bottom': '17px'}),
        # Adjust the margin-bottom here

        html.Div([
            create_temperature_thermometer(),
            create_text_log()  # Add the text log component
        ], style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'padding': '20px',
                  'margin-top': '-40px'}),  # Adjust the margin-top here

        create_interval_component(),
        html.Div([
            dcc.Graph(id='water-level-graph'),
            dcc.Graph(id='ppm-graph'),
            dcc.Graph(id='ph-graph'),
            dcc.Graph(id='temperature-graph')
        ])
    ])


def read_log_from_file(file_path):
    """Read log entries from a file."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return file.readlines()
    return []


def log_message(message, file_path=action_log_path):
    """Log a message with a timestamp to a specified log file."""
    est = pytz.timezone('US/Eastern')
    current_time = datetime.datetime.now(est).strftime("%y-%m-%d %H:%M")
    new_log_entry = f"{current_time}: {message}\n \n"

    # Read existing log entries
    log_entries = []
    if os.path.exists(file_path):
        with open(file_path, 'r') as log_file:
            log_entries = log_file.readlines()

    # Append new log entry
    log_entries.append(new_log_entry)

    # Keep only the last 10 entries
    if len(log_entries) > 10:
        log_entries = log_entries[-10:]

    # Write log entries back to the file
    with open(file_path, 'w') as log_file:
        log_file.writelines(log_entries)


def create_text_log():
    """Create the text log component style."""
    return html.Div([
        dcc.Textarea(
            id='text-log',
            value='Initializing...',
            style={'width': '230%', 'height': '220px', 'resize': 'none', 'margin-top': '55px'},
            readOnly=True,
        )
    ], style={'display': 'inline-block', 'margin-left': '80px',
              'margin-top': '-100px'})  # Increase margin to add more space


def create_ph_gauge():
    """Create the pH gauge component."""
    return html.Div([
        daq.Gauge(
            id='ph-gauge',
            value=7,  # Start with a neutral pH value
            min=0,
            max=14,
            units="pH",
            showCurrentValue=True,
            color={
                'gradient': False,
                'ranges': {
                    'red': [0, 4.8],
                    '#FFFF00': [4.8, 5.3],
                    'green': [5.3, 6.3],
                    'yellow': [6.3, 6.8],
                    '#FF0000': [6.8, 14]
                },
                'default': 'black'  # Set default color to black
            },
            size=220,  # Reduce the size
            scale={
                'start': 0,
                'interval': 0.25,  # Interval for ticks
                'custom': custom_marks_ph  # Custom labels
            }
        )
    ], style={'display': 'inline-block', 'margin-right': '40px'})  # Add margin to the right


def create_ppm_gauge():
    """Create the PPM gauge component."""
    return html.Div([
        daq.Gauge(
            id='ppm-gauge',
            value=0,  # Start at 0 PPM
            min=0,
            max=200,
            showCurrentValue=True,
            units="PPM (x10)",
            size=230,  # Reduce the size
            scale={
                'start': 0,
                'custom': custom_marks_ppm  # Custom labels
            },
            color={
                'gradient': False,
                'ranges': {
                    'red': [0, 30.0],
                    '#FFFF00': [30.0, 50.0],
                    'green': [50.0, 150.0],
                    'yellow': [150.0, 170.0],
                    '#FF0000': [170.0, 200.0]
                },
                'default': 'black'  # Set default color to black
            }
        )
    ], style={'display': 'inline-block', 'margin-right': '40px'})  # Add margin to the right


def create_temperature_thermometer():
    """Create the temperature thermometer component."""
    return daq.Thermometer(
        id='temperature-thermometer',
        value=77,  # Start at 77 Fahrenheit
        min=0,
        max=120,
        showCurrentValue=True,
        units="Fahrenheit",
        height=210,
        width=15,
        color="#FF5733",
        scale={
            'start': 0,
            'interval': 2,  # Interval for ticks
            'labelInterval': 5  # Label every tick
        }
    )


def create_water_level_figure(water_level_val):
    """Create the water level figure."""
    tickvals = [i / 4 for i in range(0, 33)]
    ticktext = ['' if i % 4 != 0 else f'{i // 4} in' for i in range(0, 33)]

    fig = go.Figure(go.Bar(
        x=['Water Level'],
        y=[water_level_val],
        marker=dict(color="#007bff"),
        orientation='v',
        hoverinfo='none',  # Disable hover info
        width=[0.85]  # Set the width to take up more space
    ))

    fig.update_layout(
        yaxis=dict(
            title='Water Level (inches)',
            titlefont=dict(size=16, family="Arial, sans-serif"),  # Title not bold
            tickmode='array',
            tickvals=tickvals,
            ticktext=ticktext,
            tickfont=dict(size=16, family="Arial, sans-serif", weight="bold"),  # Tick labels bold
            range=[0, 8],
            showgrid=True,
            gridcolor='black',  # Make the gridlines darker
            gridwidth=2.5,  # Make the gridlines thicker
            zeroline=False
        ),
        xaxis=dict(visible=False),
        height=310,  # Adjust height to make the graph larger
        width=200,  # Adjust width to make it larger
        margin=dict(l=30, r=30, t=30, b=30),  # Adjust margins to fit the larger size
        annotations=[
            dict(
                x=0,
                y=water_level_val,
                xref='x',
                yref='y',
                text=f'{water_level_val} in',
                showarrow=False,
                font=dict(size=18, color="black", family="Arial, sans-serif", weight="bold"),
                yshift=-12  # Move the text down by 20 pixels
            )
        ]
    )

    return fig


def create_water_level_bar():
    """Create the water level bar component."""
    return html.Div([
        dcc.Graph(
            id='water-level-bar',
            config={
                'displayModeBar': False,  # Hide the Plotly.js toolbar
                'staticPlot': True  # Make the plot static
            }
        )
    ], style={'display': 'inline-block', 'margin-right': '40px'})  # Add margin to the right


def create_interval_component():
    """Create the interval component for periodic updates."""
    return dcc.Interval(
        id='interval-component',
        interval=180 * 1000,  # Update every 5 minutes
        n_intervals=0
    )


def update_gauge_and_bar(_):
    with ph_value_lock:
        ph_val = ph_value
    with water_level_lock:
        water_level_val = water_level
    with ppm_value_lock:
        ppm_val = ppm_value
    with temperature_value_lock:
        temperature_val = temperature_value

    log_entries = read_log_from_file(action_log_path)
    log_text = ''.join(log_entries)

    fig = create_water_level_figure(water_level_val)

    return ph_val, fig, ppm_val, temperature_val, log_text


# Modified update_values function to use the conversion function
def update_values():
    """Periodically update the gauge and bar values by reading from the files."""
    global ph_value, water_level, ppm_value, temperature_value
    while True:
        new_ph_value = read_value_from_file('website_vals/ph_value.txt')
        new_water_level = read_value_from_file('website_vals/water_level.txt')
        new_ppm_value = read_value_from_file('website_vals/ppm_value.txt')
        new_temperature_value = read_value_from_file('website_vals/temperature_value.txt')

        if new_ph_value is not None:
            with ph_value_lock:
                ph_value = new_ph_value
        if new_water_level is not None:
            with water_level_lock:
                water_level = new_water_level
        if new_ppm_value is not None:
            with ppm_value_lock:
                ppm_value = convert_ppm_to_scale(new_ppm_value)
        if new_temperature_value is not None:
            with temperature_value_lock:
                temperature_value = new_temperature_value
        time.sleep(180)  # Adjust the sleep time as needed


def update_graphs(_):
    df = read_last_entries('sensor_data.log', 48)
    if df is not None:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        water_level_plot = create_plot(df, 'Water Level', 'Water Level Over Time', 'Water Level')
        ppm_plot = create_plot(df, 'PPM', 'PPM Over Time', 'PPM')
        ph_plot = create_plot(df, 'pH', 'pH Over Time', 'pH')
        temperature_plot = create_plot(df, 'Temperature', 'Temperature Over Time', 'Temperature (F)')

        return water_level_plot, ppm_plot, ph_plot, temperature_plot
    else:
        return {}, {}, {}, {}


app.callback(
    [Output('water-level-graph', 'figure'),
     Output('ppm-graph', 'figure'),
     Output('ph-graph', 'figure'),
     Output('temperature-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)(update_graphs)


@server.route('/static/<path:filename>')
def send_file(filename):
    return send_from_directory(os.path.join(script_dir, 'website_vals', 'pictures'), filename)


def get_latest_picture():
    """Get the path to the latest picture in the pictures folder."""
    pictures_path = os.path.join(script_dir, 'website_vals', 'pictures')
    list_of_files = glob.glob(os.path.join(pictures_path, '*.jpg'))  # Get all jpg files
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getmtime)
    return latest_file


def create_picture_display():
    """Create the picture display component."""
    latest_picture = get_latest_picture()
    if latest_picture:
        img_src = f"/static/{os.path.basename(latest_picture)}"
        return html.Div([
            html.Img(src=img_src, style={'width': '230px', 'height': '220px', 'object-fit': 'cover'})
        ], style={'display': 'inline-block', 'margin-right': '40px', 'margin-left': '10px'})
    else:
        return html.Div([
            html.P("No picture available")
        ], style={'display': 'inline-block', 'margin-right': '40px', 'margin-left': '10px'})


if __name__ == '__main__':
    app.layout = create_layout()
    Thread(target=update_values, daemon=True).start()
    app.run_server(debug=True)
