from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def fetch_data(article_number, show_all):
    url = f'https://hayyatapps.com/API/v273__new/Data/?article={article_number}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'SGSR-table-1'})
    rows = table.find_all('tr')
    gaps = []
    for row in rows[1:]:
        cols = row.find_all('td')
        name = cols[0].text.strip()
        max_buy_price = int(cols[3].text.replace(',', ''))
        min_sell_price = int(cols[4].text.replace(',', ''))
        curr_price = int(cols[5].text.replace(',', ''))
        gap = min_sell_price - curr_price
        gaps.append((name, max_buy_price, min_sell_price, curr_price, gap))
    sorted_gaps = sorted(gaps, key=lambda x: x[4], reverse=True)
    return sorted_gaps if show_all else sorted_gaps[:10]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/refresh', methods=['POST'])
def refresh():
    article_number = request.form.get('article_number')
    show_all = request.form.get('show_all') == 'true'
    sorted_gaps = fetch_data(article_number, show_all)
    return jsonify({'data': sorted_gaps})

if __name__ == '__main__':
    app.run(debug=True)
