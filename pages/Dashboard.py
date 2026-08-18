import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Load our custom module from utils.py
from utils import (load_data, load_hotzones, load_svg, svg_to_data_uri, svg_to_img, 
                    COLORSCALE, PRIMARY_COLOR, SECONDARY_COLOR, 
                    DATA_PATH, HOTZONES_PATH, APP_VERSION, WEEKDAY_ORDER)

logo_uri = svg_to_data_uri('Uber_logo_2018.svg', color=PRIMARY_COLOR)
info_icon = svg_to_img('info.svg', color=PRIMARY_COLOR, width=20)


# ---------------------------------------------------
# Data loading
# ---------------------------------------------------
pickups_df = load_data()
pickups_unfiltered_df = load_data()
hotzones_df = load_hotzones()

# ---------------------------------------------------
# Sidebar filters 
# ---------------------------------------------------

# Custom CSS to have a clean and well placed logo branding
with st.sidebar:
    st.markdown(
        f'<img src="{logo_uri}" style="display:block; margin:10px auto; height:100px;">',
        unsafe_allow_html=True
    )

    st.header('Filters')
    if pickups_df is not None:
        available_days = [d for d in WEEKDAY_ORDER if d in pickups_df['day_of_week'].unique()]
        selected_day = st.selectbox('Day', options=available_days, key='day_selectbox')
 
        available_hours = sorted(pickups_df['hour'].unique())
        selected_hour = st.slider(
                            'Hour',
                            min_value=int(min(available_hours)),
                            max_value=int(max(available_hours)),
                            value=int(available_hours[0]),
                            key='hour_slider'
                        )
    else:
        selected_day = None
        selected_hour = None


    if pickups_df is None or hotzones_df is None:
        st.stop()

    # Filter to the selected day + hour slice
    filtered_pickups = pickups_df[
        (pickups_df['day_of_week'] == selected_day) & (pickups_df['hour'] == selected_hour)
    ]
    
    filtered_hotzones = hotzones_df[
        (hotzones_df['day'] == selected_day) & (hotzones_df['hour'] == selected_hour)
    ]


    # Badges - CSS
    st.markdown(f"""
        <style>
            .version-badge {{
                position: fixed;
                bottom: 20px;
                display: flex;
                align-items: center;
                gap: 8px;
                flex-wrap: wrap;
            }}
        </style>
        <div class="version-badge">
            <div style="
                background: #0A0E1A;
                color: white;
                padding: 2px 10px;
                border-radius: 20px;
                font-size: 0.75rem;
                font-weight: 700;
                letter-spacing: 1px;
            ">{APP_VERSION}</div>
            <a href="https://www.gnu.org/licenses/gpl-3.0.html" target="_blank" style="
                background: #0A0E1A;
                color: white;
                padding: 2px 10px;
                border-radius: 20px;
                font-size: 0.75rem;
                font-weight: 700;
                text-decoration: none;
            ">GPL-3.0</a>
            <a href="https://github.com/Gargamelch/Uber_Pickup" target="_blank" style="
                background: #0A0E1A;
                color: white;
                padding: 2px 10px;
                border-radius: 20px;
                font-size: 0.75rem;
                font-weight: 700;
                text-decoration: none;
            ">{svg_to_img('github.svg', color='white', width=14)} GitHub</a>
            <span style="color: gray; font-size: 0.75rem;"
    """, unsafe_allow_html=True)
    


st.title(f'New York City Analysis')


# ---------------------------------------------------
# Tab settings 
# ---------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    'Overview',
    'Clusters',
    'Data',
])
# ---------------------------------------------------
# First tab 
# ---------------------------------------------------
with tab1:
    # KPI metrics
    col1, col2, col3, col4 = st.columns(4)
    
    hourly_counts = pickups_unfiltered_df.groupby('hour').size()
    heatmap_df = (pickups_unfiltered_df.groupby(['day_of_week', 'hour'])
                  .size()
                  .reset_index(name='count')
                  .pivot(index='day_of_week', columns='hour', values='count')
                  .reindex(WEEKDAY_ORDER)
                  )
    
    with col1:
        with st.container(border=True):
            st.markdown(f"{svg_to_img('boxicons--taxi-filled.svg')} **Total Pickups**", unsafe_allow_html=True)
            st.metric(
                label='Total Pickups',
                value=f'{len(pickups_unfiltered_df):,}',
                label_visibility='hidden',
            )

    with col2:
        with st.container(border=True):
            st.markdown(f"{svg_to_img('charts.svg')} **Average Pickups per Day**", unsafe_allow_html=True)
            avg_daily_pickups = pickups_unfiltered_df.groupby('date').size().mean()
            st.metric(
                label='Average Pickups per Day',
                value=f'{avg_daily_pickups:,.0f}',
                label_visibility='hidden',
            )

    with col3:
        with st.container(border=True):
            st.markdown(f"{svg_to_img('avg.svg')} **Average Pickups per Hour**", unsafe_allow_html=True)
            avg_hourly_pickups = pickups_unfiltered_df.groupby(['date', 'hour']).size().mean()
            st.metric(
                label='Average Pickups per Hour',
                value=f'{avg_hourly_pickups:,.0f}',
                label_visibility='hidden',
            )

    with col4:
        with st.container(border=True):
            st.markdown(f"{svg_to_img('ic--baseline-event-busy.svg')} **Busiest Combination**", unsafe_allow_html=True)
            combo_counts = pickups_unfiltered_df.groupby(['day_of_week', 'hour']).size()
            busiest_day, busiest_hour = combo_counts.idxmax()
            st.metric(
                label='Busiest Combination',
                value=f'{busiest_day} {busiest_hour}:00',
                label_visibility='hidden',
            )


    st.divider()

    # Yearly production
    col1, col2 = st.columns(2)
    with col1:
        cluster_counts = filtered_hotzones[['cluster_id', 'count']].sort_values('cluster_id')

        fig_bar = px.bar(
            hourly_counts,
            x=hourly_counts.index,
            y=hourly_counts.values,
            labels={'x': 'Hour of day', 
                    'y': 'Number of pickups'},
            height=400,
            width=1000,
        )

        fig_bar.update_layout(
            title=dict(
                text='Total pickups by hour of day (april > september 2014)',
                x=0.5,
                xanchor='center'
            ))

        fig_bar.update_traces(marker_color=PRIMARY_COLOR)

        fig_bar.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig_bar, width='stretch')

    with col2:
        fig_line = px.imshow(
            heatmap_df,
            labels=dict(x='Hour of day', y='Day of week', color='Pickups'),
            color_continuous_scale=COLORSCALE,
            height=400,
            width=1000,
        )

        fig_line.update_layout(
            title=dict(
                text='Pickup volume heatmap (april > september 2014)',
                x=0.5,
                xanchor='center'
            ))    
          
        fig_line.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig_line, width='stretch')



