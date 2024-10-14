from flask import Blueprint, request, jsonify, current_app, session
from functools import wraps
import requests
from bs4 import BeautifulSoup
from cache import cache

api_bp = Blueprint('api', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'access_token' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@api_bp.route('/refresh', methods=['POST'])
@login_required
def refresh():
    supabase = current_app.config['SUPABASE']
    try:
        article_number = request.form.get('article_number')
        show_all = request.form.get('show_all') == 'true'
        gap_mode = request.form.get('gap_mode')
        use_avg = request.form.get('use_avg') == 'true'
        
        @cache.memoize(timeout=300)  # Cache for 5 minutes
        def fetch_data(article_number):
            url = f'https://hayyatapps.com/API/v273__new/Data/?article={article_number}'
            response = requests.get(url)
            return response.text

        html_content = fetch_data(article_number)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        div = soup.find('div', {'class': 'main'})
        if not div:
            return jsonify({'error': 'Unable to find main div'}), 500
        table = div.find('table', {'id': 'SGSR-table-1'})
        if not table:
            return jsonify({'error': 'Unable to find table'}), 500
        thead = table.find('thead')
        header_row = thead.find('tr') 
        rows = table.find_all('tr')[1:]
        
        data = process_data(rows, show_all, gap_mode, use_avg)
        
        return jsonify({'data': data, 'error': None})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_data(rows, show_all, gap_mode, use_avg):
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
    return sorted_gaps if show_all else sorted_gaps[:10]
