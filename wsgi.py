"""WSGI entry point for the Club Alpin RSS Feed Server."""

from scrape_to_rss import app

if __name__ == "__main__":
    app.run()
