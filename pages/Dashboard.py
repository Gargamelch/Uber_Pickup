import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Load our custom module from utils.py
from utils import (load_data, load_hotzones, load_svg, svg_to_data_uri, svg_to_img, 
                    COLORSCALE, PRIMARY_COLOR, SECONDARY_COLOR, 
                    DATA_PATH, APP_VERSION, WEEKDAY_ORDER)

logo_uri = svg_to_data_uri('Uber_logo_2018.svg', color=PRIMARY_COLOR)



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
            <a href="https://github.com/Gargamelch/Solar_Production" target="_blank" style="
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
tab1, tab2, tab3, tab4 = st.tabs([
    'Overview',
    'Map',
    'Cluster Profiles',
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
            st.markdown(f"{svg_to_img('pred.svg')} **Total Pickups**", unsafe_allow_html=True)
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
            st.markdown(f"{svg_to_img('panel.svg')} **Busiest Combination**", unsafe_allow_html=True)
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

        fig_bar.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig_bar, use_container_width=True)

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
        st.plotly_chart(fig_line, use_container_width=True)



# ---------------------------------------------------
# Second tab
# ---------------------------------------------------
with tab2:

    st.markdown(f"**Pickup Locations · {selected_day} {selected_hour}:00**", unsafe_allow_html=True)

    show_centers = st.checkbox('Show cluster centers', value=True)

    fig_map = px.scatter_map(
        filtered_pickups,
        lat='Lat',
        lon='Lon',
        color=filtered_pickups['cluster_id'].astype(str),
        zoom=10,
        height=650,
        opacity=0.5,
    )
    fig_map.update_traces(marker=dict(size=5))
    fig_map.update_layout(
        legend_title_text='Cluster',
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

    st.plotly_chart(fig_map, use_container_width=True)
# ---------------------------------------------------
# Third tab
# ---------------------------------------------------
with tab3:
    st.markdown("**What makes each cluster different? (all days/hours)**", unsafe_allow_html=True)

    cluster_options = sorted(hotzones_df['cluster_id'].unique())
    selected_cluster = st.selectbox('Select a cluster to inspect', options=cluster_options)

    cluster_hotzones = hotzones_df[hotzones_df['cluster_id'] == selected_cluster]

    pivot = (
        cluster_hotzones
        .pivot_table(index='day', columns='hour', values='count', aggfunc='sum')
        .reindex(WEEKDAY_ORDER)
        .fillna(0)
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown(f"**Cluster {selected_cluster} size**")
        st.metric(
            label='Pickups in this cluster',
            value=f'{int(cluster_hotzones["count"].sum()):,}',
            label_visibility='hidden',
        )

        st.markdown("**All clusters compared (total, all days/hours)**")
        cluster_counts_all = (
            hotzones_df
            .groupby('cluster_id')['count']
            .sum()
            .reset_index()
            .sort_values('cluster_id')
        )
        fig_compare = px.bar(
            cluster_counts_all,
            x='count',
            y='cluster_id',
            orientation='h',
            color='cluster_id',
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_compare.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig_compare, use_container_width=True)

    with col2:
        st.markdown(f"**Cluster {selected_cluster} · Hour of Day × Day of Week**")
        fig_heatmap = px.imshow(
            pivot,
            color_continuous_scale=COLORSCALE,
            aspect='auto',
            labels=dict(x='Hour of Day', y='Day of Week', color='Pickups'),
        )
        fig_heatmap.update_layout(height=350)
        st.plotly_chart(fig_heatmap, use_container_width=True)

    info_icon = svg_to_img('info.svg', color=PRIMARY_COLOR, width=20)
    st.markdown(f"""
        <div style="
            background-color: rgba(15, 21, 37, 1);
            border-left: 3px solid {PRIMARY_COLOR};
            border-radius: 0 8px 8px 0;
            padding: 15px 20px;
            margin: 15px 0 0 0;
        ">
            <p style="margin: 0; font-size: 1rem; line-height: 1.6;">
                {info_icon} <strong>Note:</strong>
                <span style="color: #aaa;">This tab shows activity across all days and hours regardless of the sidebar filter, so you can see each cluster's full time-based pattern (commute, nightlife, etc).</span>
            </p>
        </div>
    """, unsafe_allow_html=True)

      


# ---------------------------------------------------
# Fourth tab
# ---------------------------------------------------
with tab4:
    st.markdown(f"{svg_to_img('glass.svg')} **Pickups Data Preview · {selected_day} {selected_hour}:00**", unsafe_allow_html=True)
    st.dataframe(filtered_pickups.head(1000), use_container_width=True)

    csv_bytes = filtered_pickups.to_csv(index=False).encode('utf-8')
    st.download_button(
        label='Download filtered pickups as CSV',
        data=csv_bytes,
        file_name=f'pickups_{selected_day}_{selected_hour}h.csv',
        mime='text/csv',
    )

    st.markdown(f"{svg_to_img('DB.svg')} **Hotzones Summary · Same Slot**", unsafe_allow_html=True)
    st.dataframe(filtered_hotzones, use_container_width=True)

    st.markdown(f"{svg_to_img('info.svg', color=PRIMARY_COLOR, width=20)} **Method**", unsafe_allow_html=True)
    st.markdown("""
    Clusters were generated from raw pickup latitude/longitude coordinates.
    `hotzones_summary_df` is a pre-aggregated table of pickup counts per
    cluster, per day of week, and per hour of day, alongside each cluster's
    center coordinates. The sidebar lets you pick one specific day + hour
    slot; the Overview, Map, and Data tabs all show that slice, while
    Cluster Profiles shows each cluster's full time-based pattern.
    """)