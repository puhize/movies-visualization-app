import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Load data
df = pd.read_csv('imdb_top_1000.csv')

# Data cleaning
df.dropna(subset=['Gross'], inplace=True)
df['Certificate'] = df['Certificate'].fillna(df["Certificate"].mode()[0])
df['Meta_score'] = df['Meta_score'].fillna(df["Meta_score"].mode()[0])
df["Runtime"] = df["Runtime"].str.replace(' min', '')
df['Gross'] = df['Gross'].str.replace(',', '')

# Convert columns to appropriate data types
df["Runtime"] = df["Runtime"].astype(int)
df['Gross'] = df['Gross'].astype(int)
df = df.drop(df[df['Released_Year'] == 'PG'].index)
df['Released_Year'] = df['Released_Year'].astype(int)
df['Meta_score'] = df['Meta_score'].astype(int)
df['Gross'] = df['Gross'].astype(int)

# Split genres and get unique genres
unique_genres = set()
df['Genre'] = df['Genre'].apply(lambda x: x.split(', '))
df['Genre'].apply(lambda genres: [unique_genres.add(genre) for genre in genres])
unique_genres = sorted(unique_genres)


# Function to create visualizations
# Function to create visualizations
def create_visualization(df, chart_type, x_col, y_col, color_col=None):
    if chart_type == 'Bar Chart':
        fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=f'{y_col} by {x_col}',
                     labels={x_col: x_col, y_col: y_col})
    elif chart_type == 'Scatter Plot':
        fig = px.scatter(df, x=x_col, y=y_col, color=color_col, title=f'{y_col} vs {x_col}',
                         labels={x_col: x_col, y_col: y_col})
    elif chart_type == 'Histogram':
        fig = px.histogram(df, x=x_col, color=color_col, title=f'{y_col} distribution',
                           labels={x_col: x_col, 'count': 'Frequency'})
    elif chart_type == 'Box Plot':
        fig = px.box(df, x=x_col, y=y_col, color=color_col, title=f'{y_col} by {x_col}',
                     labels={x_col: x_col, y_col: y_col})
    elif chart_type == 'Pie Chart':
        fig = px.pie(df, values=y_col, names=x_col, color=color_col, title=f'{y_col} by {x_col}',
                     labels={x_col: x_col, y_col: y_col})
        fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig


# Function to create the top 10 grossing movies chart
def create_top_grossing_chart(df):
    grouped = df.groupby("Series_Title")["Gross"].mean().reset_index()
    mean1 = grouped.sort_values("Gross", ascending=False).head(10)
    fig = px.bar(mean1, x="Series_Title", y="Gross", title="Top 10 Movies by Gross",
                 labels={"Series_Title": "Movie Title", "Gross": "Gross Revenue"},
                 color="Gross", color_continuous_scale="Viridis")
    return fig


# Function to create the box office over years visualization
def create_box_office_over_years_plot(df):
    yearly_gross = df.groupby('Released_Year')['Gross'].sum().reset_index()
    fig = px.line(yearly_gross, x='Released_Year', y='Gross', title='Box Office Earnings Over the Years',
                  labels={'Released_Year': 'Year', 'Gross': 'Gross Revenue'})
    return fig


# Function to create the top 20 movie genres chart
def create_top_genres_chart(df):
    genre_count = df['Genre'].explode().value_counts().head(20).reset_index()
    genre_count.columns = ['Genre', 'Count']
    fig = px.bar(genre_count, x='Genre', y='Count', title='Top 20 Movie Genres',
                 labels={'Genre': 'Genre', 'Count': 'Number of Movies'}, color='Count',
                 color_continuous_scale='Viridis')
    return fig


# Function to display movies with posters
def display_movies_with_posters(df):
    for index, row in df.iterrows():
        st.image(row['Poster_Link'], width=150, caption=row['Series_Title'])
        st.write(f"**{row['Series_Title']} ({row['Released_Year']})**")
        st.write(f"IMDB Rating: {row['IMDB_Rating']}")
        st.write(f"Genre: {', '.join(row['Genre'])}")
        st.write(f"Gross: ${row['Gross']:,}")
        st.write("---")


