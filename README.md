# FIFA/FUT Trading Gaps Finder

## Description
This web application helps FIFA/FUT players find trading opportunities by analyzing price gaps for different player cards. It provides real-time data on player prices, allowing users to make informed decisions for trading in the FIFA Ultimate Team market. Thank you futtrading.co.uk !!

## Features
- Real-time price data for FIFA/FUT player cards
- Multiple chemistry styles support (Hunter, Shadow, Anchor)
- User authentication system
- Favorite players tracking
- Customizable gap calculations
- Responsive web interface
- Caching system for improved performance

## Technologies Used
- Backend: Python, Flask
- Frontend: HTML, CSS, JavaScript
- Database: Supabase
- Authentication: Supabase Auth
- Caching: Flask-Caching
- Deployment: Vercel

## Setup and Installation
1. Clone the repository:   ```
   git clone https://github.com/carterlasalle/fifa-fut-trading-gaps.git
   cd fifa-fut-trading-gaps   ```

2. Set up a virtual environment:   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`   ```

3. Install dependencies:   ```
   pip install -r requirements.txt   ```

4. Set up environment variables:
   Create a `.env` file in the root directory and add the following:   ```
   SECRET_KEY=your_secret_key
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_api_key   ```

5. Run the application:   ```
   python gapfinder.py   ```

6. Open a web browser and navigate to `http://localhost:5001`

## Deployment
This application is configured for deployment on Vercel. Ensure you have the Vercel CLI installed and configured, then run:
