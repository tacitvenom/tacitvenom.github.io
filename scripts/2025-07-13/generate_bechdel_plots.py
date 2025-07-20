#!/usr/bin/env python3
"""
Script to generate interactive Plotly visualizations for Bechdel test analysis of IMDb top movies.
This script reads a CSV file containing movie data and creates interactive visualizations
to be included in Jekyll blog posts.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# Define paths
SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parent.parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
PLOTS_DIR = PROJECT_ROOT / '_includes' / 'plots' / '2025-07-13'

# Ensure plots directory exists
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# TODO: substitute ⛔ with [[1]]
# Define unified color map for all results
COLORS_MAP = {
    'Passes ✅': '#ADEBB3',  # Mint green
    'Controversial 🤔': '#FFEE8C',  # Pastel Yellow
    'Fails ⛔': '#DCA1A1'  # Dusty Rose
}

# Define order for consistency in charts
COLORS_ORDER = list(COLORS_MAP.keys())

PLOT_HEIGHT = 600
PLOT_WIDTH = 700

def load_data():
    """Load the IMDb Bechdel test dataset."""
    csv_path = DATA_DIR / 'imdb_bechdel.csv'
    df = pd.read_csv(csv_path, sep='\t')

    # Clean up the text but preserve the different categories
    df['Pass Bechdel Test?'] = df['Pass Bechdel Test?'].str.strip()
    df['Pass Reverse Bechdel Test?'] = df['Pass Reverse Bechdel Test?'].str.strip()
    df['MovieText'] = df.apply(lambda row: f"#{row['Rank']}: {row['Movie Title'].strip()} ({row['Year of Release']})", axis=1)

    return df

def create_pie_chart(df):
    """Create a pie chart showing Bechdel test counts with all categories and percentages."""
    # Count all the different result categories
    bechdel_counts = df.groupby('Pass Bechdel Test?').agg(
        {
            'Pass Bechdel Test?': 'count',
            'MovieText': list,
        }
    ).rename(columns={
        'Pass Bechdel Test?': 'Count',
        'MovieText': 'Movies'}
    ).reset_index(names='Result')

    # Define a custom sort order to group similar results
    result_order = {category: i for i, category in enumerate(COLORS_ORDER)}

    # Add sort key column and sort
    bechdel_counts['sort_key'] = bechdel_counts['Result'].map(result_order)
    bechdel_counts = bechdel_counts.sort_values('sort_key', ascending=True)

    # Calculate percentages
    total = bechdel_counts['Count'].sum()
    bechdel_counts['Percentage'] = (bechdel_counts['Count'] / total * 100).round(0).astype(int)

    # Create the pie chart with all categories
    fig = px.pie(
        bechdel_counts,
        names='Result',
        values='Count',
        color='Result',
        title="Bechdel Test Results for IMDb Top 25 Movies",
        color_discrete_map=COLORS_MAP,
        custom_data=['Count', 'Percentage'],
        hover_data=None,
        category_orders={'Result': COLORS_ORDER},
    )

    # Create custom text templates with count and percentage
    text_templates = [
        f"<b>{count} movies</b><br>({percentage}%)</br>"
        for count, percentage in zip(bechdel_counts['Count'], bechdel_counts['Percentage'])
    ]

    # Prepare custom hover templates with movie lists
    hover_templates = []
    for _, row in bechdel_counts.iterrows():
        category = row['Result']
        movie_list_html = "<br>".join(row['Movies'])
        hover_template = f"<b>{category}</b><br>Number of Movies: {row['Count']} ({row['Percentage']}%)</br><br><b>Movies in this category:</b><br>{movie_list_html}<extra></extra>"
        hover_templates.append(hover_template)

    fig.update_traces(
        texttemplate=text_templates,
        textfont=dict(size=16, family='Courier New', weight='bold'),
        hovertemplate=hover_templates,
        marker=dict(line=dict(color='#FFFFFF', width=2)),
        textposition='inside',
        hoverlabel=dict(bgcolor='white', font=dict(size=12, family='Courier New')),
    )

    fig.update_layout(
        font=dict(size=16, family="Courier New"),
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=80, b=80),  # Increased top margin for legend
        height=PLOT_HEIGHT,
        title=dict(
            text='Bechdel Test Results for IMDb Top 25 Movies',
            y=0.95,  # Move title position up to make room for legend
            x=0.5,
            xanchor='center',
            font=dict(size=18, family="Courier New", weight='bold'),
        ),
        legend=dict(
            title_font=dict(size=16, family="Courier New", weight='bold'),
            font=dict(size=16, family="Courier New", weight='bold'),
            orientation="h",  # Horizontal legend
            yanchor="bottom",
            y=-0.1,  # Position below the chart
            xanchor="center",
            x=0.5  # Center horizontally
        ),
        legend_traceorder='reversed',
    )

    return fig

def create_comparison_chart(df):
    """Create side-by-side pie charts comparing Bechdel and Reverse Bechdel test results."""

    # Prepare data for Bechdel test
    bechdel = df['Pass Bechdel Test?'].value_counts().reset_index()
    bechdel.columns = ['Result', 'Count']
    bechdel['sort_key'] = bechdel['Result'].map({result: i for i, result in enumerate(COLORS_ORDER)})
    bechdel = bechdel.sort_values('sort_key')
    bechdel['percentage'] = (bechdel['Count'] / bechdel['Count'].sum() * 100).round(0).astype(int)

    # Prepare data for Reverse Bechdel test
    reverse = df['Pass Reverse Bechdel Test?'].value_counts().reset_index()
    reverse.columns = ['Result', 'Count']
    reverse['sort_key'] = reverse['Result'].map({result: i for i, result in enumerate(COLORS_ORDER)})
    reverse = reverse.sort_values('sort_key')
    reverse['percentage'] = (reverse['Count'] / reverse['Count'].sum() * 100).round(0).astype(int)

    # Create subplot layout with 1 row, 2 columns for two pies
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type':'domain'}, {'type':'domain'}]],
    )

    # Add Bechdel Test pie
    fig.add_trace(go.Pie(
        labels=bechdel['Result'],
        values=bechdel['Count'],
        marker=dict(colors=[COLORS_MAP[result] for result in bechdel['Result']]),
        texttemplate='%{value} movies<br>(%{percent})',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>',
        sort=False,
        direction='clockwise'
    ), row=1, col=1)

    # Add Reverse Bechdel Test pie
    fig.add_trace(go.Pie(
        labels=reverse['Result'],
        values=reverse['Count'],
        marker=dict(colors=[COLORS_MAP[result] for result in reverse['Result']]),
        texttemplate='%{value} movies<br>(%{percent})',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>',
        sort=True,
    ), row=1, col=2)

    fig.add_annotation(
        x=0.13,  # x-position roughly centered below first pie (0 to 1 spans whole figure width)
        y=0.1,  # y-position below plot area (adjust negative to move down)
        text="<b>Bechdel Test</b>",
        showarrow=False,
        xref='paper', yref='paper',
        font=dict(size=16, family='Courier New')
    )

    fig.add_annotation(
        x=0.96,  # x-position roughly centered below second pie
        y=0.1,
        text='<b>"Reverse Bechdel" Test</b>',
        showarrow=False,
        xref='paper', yref='paper',
        font=dict(size=16, family='Courier New')
    )
    # Update layout
    fig.update_layout(
        title=dict(
            text='Comparison of Bechdel and "Reverse Bechdel" Test Results',
            y=0.85,
            x=0.5,
            xanchor='center',
            font=dict(size=18, family="Courier New", weight='bold'),
        ),
        # title_text='Comparison of Bechdel and "Reverse Bechdel" Test Results',
        font=dict(size=13, family="Courier New", weight='bold'),
        height=PLOT_HEIGHT,
        margin=dict(l=40, r=40, t=40, b=40),
        legend_title_text=None,
        legend=dict(
            font=dict(size=12, family="Courier New"),
            orientation='h',
            yanchor='bottom',
            y=0.0,
            xanchor='center',
            x=0.5
        ),
        legend_traceorder='reversed',
    )

    return fig

def create_timeline_chart(df):
    """Create a chart showing Bechdel test results over time."""

    # Add decade column
    df['Decade'] = (df['Year of Release'] // 10) * 10
    df['Decade_Label'] = df['Decade'].astype(str) + 's'

    # Group by decade and result category
    decade_data = df.groupby(
        ['Decade', 'Decade_Label', 'Pass Bechdel Test?'],
        observed=False
    ).agg(
        {
            'Pass Bechdel Test?': 'count',
            'MovieText': list,
        }
    ).rename(
        columns={'Pass Bechdel Test?': 'Count', 'MovieText': 'Movies'}
    ).reset_index().rename(columns={'Pass Bechdel Test?': 'Result'})
    decade_data['Movies'] = decade_data['Movies'].apply(lambda x: '<br>'.join(x))
    decade_data['sort_key'] = decade_data['Result'].map({result: i for i, result in enumerate(COLORS_ORDER)})

    # Calculate percentages within each decade
    decade_totals = decade_data.groupby('Decade_Label')['Count'].sum().reset_index()
    decade_data = decade_data.merge(decade_totals, on='Decade_Label', suffixes=('', '_total'))
    decade_data['Percentage'] = (decade_data['Count'] / decade_data['Count_total'] * 100).round(0).astype(int)
    decade_data['Percent'] = decade_data['Percentage'].astype(str) + '%'

    decade_data = decade_data.sort_values(['Decade', 'sort_key'])

    # Create the chart
    fig = px.bar(
        decade_data,
        x='Decade_Label',
        y='Count',
        color='Result',
        title='Bechdel Test Results for IMDb Top 25 Movies by Decade',
        labels={'Decade_Label': 'Decade', 'Count': 'Number of Movies', 'Result': 'Test Result'},
        color_discrete_map=COLORS_MAP,
        category_orders={
            'Decade_Label': sorted(decade_data['Decade_Label'].unique()),
            'Result': COLORS_ORDER
        },
        text='Percent', # Show percentage labels
        custom_data=['Result', 'Count', 'Percentage', 'Movies'] # For hover info
    )
    fig.update_traces(
        hovertemplate="""
        <b>%{customdata[0]} from %{x}</b>
        <br>%{customdata[1]} movie(s)
        <br>%{customdata[2]}%
        <br>
        <b>Movies in this category:</b>
        <br>%{customdata[3]}
        <extra></extra>
        """,
        hoverlabel=dict(align='left', font=dict(size=14, family="Courier New")),
        textposition='inside',
        insidetextanchor='middle',
    )
    fig.update_layout(
        font=dict(size=14, family="Courier New"),
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=80, r=40, t=40, b=120),
        height=PLOT_HEIGHT,
        title=dict(font=dict(size=18, family="Courier New", weight='bold')),
        legend_title=None,
        legend=dict(
            font=dict(size=16, family="Courier New", weight='bold'),
            orientation="h", # Horizontal legend
            yanchor="bottom",
            y=-0.2, # Position below the chart
            xanchor="center",
            x=0.5 # Center horizontally
        ),
        xaxis=dict(
            title_font=dict(size=16, family="Courier New", weight='bold'),
            categoryorder='array',
            categoryarray=sorted(decade_data['Decade_Label'].unique())
        ),
        yaxis=dict(title_font=dict(size=16, family="Courier New", weight='bold')),
    )

    return fig

def save_plot(fig, filename):
    """Save a plotly figure as HTML in the plots directory."""
    output_path = PLOTS_DIR / f"{filename}.html"
    fig.write_html(
        output_path,
        include_plotlyjs='cdn',
        full_html=False,
        config={
            'displayModeBar': True,
            'responsive': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'bechdel_analysis',
                'height': PLOT_HEIGHT,
                'width': PLOT_WIDTH,
                'scale': 2
            }
        }
    )
    print(f"Plot saved to {output_path}")

def main():
    """Main function to generate all plots."""
    print("Loading data...")
    df = load_data()

    print("Generating plots...")
    # Pie chart with percentages
    pie_chart = create_pie_chart(df)
    save_plot(pie_chart, "bechdel_pie_chart")

    # Comparison chart
    comparison_chart = create_comparison_chart(df)
    save_plot(comparison_chart, "bechdel_comparison_chart")

    # Timeline chart
    timeline_chart = create_timeline_chart(df)
    save_plot(timeline_chart, "bechdel_timeline_chart")

    print("All plots generated successfully!")

if __name__ == "__main__":
    main()
