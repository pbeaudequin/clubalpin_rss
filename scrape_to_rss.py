import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from flask import Flask, Response, request
from flask_caching import Cache

app = Flask(__name__)
cache = Cache(
    app,
    config={
        "CACHE_TYPE": "SimpleCache",
        "CACHE_DEFAULT_TIMEOUT": 600,  # 10 minutes in seconds
    },
)


def parse_date(date_text):
    # Handle different date formats
    # Format 1: "le DD/MM/YYYY de HH:MM à HH:MM"
    # Format 2: "du DD/MM/YYYY à HH:MM au DD/MM/YYYY à HH:MM"

    # Try format 1
    single_day = re.search(
        r"le (\d{2}/\d{2}/\d{4}) de (\d{2}:\d{2}) à (\d{2}:\d{2})", date_text
    )
    if single_day:
        date_str = single_day.group(1)
        start_time = single_day.group(2)
        dt = datetime.strptime(f"{date_str} {start_time}", "%d/%m/%Y %H:%M")
        # Add timezone info (France is UTC+1 or UTC+2 depending on DST)
        # For simplicity, we'll use UTC+1
        return dt.replace(tzinfo=timezone(timedelta(hours=1)))

    # Try format 2
    date_range = re.search(r"du (\d{2}/\d{2}/\d{4}) à (\d{2}:\d{2})", date_text)
    if date_range:
        date_str = date_range.group(1)
        start_time = date_range.group(2)
        dt = datetime.strptime(f"{date_str} {start_time}", "%d/%m/%Y %H:%M")
        # Add timezone info (France is UTC+1 or UTC+2 depending on DST)
        # For simplicity, we'll use UTC+1
        return dt.replace(tzinfo=timezone(timedelta(hours=1)))

    return None


def get_event_description(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the first div with class bloc-contenu
        content_div = soup.find("div", class_="bloc-contenu")
        if content_div:
            # Get all text content, preserving line breaks
            description = []
            for element in content_div.stripped_strings:
                description.append(element)
            return "\n".join(description)

    except Exception as e:
        print(f"Error fetching description from {url}: {str(e)}")

    return None


@cache.memoize(timeout=600)
def generate_rss(c, h):
    # Construct URL with parameters
    base_url = "https://extranet-clubalpin.com/app/out/out.php"
    URL = f"{base_url}?c={c}&s=12&h={h}&section=init&pratique=CA&statut=AU+PLANNING&responsable="

    # Fetch the page
    response = requests.get(URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Prepare RSS feed
    fg = FeedGenerator()
    fg.title("Club Alpin Français Cannes-Côte d'Azur - Agenda des sorties clubs")
    fg.link(href=URL, rel="alternate")
    fg.description(
        "Agenda des sorties clubs (Canyonisme) - Club Alpin Français Cannes-Côte d'Azur"
    )
    # Set feed last updated time to now with timezone
    fg.updated(datetime.now(timezone.utc))

    # Find all event blocks (each event is in a div with class 'sortie')
    events = soup.find_all("div", class_="sortie")

    for event in events:
        # Extract event title from the intitule div
        title_elem = event.find("div", class_="intitule")
        if title_elem:
            title = title_elem.get_text(strip=True)

            # Extract date information
            date_text = None
            for text in event.stripped_strings:
                if text.startswith("le ") or text.startswith("du "):
                    date_text = text
                    break

            # Parse the date
            event_date = None
            if date_text:
                event_date = parse_date(date_text)

            # Find the registration link
            link = None
            registration_link = event.find("a", class_="packClub")
            if registration_link and "href" in registration_link.attrs:
                link = registration_link["href"]

            # If no registration link found, try to find the detail link
            if not link:
                detail_link = event.find("a", class_="lienDetail")
                if detail_link and "data-sortie-id" in detail_link.attrs:
                    sortie_id = detail_link["data-sortie-id"]
                    link = f"https://extranet-clubalpin.com/app/out/out.php?s=6&c={sortie_id}"

            # If still no link found, use the main URL
            if not link:
                link = URL

            # Get the event description
            description = get_event_description(link)

            # Add the entry to the feed
            fe = fg.add_entry()
            fe.title(title)
            fe.link(href=link)

            # Build the description
            desc_parts = [title]
            if date_text:
                desc_parts.append(f"Date: {date_text}")
            if description:
                desc_parts.append("\nDescription:")
                desc_parts.append(description)

            fe.description("\n".join(desc_parts))

            # Add the date if available
            if event_date:
                fe.pubDate(event_date)
                fe.updated(event_date)

    return fg.rss_str(pretty=True)


@app.route("/rss")
@app.route("/clubalpin_rss")
def rss_feed():
    # Get parameters from request
    c = request.args.get("c")
    h = request.args.get("h")

    if not c or not h:
        return "Missing required parameters 'c' and 'h'", 400

    try:
        rss_content = generate_rss(c, h)
        return Response(rss_content, mimetype="application/xml")
    except Exception as e:
        return f"Error generating RSS feed: {str(e)}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