# Main function for Streamlit app
def main():
    st.set_page_config(page_title="Movie Dataset Visualization", layout="wide")

    # Title and description
    st.title("Movie Dataset Visualization Dashboard")
    st.markdown("""
    This dashboard allows you to visualize and explore a movie dataset. 
    Use the filters in the sidebar to create various types of charts.
    """)

    # Summary metrics
    st.header("Summary Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Movies", f"{df['Series_Title'].nunique():,}")
    col2.metric("Total Votes", f"{df['No_of_Votes'].sum():,}")
    col3.metric("Average IMDB Rating", f"{df['IMDB_Rating'].mean():.2f}")
    col4.metric("Total Gross", f"${df['Gross'].sum():,}")

    # Display the dataset table
    # Prepare the dataframe for display
    display_df = df.drop(columns=['Poster_Link'])
    display_df['Released_Year'] = display_df['Released_Year'].astype(str).str.replace(",", "")

    # Display the dataset table
    st.header("Dataset")
    st.dataframe(display_df)

    # Sidebar filters
    st.sidebar.title("Filters")
    selected_genres = st.sidebar.multiselect("Select Genre(s)", options=unique_genres, default=unique_genres)
    years = st.sidebar.slider("Select Released Year Range", int(df['Released_Year'].min()),
                              int(df['Released_Year'].max()),
                              (int(df['Released_Year'].min()), int(df['Released_Year'].max())))
    rating = st.sidebar.slider("Select IMDB Rating Range", float(df['IMDB_Rating'].min()),
                               float(df['IMDB_Rating'].max()),
                               (float(df['IMDB_Rating'].min()), float(df['IMDB_Rating'].max())))

    # Filter data based on selections
    filtered_df = df[df['Genre'].apply(lambda genres: any(genre in selected_genres for genre in genres))]
    filtered_df = filtered_df[(filtered_df['Released_Year'].between(years[0], years[1])) & (
        filtered_df['IMDB_Rating'].between(rating[0], rating[1]))]

    # Search bar in the main part of the dashboard
    search_query = st.text_input("Search for a movie")

    # Search functionality
    if search_query:
        search_results = df[df['Series_Title'].str.contains(search_query, case=False)]
        if not search_results.empty:
            st.header(f"Search Results for '{search_query}'")
            display_movies_with_posters(search_results)
        else:
            st.write(f"No movies found for '{search_query}'")

    # Sidebar for chart type and axes selection
    chart_type = st.sidebar.selectbox("Select Chart Type",
                                      ['Bar Chart', 'Scatter Plot', 'Histogram', 'Box Plot', 'Pie Chart'])
    x_col = st.sidebar.selectbox("Select X-Axis", df.columns.drop(['Poster_Link']))
    y_col = st.sidebar.selectbox("Select Y-Axis", df.columns.drop(['Poster_Link']))
    color_col = st.sidebar.selectbox("Select Color (Optional)", [None] + list(df.columns.drop(['Poster_Link'])),
                                     index=0)


    # Display multiple visualizations
    st.header("Visualizations")
    # First column
    col1, col2 = st.columns([1, 1])
    with col1:
        # Create and display charts
        st.subheader("Top 10 Movies by Gross")
        top_grossing_fig = create_top_grossing_chart(df)
        st.plotly_chart(top_grossing_fig, use_container_width=True)

        st.subheader("Top 20 Movie Genres")
        top_genres_fig = create_top_genres_chart(df)
        st.plotly_chart(top_genres_fig, use_container_width=True)

    with col2:
        st.subheader("Box Office Earnings Over The Years")
        box_office_fig = create_box_office_over_years_plot(df)
        st.plotly_chart(box_office_fig, use_container_width=True)

        # 10 directors most rated
        st.subheader("Top 10 Most Voted Directors")

        # Group by Director and calculate average IMDb rating
        grouped_directors = df.groupby("Director")["IMDB_Rating"].mean().reset_index()

        # Sort by IMDb rating descending and select top 10 directors
        top_directors = grouped_directors.sort_values(by="IMDB_Rating", ascending=False).head(10)

        fig = px.bar(top_directors, x='IMDB_Rating', y='Director', orientation='h',
                     title='Top 10 Directors by Average IMDb Rating',
                     labels={'IMDB_Rating': 'Average IMDb Rating', 'Director': 'Director'},
                     color='IMDB_Rating', color_continuous_scale='Viridis',
                     text=top_directors['IMDB_Rating'].round(2),  # Display IMDb rating inside bars
                     )

        # Customize layout and appearance
        # fig.update_layout(plot_bgcolor='rgb(30, 30, 30)', paper_bgcolor='rgb(30, 30, 30)',
        #                   font_color='white', title_font_color='white')

        st.plotly_chart(fig)

    # Additional content
    st.header("Additional Insights")
    # Example of additional content (you can add more as needed)
    st.subheader("Genre Distribution")
    genre_distribution = df['Genre'].explode().value_counts().reset_index()
    genre_distribution.columns = ['Genre', 'Count']  # Rename columns for clarity
    st.bar_chart(genre_distribution, x='Genre', y='Count', color='Genre', height=400)

    # Adjusted code for rating distribution histogram
    st.subheader("Rating Distribution")
    fig_rating = px.histogram(df, x='IMDB_Rating', nbins=20, color='IMDB_Rating', title='Distribution of IMDB Ratings')
    st.plotly_chart(fig_rating)

    if st.sidebar.button('Create Chart'):
        fig = create_visualization(filtered_df, chart_type, x_col, y_col, color_col)
        st.plotly_chart(fig, use_container_width=True)

    # Additional styling
    st.markdown(
        """
        <style>
        .stButton button {
            background-color: #4CAF50 !important;
            color: white !important;
            border-radius: 12px !important;
        }
        .stDataFrame {
            border: 1px solid #ddd !important;
            border-radius: 4px !important;
        }
        body {
            background-color: #1E1E1E;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
