from flask import Flask, render_template, request
from pymongo import MongoClient
import re

app = Flask(__name__)

# MongoDB connection
connection_string = "mongodb://localhost:27017/legal"
client = MongoClient(connection_string)
db = client.legal
collection = db.georgia

@app.route('/', methods=['GET', 'POST'])
def search():
    search_query = request.form.get('search_query', '')
    filter_type = request.form.get('filter_type', '')
    page = int(request.args.get('page', 1))
    per_page = 10

    query = {}
    if filter_type == 'code':
        query['TYPE'] = 'code'
        search_fields = ['Rule_text']
    elif filter_type == 'regulation':
        query['TYPE'] = 'regulation'
        search_fields = ['section_text']
    else:
        search_fields = ['Rule_text', 'section_text']

    keywords = re.findall(r'\w+', search_query)
    if keywords:
        query['$or'] = [{field: {'$regex': '|'.join(keywords), '$options': 'i'}} for field in search_fields]

    offset = (page - 1) * per_page
    results = collection.find(query).skip(offset).limit(per_page)

    highlighted_results = []
    for result in results:
        highlighted_text = result.get('Rule_text') or result.get('section_text')
        for keyword in keywords:
            highlighted_text = re.sub(f'({keyword})', r'<mark>\1</mark>', highlighted_text, flags=re.IGNORECASE)
        result['highlighted_text'] = highlighted_text
        highlighted_results.append(result)
    total_results = collection.count_documents(query)

    return render_template('search.html', results=highlighted_results, search_query=search_query,
                           filter_type=filter_type, page=page, per_page=per_page, total_results=total_results)

if __name__ == '__main__':
    app.run(debug=True)