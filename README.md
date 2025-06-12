# Club Alpin RSS Feed Server

This is a simple web server that generates RSS feeds from the Club Alpin Français Cannes-Côte d'Azur website. It scrapes the events page and converts it into an RSS feed format.

## Prerequisites

- Python 3.x
- pip (Python package installer)

## Installation

1. Clone this repository or download the files
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the server:
```bash
python3 scrape_to_rss.py
```

The server will start on port 5000.

2. Access the RSS feed by making a GET request to:
```
http://localhost:5000/rss?c=0640&h=c3dc07dc20
```

Required parameters:
- `c`: Club identifier (e.g., "0640")
- `h`: Hash parameter (e.g., "c3dc07dc20")

## Example

Using curl to test the feed:
```bash
curl "http://localhost:5000/rss?c=0640&h=c3dc07dc20"
```

## Error Handling

The server will return:
- 400 Bad Request if the required parameters (`c` and `h`) are missing
- 500 Internal Server Error if there's an error generating the feed
- 200 OK with XML content if successful

## RSS Feed Content

The generated RSS feed includes:
- Title of each event
- Link to the event registration or details page
- Description of the event

## Development

The server is built using:
- Flask for the web server
- BeautifulSoup4 for HTML parsing
- Feedgen for RSS feed generation
- Requests for HTTP requests 