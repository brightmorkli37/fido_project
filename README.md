# Fido Project - Transactions API

This project is a FastAPI-based API for handling transactions. It uses MongoDB as the database backend.

## Prerequisites

- Python 3.7+
- MongoDB

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/fido-project.git
   cd fido-project
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Configuration

Make sure to set up your MongoDB connection string in the appropriate configuration file or environment variable.

## Running the Development Server

To start the development server, run:

```
uvicorn app.api_v1.main:app
```

The API will be available at `http://localhost:8000`.

## API Documentation

Once the server is running, you can access the auto-generated API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

To run the tests, execute:

```
pytest
```

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct, and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.