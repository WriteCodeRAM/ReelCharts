import streamlit as st
import requests
import pandas as pd  # Gio to implente tables feature
import numpy as np
from config import Config


def get_genres():
    url = "https://api.themoviedb.org/3/genre/movie/list?language=en-US"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {Config.API_KEY}"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return data['genres']


def get_movies(filter_type, release_year=None, genres=None, search_query=None, vote_average_range=None):
    filters = {
        'Popular': 'popular',
        'Now Playing': 'now_playing',
        'Top Rated': 'top_rated',
        'Upcoming': 'upcoming'
    }

    genre_ids = [genre['id'] for genre in genres] if genres else None
    genre_query = f'&with_genres={",".join(str(id) for id in genre_ids)}' if genre_ids else ''

    if search_query:
        url = f"https://api.themoviedb.org/3/search/movie?language=en-US&query={search_query}&page=1"
    else:
        url = f"https://api.themoviedb.org/3/movie/{filters[filter_type]}?language=en-US&page=1{genre_query}"
        if release_year:
            url += f"&year={release_year}"  # Add release year as a filter
        if vote_average_range:
            url += f"&vote_average.gte={vote_average_range[0]}&vote_average.lte={vote_average_range[1]}"  # Add vote average range as a filter

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {Config.API_KEY}"
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    return data['results']


def main():
    st.title('Reel Charts')

    st.sidebar.title('Charts')
    # Sidebar options
    selected_option = st.sidebar.selectbox("Select a chart", ["Home", "Box Office", "Upcoming Movies", "Movie Table", "Map"])

    def get_selected_genres():
        all_genres = get_genres()
        genre_names = [genre['name'] for genre in all_genres]
        selected_genres = st.sidebar.multiselect('Select Genres', genre_names)
        selected_genre_ids = [genre['id'] for genre in all_genres if genre['name'] in selected_genres]
        selected_genres = [{'id': genre_id, 'name': genre_name} for genre_id, genre_name in
                           zip(selected_genre_ids, selected_genres)]
        return selected_genres

    # home page filters
    if selected_option == 'Home':
        filter_type = st.radio('What movies would you like to see?',
                               ['Popular', 'Now Playing', 'Top Rated', 'Upcoming'])
        search_query = st.text_input("Search by movie title")
        release_year = st.number_input("Filter by release year", min_value=1990, max_value=2023, step=1,
                                       value=2023)  # Set default value to 2023
        vote_average_range = st.slider("Filter by vote average range", min_value=0.0, max_value=10.0,
                                       value=(0.0, 10.0), step=0.1)  # Slider widget for vote average range



        # Dynamically change the header based on the selected filter type
        header_text = filter_type + " Movies"
        st.header(header_text)

        # Clear Filters button
        if st.button("Clear Filters"):
            search_query = None
            release_year = 2023
            vote_average_range = (0.0, 10.0)
            genres = None

        columns = st.columns(3)
        genres = get_selected_genres()

        movies = get_movies(filter_type, release_year, genres, search_query, vote_average_range)

        # creates home page columns with movie posters
        for i, movie in enumerate(movies):
            with columns[i % 3]:
                poster_url = f'https://image.tmdb.org/t/p/w200{movie["poster_path"]}'
                st.image(poster_url, width=200)
                st.write(movie['title'])


    # Gio code start
    if selected_option == "Movie Table":

        #Movie seach name table
        st.title("TMDB Movie Search")

        TMDB_URL = "https://api.themoviedb.org/3/search/movie"
        API_KEY = "9bc1882d52cb1a350bd25fb47aa8ff26"

        def fetch_movies(query):
            params = {
                'api_key': API_KEY,
                'query': query
            }

            response = requests.get(TMDB_URL, params=params)
            data = response.json()

            if data and 'results' in data:
                return data['results']
            else:
                return []

        query = st.text_input("Enter movie name:", value='').strip()

        if query:
            movies = fetch_movies(query)

            if movies:
                # Convert the results into a pandas DataFrame for display
                df = pd.DataFrame(movies)
                st.write(df[["title", "release_date", "overview", "popularity", "vote_average"]])
                st.success(f'Data results for "{query}" ✅')
            else:
                ##t.write("No movies found!")
                st.error(f'No movies found for "{query}" 🚨')

                ##COMPLETE

        # Gio Code end

    # Nageline Code
    if selected_option == "Map":
        def get_movie_providers_by_country(country):
            url = f'https://api.themoviedb.org/3/watch/providers/movie?watch_region={country}'
            headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {Config.API_KEY}"
            }
            response = requests.get(url, headers=headers)
            data = response.json()
            return data['results']

        st.title('Movie Providers by Country')

        # Input field to enter the country
        country = st.text_input('Enter a country name or ISO code (e.g., "United States" or "US"):')

        # Get movie providers
        if country:
            movie_providers = get_movie_providers_by_country(country)

            if not movie_providers:
                st.warning(f"No movie providers found for {country}.")
            else:
                st.header(f"Movie Providers in {country}:")
                df = pd.DataFrame(movie_providers)
                st.dataframe(df[['provider_name', 'provider_id']])

                # Count the number of movie providers
                num_providers = len(movie_providers)
                st.write(f"Number of movie providers in {country}: {num_providers}")

            # new shit
            # Step 1: Read the CSV file
            csv_file = 'countries.csv'
            df = pd.read_csv(csv_file)

            # Step 2: Create a Streamlit app
            st.title('Country Map Viewer')

            # Get the latitude and longitude for the selected country
            latitude = df.loc[df['country'] == country, 'latitude'].values[0]
            longitude = df.loc[df['country'] == country, 'longitude'].values[0]

            # Display the selected country's location on the map
            st.map(data=[[latitude, longitude]], zoom=5)

            st.map(df)

if __name__ == '__main__':
    main()
