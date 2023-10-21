import requests
from bs4 import BeautifulSoup
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QListWidget
from PyQt5.QtCore import Qt
import os
import sys

class MovieSuggestionApp(QMainWindow):
    def __init__(self):
        super(MovieSuggestionApp, self).__init__()

        self.setWindowTitle("Movie Suggestion App")
        self.setGeometry(100, 100, 800, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        genre_label = QLabel("Enter a genre (e.g., action, drama, comedy):")
        layout.addWidget(genre_label)

        self.genre_entry = QLineEdit()
        layout.addWidget(self.genre_entry)

        scrape_button = QPushButton("Scrape Movies")
        scrape_button.clicked.connect(self.get_genre_and_scrape)
        layout.addWidget(scrape_button)

        self.result_label = QLabel()
        layout.addWidget(self.result_label)

        self.suggested_list = QListWidget()
        layout.addWidget(self.suggested_list)

        # Add a close button at the bottom
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close_app)
        layout.addWidget(close_button)

        central_widget.setLayout(layout)

    def close_app(self):
        self.close()

    def get_genre_and_scrape(self):
        genre = self.genre_entry.text()
        scrape_and_store_movies(genre, self.result_label, self.suggested_list)

def scrape_and_store_movies(genre, result_label, suggested_list):
    url = f'https://www.imdb.com/search/title/?genres={genre}&sort=user_rating,desc'
    page = requests.get(url)
    if page.status_code != 200:
        result_label.setText("Error: Failed to fetch data from IMDb.")
        return

    soup = BeautifulSoup(page.content, 'html.parser')

    movies = []
    for movie in soup.find_all('div', class_='lister-item-content'):
        title = movie.h3.a.text
        rating = movie.find('div', class_='ratings-bar').strong.text
        link = movie.h3.a['href']
        movies.append({'Title': title, 'Rating': rating, 'Link': f'https://www.imdb.com{link}'})

    if not movies:
        result_label.setText("No movies found for the given genre.")
        return

    df = pd.DataFrame(movies)
    csv_filename = f'{genre}_movies.csv'
    csv_path = os.path.join(os.getcwd(), csv_filename)
    df.to_csv(csv_path, index=False)
    result_label.setText(f"Data scraped and saved as '{csv_filename}' at location:\n{csv_path}")
    suggest_movies(df, suggested_list)

# Function to suggest top-rated movies
def suggest_movies(df, suggested_list):
    suggested_movies = df.head(5)  # Suggest the top 5 highly-rated movies
    suggested_list.clear()
    for index, row in suggested_movies.iterrows():
        suggested_list.addItem(f"{row['Title']} ({row['Rating']})")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MovieSuggestionApp()
    window.show()
    sys.exit(app.exec_())
