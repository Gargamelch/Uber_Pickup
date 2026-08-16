# This file is dedicated to define functions, paths and colors
import pandas as pd
import streamlit as st
import base64 # SVG manipulation
import re # SVG manipulation


# ---------------------------------------------------
# General settings
# ---------------------------------------------------

APP_VERSION = '1.0.0'

# Constants
DATA_PATH = 'pickups_with_clusters.csv'
HOTZONES_PATH = 'hotzones_summary.csv'

# Color palette
COLORSCALE = [
    [0.0,  '#e0e7ff'],
    [0.25, '#a5b4fc'],
    [0.5,  '#6366f1'],
    [0.75, '#4338ca'],
    [1.0,  '#312e81'],
]

#eef2ff, #e0e7ff, #c7d2fe, #a5b4fc, #818cf8, #6366f1, #4f46e5, #4338ca, #3730a3, #312e81, #1e1b4b

PRIMARY_COLOR = '#4338ca'
SECONDARY_COLOR = '#6366f1'

WEEKDAY_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# ---------------------------------------------------
# Cache Functions
# ---------------------------------------------------

# CSV
@st.cache_data(ttl=604800) # Cache data for 1 week
def load_data():
    '''Load uber data with clusters.'''
    try:
        df = pd.read_csv(DATA_PATH, parse_dates=['Date/Time'])
    except Exception as e: 
        st.error(f'Data file not found')
        return None
   
    return df


@st.cache_data(ttl=604800) # Cache data for 1 week
def load_hotzones():
    '''Load pre-aggregated cluster x day x hour pickup counts and cluster centers.'''
    try:
        df = pd.read_csv(HOTZONES_PATH)
    except Exception as e:
        st.error(f'Hotzones summary file not found')
        return None

    return df


# SVG recolor
def load_svg(filename, color=PRIMARY_COLOR):
    """Load an SVG file and change its color"""
    with open(f'static/{filename}', 'r') as f:
        svg = f.read()
    
    svg = re.sub(r'fill="(?!none)[^"]*"', f'fill="{color}"', svg)
    svg = re.sub(r'stroke="(?!none)[^"]*"', f'stroke="{color}"', svg)
    svg = re.sub(r'fill:[^;}"]*', f'fill:{color}', svg)
    svg = re.sub(r'stroke:[^;}"]*', f'stroke:{color}', svg)
    
    return svg



def svg_to_data_uri(filename, color=PRIMARY_COLOR):
    """Converts an SVG file into a base64 data URI string (for use in CSS, e.g. background-image: url(...))"""
    svg = load_svg(filename, color)
    b64 = base64.b64encode(svg.encode()).decode()
    return f'data:image/svg+xml;base64,{b64}'


# SVG to imgage tag
def svg_to_img(filename, color=PRIMARY_COLOR, width=30):
    """Converts an SVG file into an HTML <img> tag that can be embedded directly in a webpage"""
    svg = load_svg(filename, color)
    b64 = base64.b64encode(svg.encode()).decode()
    return f'<img src="data:image/svg+xml;base64,{b64}" width="{width}"/>'