# ---------------------------------------------------
# Second tab
# ---------------------------------------------------
with tab2:

    st.markdown(f"**Pickup Locations · {selected_day} {selected_hour}:00**", unsafe_allow_html=True)
    show_centers = st.checkbox('Show cluster centers', value=True)

    col_map, col_table = st.columns([5, 3])

    with col_map:
        
        fig_map = px.scatter_map(
            filtered_pickups,
            lat='Lat',
            lon='Lon',
            color=filtered_pickups['cluster_id'].astype(str),
            center={"lat": 40.729, "lon": -73.9},
            zoom=10,
            height=650,
            opacity=1,
        )
        fig_map.update_traces(marker=dict(size=5))
        fig_map.update_layout(
            showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0),
            map_style='dark',
        )

        if show_centers and len(filtered_hotzones):
            centers = filtered_hotzones
            fig_map.add_trace(go.Scattermap(
                lat=centers['cluster_lat'],
                lon=centers['cluster_lon'],
                mode='markers',
                marker=dict(size=14, color='white', symbol='circle'),
                name='Cluster centers',
                text=[f'Cluster {c} · {n:,} pickups' for c, n in zip(centers['cluster_id'], centers['count'])],
                hovertemplate='%{text}<extra></extra>',
            ))

        st.plotly_chart(fig_map, width='stretch')

    with col_table:
        ranked = (
            filtered_hotzones[['cluster_id', 'count', 'mean_km', 'median_km', 'max_km']]
            .sort_values('count', ascending=False)
            .rename(columns={
                'cluster_id': 'Cluster',
                'count': 'Pickups',
                'mean_km': 'Mean (km)',
                'median_km': 'Median (km)',
                'max_km': 'Max (km)',
            })
        )

        st.dataframe(
            ranked,
            hide_index=True,
            height=517,
            width='stretch',
            column_config={
                'Pickups': st.column_config.ProgressColumn(
                    label='Pickups',
                    format='%d',
                    min_value=0,
                    max_value=int(ranked['Pickups'].max()),
                ),
                'Mean (km)': st.column_config.NumberColumn(format='%.2f'),
                'Median (km)': st.column_config.NumberColumn(format='%.2f'),
                'Max (km)': st.column_config.NumberColumn(format='%.2f'),
            },
        )

        st.markdown(f"""
            <div style="
                background-color: rgba(15, 21, 37, 1);
                border-left: 3px solid {PRIMARY_COLOR};
                border-radius: 0 8px 8px 0;
                padding: 15px 20px;
                margin: 10px 0 0 0;
            ">
                <p style="margin: 0; font-size: 1rem; line-height: 1.6;">
                    {info_icon} <strong>Clusters</strong>
                    <span style="color: #aaa;"> were generated from raw pickup latitude/longitude coordinates.</span>
                    <br>
                    <span style="color: #aaa;"><code>k value</code> was fixed at 9 for every slice rather than re-optimized per slice.</span>
                </p>
            </div>
            """, unsafe_allow_html=True)
# ---------------------------------------------------
# Third tab
# ---------------------------------------------------
with tab3:
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown(
            f"{svg_to_img('glass.svg')} **Pickups Data Preview · {selected_day} {selected_hour}:00**",
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"{svg_to_img('download.svg')} [Download full dataset]({DATA_PATH})",
            unsafe_allow_html=True
        )

    st.dataframe(filtered_pickups.sample(5), width='stretch')

    csv_bytes = filtered_pickups.to_csv(index=False).encode('utf-8')

    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown(f"{svg_to_img('DB.svg')} **Hotzones Summary · {selected_day} {selected_hour}:00**", 
                    unsafe_allow_html=True
        )
    with col2:
        st.markdown(f"{svg_to_img('download.svg')} [Download full dataset]({HOTZONES_PATH})", 
                    unsafe_allow_html=True
        )
    
    st.dataframe(filtered_hotzones, width='stretch')