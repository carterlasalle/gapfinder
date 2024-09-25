from flask import Flask, render_template, request, jsonify, session, redirect
import requests
from bs4 import BeautifulSoup
from json import dumps

app = Flask(__name__)
app.secret_key = 'some_random_key'  

@app.route('/')
def index():
    if 'authenticated' not in session or not session['authenticated']:
        return redirect('/login')
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'fut':  
            session['authenticated'] = True
            return redirect('/')
        else:
            return 'Invalid Password', 401
    return render_template('login.html')

@app.route('/refresh', methods=['POST'])
def refresh():
    if 'authenticated' not in session or not session['authenticated']:
        return 'Unauthorized', 401
    try:
        article_number = request.form.get('article_number')
        show_all = request.form.get('show_all') == 'true'
        gap_mode = request.form.get('gap_mode')
        use_avg = request.form.get('use_avg') == 'true'
        
        url = f'https://hayyatapps.com/API/v273__new/Data/?article={article_number}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        div = soup.find('div', {'class': 'main'})
        table = div.find('table', {'id': 'SGSR-table-1'})
        thead = table.find('thead')
        header_row = thead.find('tr') 
        rows = table.find_all('tr')[1:]
        
        gaps = []
        for row in rows:
            cols = row.find_all('td') 
            name = cols[0].text.strip()            
            max_buy_price = int(cols[3].text.replace(',', ''))
            min_sell_price = int(cols[4].text.replace(',', ''))
            
            curr_price_text = cols[5].text.split(" ")[0].replace(',', '') 
            avg_price_text = cols[5].text.split("(")[1].split(" ")[0].replace(',', '') if '(' in cols[5].text else None
            
            curr_price = int(curr_price_text)
            avg_price = int(avg_price_text) if avg_price_text else None
            
            price_for_calculation = avg_price if use_avg and avg_price else curr_price
            
            if gap_mode == 'min_sell':
                gap = min_sell_price - price_for_calculation 
            elif gap_mode == 'max_buy':
                gap = max_buy_price - price_for_calculation
            else:  
                gap = max_buy_price - min_sell_price
            
            gaps.append((name, max_buy_price, min_sell_price, curr_price, avg_price, gap))
        
        sorted_gaps = sorted(gaps, key=lambda x: x[-1], reverse=True)  
        return jsonify({'data': sorted_gaps if show_all else sorted_gaps[:10], 'error': None})
    
    except Exception as e:
        print(e)
        return dumps({'data': None, 'error': str(e)})

    return dumps({'data': gaps, 'error': None})

if __name__ == '__main__':
    app.run(debug=True)