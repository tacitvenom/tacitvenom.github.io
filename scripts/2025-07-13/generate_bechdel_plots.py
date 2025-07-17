#!/usr/bin/env python3
"""
Script to generate interactive Plotly visualizations for Bechdel test analysis of IMDb top movies.
This script reads a CSV file containing movie data and creates interactive visualizations
to be included in Jekyll blog posts.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from plotly.subplots import make_subplots

# Define paths
SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parent.parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
PLOTS_DIR = PROJECT_ROOT / '_includes' / 'plots' / '2025-07-13'

# Ensure plots directory exists
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

def load_data():
    """Load the IMDb Bechdel test dataset."""
    csv_path = DATA_DIR / 'imdb_bechdel.csv'
    df = pd.read_csv(csv_path, sep='\t')

    # Clean up the text but preserve the different categories
    df['Pass Bechdel Test?'] = df['Pass Bechdel Test?'].str.strip()
    df['Pass Reverse Bechdel Test?'] = df['Pass Reverse Bechdel Test?'].str.strip()

    return df

def create_pie_chart(df):
    """Create a pie chart showing Bechdel test counts with all categories and percentages."""
    # Count all the different result categories
    bechdel_counts = df['Pass Bechdel Test?'].value_counts().reset_index()
    bechdel_counts.columns = ['Result', 'Count']

    # Define a custom sort order to group similar results
    result_order = {
        '✅ Passes': 1,
        '✅ Passes (dubiously)': 2,
        '✅ Barely passes': 3,
        '❌ Fails': 4
    }

    # Add sort key column and sort
    bechdel_counts['sort_key'] = bechdel_counts['Result'].map(result_order)
    bechdel_counts = bechdel_counts.sort_values('sort_key')

    # Calculate percentages
    total = bechdel_counts['Count'].sum()
    bechdel_counts['Percentage'] = (bechdel_counts['Count'] / total * 100).round(1)

    # Create a custom color map for all categories
    color_map = {
        '✅ Passes': '#2ca02c',  # Strong green
        '✅ Passes (dubiously)': '#7fba3c',  # Light green
        '✅ Barely passes': '#b5d96c',  # Very light green
        '❌ Fails': '#d62728'  # Red
    }

    # Create the pie chart with all categories
    fig = px.pie(
        bechdel_counts,
        names='Result',
        values='Count',
        color='Result',
        title='Bechdel Test Results for IMDb Top 25 Movies',
        color_discrete_map=color_map,
        custom_data=['Count', 'Percentage'],
        hover_data=None
    )

    # Update hover template to show count and percentage
    # Create fully custom text labels with count and percentage
    custom_text = [f"{count} movies ({percentage}%)" for count, percentage in zip(bechdel_counts['Count'], bechdel_counts['Percentage'])]

    fig.update_traces(
        textinfo='text',
        text=custom_text,
        hovertemplate='<b>%{label}</b><br>Number of Movies: %{value}<extra></extra>'
    )

    fig.update_layout(
        font=dict(size=14),
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=60, b=40),
        height=500,
        legend=dict(
            title_font=dict(size=16),
            font=dict(size=14)
        )
    )

    return fig

def create_comparison_chart(df):
    """Create a side-by-side comparison of Bechdel and Reverse Bechdel test results."""
    # Create a simplified version for comparison (just Pass/Fail)
    df_simplified = df.copy()
    df_simplified['Bechdel_Simple'] = df_simplified['Pass Bechdel Test?'].apply(
        lambda x: 'Pass' if '✅' in str(x) else 'Fail'
    )
    df_simplified['Reverse_Simple'] = df_simplified['Pass Reverse Bechdel Test?'].apply(
        lambda x: 'Pass' if '✅' in str(x) else 'Fail'
    )

    # Count for Bechdel test (simplified)
    bechdel = df_simplified['Bechdel_Simple'].value_counts().reset_index()
    bechdel.columns = ['Result', 'Count']
    bechdel = bechdel.sort_values('Result', ascending=False)  # Sort so 'Pass' comes first
    bechdel['Test'] = 'Bechdel Test'

    # Count for Reverse Bechdel test (simplified)
    reverse = df_simplified['Reverse_Simple'].value_counts().reset_index()
    reverse.columns = ['Result', 'Count']
    reverse = reverse.sort_values('Result', ascending=False)  # Sort so 'Pass' comes first
    reverse['Test'] = 'Reverse Bechdel Test'

    # Combine data
    combined = pd.concat([bechdel, reverse])

    # Create the grouped bar chart
    fig = px.bar(
        combined,
        x='Test',
        y='Count',
        color='Result',
        barmode='group',
        title='Comparison of Bechdel and Reverse Bechdel Test Results',
        labels={'Test': 'Test Type', 'Count': 'Number of Movies', 'Result': 'Test Result'},
        color_discrete_map={'Pass': '#2ca02c', 'Fail': '#d62728'}
    )

    # Update hover template
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Result: %{color}<br>Number of Movies: %{y}<extra></extra>'
    )

    fig.update_layout(
        font=dict(size=14),
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=60, b=40),
        height=500,
        legend=dict(
            title_font=dict(size=16),
            font=dict(size=14)
        ),
        xaxis=dict(title_font=dict(size=16)),
        yaxis=dict(title_font=dict(size=16))
    )

    return fig

def create_timeline_chart(df):
    """Create a chart showing Bechdel test results over time."""
    # Create a simplified version for the timeline
    df_timeline = df.copy()
    df_timeline['Bechdel_Simple'] = df_timeline['Pass Bechdel Test?'].apply(
        lambda x: 'Pass' if '✅' in str(x) else 'Fail'
    )

    # Add decade column
    df_timeline['Decade'] = (df_timeline['Year of Release'] // 10) * 10
    df_timeline['Decade_Label'] = df_timeline['Decade'].astype(str) + 's'

    # Ensure Decade is ordered correctly
    df_timeline['Decade'] = pd.Categorical(df_timeline['Decade'],
                                         categories=sorted(df_timeline['Decade'].unique()),
                                         ordered=True)

    # Group by decade and simplified test result
    decade_data = df_timeline.groupby(['Decade', 'Decade_Label', 'Bechdel_Simple']).size().reset_index(name='Count')

    # Create the chart
    fig = px.bar(
        decade_data,
        x='Decade_Label',
        y='Count',
        color='Bechdel_Simple',
        title='Bechdel Test Results by Decade',
        labels={'Decade_Label': 'Decade', 'Count': 'Number of Movies', 'Bechdel_Simple': 'Test Result'},
        color_discrete_map={'Pass': '#2ca02c', 'Fail': '#d62728'},
        category_orders={'Decade_Label': sorted(decade_data['Decade_Label'].unique())}
    )

    # Update hover template
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Result: %{color}<br>Number of Movies: %{y}<extra></extra>'
    )

    fig.update_layout(
        font=dict(size=14),
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=60, b=40),
        height=500,
        legend=dict(
            title_font=dict(size=16),
            font=dict(size=14)
        ),
        xaxis=dict(
            title_font=dict(size=16),
            categoryorder='array',
            categoryarray=sorted(decade_data['Decade_Label'].unique())
        ),
        yaxis=dict(title_font=dict(size=16))
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
                'height': 500,
                'width': 700,
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
    save_plot(pie_chart, "bechdel_bar_chart")

    # Comparison chart
    comparison_chart = create_comparison_chart(df)
    save_plot(comparison_chart, "bechdel_comparison_chart")

    # Timeline chart
    timeline_chart = create_timeline_chart(df)
    save_plot(timeline_chart, "bechdel_timeline_chart")

    print("All plots generated successfully!")

if __name__ == "__main__":
    main()
