from flask import Flask, render_template, request,jsonify
from index import search_index
import requests
app = Flask(__name__)



@app.route('/')
def index():
    url = 'https://saurav.tech/NewsAPI/top-headlines/category/health/in.json'
    
    try:
        # Fetch JSON data from the URL
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse JSON data
            data = response.json()
    except Exception as e:
        # Handle any exceptions
        return jsonify({"error": str(e)}), 500
    return render_template('index.html', articles=data['articles'])

@app.route('/search')
def search():
    query = request.args.get('q')

    # Perform the search
    results = search_index(query)

    # Render the results in a template
    return render_template('results.html', query=query, results=results)

if __name__ == "__main__":
    app.run(debug=True)
