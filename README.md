# Club Alpin RSS Feed Server

This is a simple web server that generates RSS feeds from the Club Alpin Français Cannes-Côte d'Azur website. It scrapes the events page and converts it into an RSS feed format.

## Purpose

The main purpose of this server is to provide real-time notifications when new climbing/canyoning outings are published on the club's website. This is achieved by:

1. Converting the club's event page into an RSS feed
2. Using IFTTT (If This Then That) to monitor the RSS feed
3. Automatically sending email notifications when new outings are detected

This setup ensures you never miss a new outing opportunity, as you'll receive an email notification as soon as it's published on the club's website.

## Prerequisites

- Python 3.x
- pip (Python package installer)
- systemd (for running as a service)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/pbeaudequin/clubalpin_rss.git
cd clubalpin_rss
```

2. Run the setup script to create a virtual environment and install dependencies:
```bash
./setup.sh
```

3. Install and enable the systemd service:
```bash
./install_service.sh
```

The service will be installed and started automatically. It will also be configured to start at system boot.

## Development

### Manual Usage

#### Development Server

For development purposes, you can run the Flask development server:

1. Activate the virtual environment:
```bash
source venv/bin/activate
```

2. Start the development server:
```bash
python scrape_to_rss.py
```

#### Production Server

For production use, the service uses Gunicorn as the WSGI server. You can also run it manually:

1. Activate the virtual environment:
```bash
source venv/bin/activate
```

2. Start the production server:
```bash
gunicorn --workers 1 --bind 0.0.0.0:9191 wsgi:app
```

The server will start on port 9191.

## Accessing the RSS Feed

Access the RSS feed by making a GET request to:
```
http://localhost:9191/rss?c=0640&h=c3dc07dc20
```

Required parameters:
- `c`: Club identifier (e.g., "0640")
- `h`: Hash parameter (e.g., "c3dc07dc20")

## Service Management

Once installed as a service, you can manage it using systemd commands:

- Check status:
```bash
sudo systemctl status clubalpin_rss
```

- Stop the service:
```bash
sudo systemctl stop clubalpin_rss
```

- Start the service:
```bash
sudo systemctl start clubalpin_rss
```

- Restart the service:
```bash
sudo systemctl restart clubalpin_rss
```

- View logs:
```bash
sudo journalctl -u clubalpin_rss
```

## Error Handling

The server will return:
- 400 Bad Request if the required parameters (`c` and `h`) are missing
- 500 Internal Server Error if there's an error generating the feed
- 200 OK with XML content if successful

## RSS Feed Content

The generated RSS feed includes:
- Title of each event
- Date and time of the event
- Link to the event registration or details page
- Full description of the event from the detail page

## Development

The server is built using:
- Flask for the web framework
- Gunicorn as the production WSGI server
- BeautifulSoup4 for HTML parsing
- Feedgen for RSS feed generation
- Requests for HTTP requests

## Project Structure

```
clubalpin_rss/
├── scrape_to_rss.py      # Main server code
├── wsgi.py              # WSGI entry point
├── requirements.txt      # Python dependencies
├── setup.sh             # Virtual environment setup script
├── install_service.sh   # Service installation script
├── clubalpin_rss.service # systemd service file
└── README.md            # This file
```
