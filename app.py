import streamlit as st
import requests


def main():
    st.title('Reel Charts')

    st.sidebar.title('Charts')
    selected_option = st.sidebar.selectbox("Select a chart", ["Home", "Box Office", "Upcoming Movies"])

    def get_movies(filter_type, release_year=None, search_query=None):
        filters = {
            'Popular': 'popular',
            'Now Playing': 'now_playing',
            'Top Rated': 'top_rated',
            'Upcoming': 'upcoming'
        }

        if search_query:
            url = f"https://api.themoviedb.org/3/search/movie?language=en-US&query={search_query}&page=1"
        else:
            url = f"https://api.themoviedb.org/3/movie/{filters[filter_type]}?language=en-US&page=1"

        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwOTVlNzIxYjA5ZWFkZjZjMTJjNzU5OTU1M2QyZDAyNiIsInN1YiI6IjY0NDA2MDljYzk5NWVlMDUzNjdjNWM5YyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.OP6U2o7e-MhiswrP8csW80J6a7yr5Z9LBU1bWoSHCv8"
        }

        response = requests.get(url, headers=headers)
        data = response.json()
        return data['results']

    if selected_option == 'Home':
        filter_type = st.radio('What movies would you like to see?',
                               ['Popular', 'Now Playing', 'Top Rated', 'Upcoming'])
        search_query = st.text_input("Search by Movie Title")

        # Clear release_year input if a search query is entered
        if search_query:
            release_year = None
        else:
            release_year = st.number_input("Filter by release year", min_value=1990, max_value=2023, step=1)

        movies = get_movies(filter_type, release_year, search_query)

        st.header('Popular Movies')

        columns = st.columns(3)

        for i, movie in enumerate(movies):
            with columns[i % 3]:
                poster_url = f'https://image.tmdb.org/t/p/w200{movie["poster_path"]}'
                st.image(poster_url, width=200)
                st.write(movie['title'])


if __name__ == '__main__':
    main()
