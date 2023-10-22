from flask import Flask, request, render_template, jsonify, redirect, url_for, Response
from bs4 import BeautifulSoup
import requests
from urlparse import urljoin

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/proxy', methods=['GET', 'POST'])
def proxy():
    if request.method == 'POST':
        url = request.form.get('url', '')
    elif request.method == 'GET':
        url = request.args.get('url', '')
    
    # Check if the URL starts with 'http://' or 'https://'. If not, add 'https://'.
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    if url:
        try:
            response = requests.get(url)
            
            # Handling redirects
            while response.history:
                response = requests.get(response.url)

            content_type = response.headers.get('content-type', '')
            if content_type.startswith('image'):
                return Response(response.content, content_type=content_type)
            elif content_type.startswith('text/html'):
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Update all URLs to go through the proxy
                for tag, attribute in [('a', 'href'), ('img', 'src'), ('link', 'href'), ('script', 'src')]:
                    for elem in soup.find_all(tag, **{attribute: True}):
                        absolute_url = urljoin(url, elem[attribute])
                        elem[attribute] = url_for('proxy', url=absolute_url)
                
                return str(soup)
            else:
                return response.content
        except Exception as e:
            return str(e), 500  # Handle errors gracefully
    return 'Invalid URL', 400

if __name__ == '__main__':
    app.run(debug=True)
