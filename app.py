from flask import Flask, render_template, request
from index import search_index

app = Flask(__name__)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q')

    # Perform the search
    results = search_index(query)

    # Render the results in a template
    return render_template('results.html', query=query, results=results)

if __name__ == "__main__":
    app.run(debug=True)
