from flask import Flask, request, render_template, render_template_string, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = Flask(__name__)

# Function to fetch the page content (HTML) of a webpage
def fetch_page_content(url):
    try:
        # Attempt to fetch the content from the external URL
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request was successful
        return response.text
    except requests.exceptions.RequestException as e:
        # Return a user-friendly error message if fetching fails
        return f"Sorry, we couldn't load the requested page. Please try again later."

@app.route('/')
def home():
    # Search page with simple search form
    return render_template('index.html')

@app.route('/fetch', methods=['GET'])
def fetch_page():
    # Get URL from user input
    url = request.args.get('url')
    
    if not url:
        return jsonify({"error": "URL is required!"}), 400

    # Fetch the page content
    page_content = fetch_page_content(url)
    
    # If there's an error fetching the page, return the error message
    if page_content.startswith("Sorry"):
        return render_template('error.html', message=page_content)

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(page_content, 'html.parser')

    # Fix images, stylesheets, and scripts by making their paths absolute
    for img in soup.find_all('img'):
        src = img.get('src', '')
        if not src.startswith('http'):
            img['src'] = urljoin(url, src)  # Convert relative URL to absolute

    for link in soup.find_all('link', {'rel': 'stylesheet'}):
        href = link.get('href', '')
        if not href.startswith('http'):
            link['href'] = urljoin(url, href)  # Convert relative URL to absolute

    for script in soup.find_all('script'):
        src = script.get('src', '')
        if src and not src.startswith('http'):
            script['src'] = urljoin(url, src)  # Convert relative URL to absolute

    # Now render the content as raw HTML with the 'safe' filter to prevent Jinja2 from interpreting the tags
    return render_template_string('{{ content|safe }}', content=str(soup))

if __name__ == '__main__':
    app.run(debug=True)
