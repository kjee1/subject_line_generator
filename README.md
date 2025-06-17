# Newsletter Headline Generator API

A FastAPI-based service that generates optimized newsletter subject lines using AI and trending topics.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with the following variables:
```
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
API_RATE_LIMIT=10  # requests per minute
```

## Running the API

Start the development server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Run tests with:
```bash
pytest
```

## Project Structure

```
headline-api/
├── main.py                  # FastAPI app & routing
├── headline_generator.py    # Core logic + LLM
├── prompt_builder.py        # Assemble context-rich prompt
├── trends_fetcher.py        # Google Trends integration
├── tests/                   # Test directory
│   ├── test_main.py
│   ├── test_headline_generator.py
│   └── test_trends_fetcher.py
├── requirements.txt
└── README.md
``` 