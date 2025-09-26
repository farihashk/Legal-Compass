# Legal Compass

Legal Compass is an AI-powered virtual assistant designed to simplify legal processes by providing accessible legal support. It answers legal questions, summarizes documents, and recommends specialized lawyers based on user needs, making legal assistance easier for scenarios like estate planning, contracts, or disputes.

## Features
- **Legal Q&A**: Provides clear answers to user-submitted legal questions using AI.
- **Document Summarization**: Summarizes legal documents for quick understanding.
- **Lawyer Recommendations**: Matches users with lawyers based on location, specialization, and needs using semantic search.
- **User-Friendly Interface**: Planned web interface for seamless interaction.

## Tech Stack
- **Frontend**: React (in `frontend/src`), served from `frontend/public`.
- **Backend**: Flask (in `flask_server/app.py`), with testing in `flask_server/test.py`.
- **Data Collection**:
  - `scrape_lawyers.py`: Scrapes lawyer data from Avvo using Scrapy.
  - `geocode_lawyers.py`: Converts lawyer addresses to coordinates.
  - `map_specialization.py`: Maps lawyer specializations.
  - `setup_specializations.py`: Configures specialization data.
  - `specialization_mapping.json`: Stores specialization mappings.
- **Data Preprocessing**: `pdf_reader.py` for document processing, with data in `lawyer_data`.
- **Database**: MySQL (for storing lawyer and user data), SQLAlchemy (ORM).
- **Vector Search**: Pinecone (for semantic lawyer recommendations).
- **AI**: Integration with AI models for Q&A and summarization.

## Project Structure
```
legal-compass/
├── flask_server/                 # Flask backend
│   ├── app.py                   # Main Flask application
│   ├── test.py                  # Backend tests
├── data_collection/             # Data scraping and processing
│   ├── geocode_lawyers.py       # Geocodes lawyer addresses
│   ├── map_specialization.py    # Maps lawyer specializations
│   ├── scrape_lawyers.py        # Scrapes lawyer data
│   ├── setup_specializations.py # Configures specializations
│   ├── specialization_mapping.json # Specialization mappings
│   ├── scraper/                 # Scrapy configuration
│   │   ├── items.py             # Scrapy item definitions
│   │   ├── middleware.py        # Scrapy middleware
│   │   ├── pipelines.py         # Scrapy data pipelines
│   │   ├── settings.py          # Scrapy settings
├── data_preprocessing/          # Data cleaning and processing
│   ├── lawyer_data/             # Stores processed lawyer data
│   ├── pdf_reader.py            # Processes legal documents
├── frontend/                    # React frontend
│   ├── public/                  # Public assets
│   ├── src/                     # React source code
│   ├── package.json             # Frontend dependencies
├── requirements.txt             # Backend dependencies
├── schema.sql                   # MySQL schema
└── README.md                    # This file
```

## Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/legal-compass.git
   cd legal-compass
   ```

2. **Install Backend Dependencies**:
   Ensure Python 3.8+ is installed, then run:
   ```bash
   pip install -r requirements.txt
   ```
   Key dependencies: `flask`, `scrapy`, `sqlalchemy`, `pinecone-client`, `geopy`.

3. **Install Frontend Dependencies**:
   Navigate to the frontend directory and install Node.js dependencies:
   ```bash
   cd frontend
   npm install
   ```

4. **Set Up Environment Variables**:
   Create a `.env` file in the root directory:
   ```bash
   MYSQL_HOST=your_mysql_host
   MYSQL_USER=your_mysql_user
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_DATABASE=legal_compass_db
   PINECONE_API_KEY=your_pinecone_api_key
   ```

5. **Database Setup**:
   - Install MySQL and create a database named `legal_compass_db`.
   - Run the schema:
     ```bash
     mysql -u your_mysql_user -p legal_compass_db < schema.sql
     ```

6. **Run Data Collection**:
   Scrape lawyer data from Avvo:
   ```bash
   cd data_collection
   python scrape_lawyers.py
   ```
   Geocode addresses and map specializations:
   ```bash
   python geocode_lawyers.py
   python map_specialization.py
   ```

7. **Run Data Preprocessing**:
   Process documents and data:
   ```bash
   cd data_preprocessing
   python pdf_reader.py
   ```

8. **Run the Backend**:
   Start the Flask server:
   ```bash
   cd flask_server
   python app.py
   ```
   Access the API at `http://localhost:5000`.

9. **Run the Frontend**:
   Start the React development server:
   ```bash
   cd frontend
   npm start
   ```
   Access the app at `http://localhost:3000`.

## Usage
- **Legal Q&A**: Send a POST request to `/api/ask` with a JSON payload containing the legal question.
- **Document Summarization**: Upload a document to `/api/summarize` for a summary.
- **Lawyer Recommendations**: Query `/api/recommend` with preferences (e.g., location, specialization).

## Challenges Overcome
- **HTML Inconsistencies**: Handled Avvo’s inconsistent HTML with Scrapy’s robust parsing.
- **Dependency Conflicts**: Resolved issues between `pinecone-client`, `sqlalchemy`, and Scrapy.
- **Data Quality**: Normalized lawyer data and geocoded addresses for accurate recommendations.

## Future Plans
- Enhance the React frontend for a polished user experience.
- Expand scraping to cover more regions.
- Improve AI models for better Q&A and summarization accuracy.
- Introduce subscription models and law firm partnerships.

## Contributing
Fork the repository, create a feature branch, and submit a pull request with your changes.

## License
MIT License. See the `LICENSE` file for details.

## Contact
For questions, contact [your email] or open a GitHub issue.