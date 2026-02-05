# School Badge Collection Website

A Flask web application for collecting and displaying school badges from around the world.

## Features

- Browse school badges by geographic region
- Search schools by name or location
- User registration and authentication
- Like and download school badges
- Support for universities, middle schools, elementary schools, and kindergartens

## Installation

1. Clone the repository:
```bash
git clone https://github.com/wangfeng/school-badge-website.git
cd school-badge-website
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
flask --app app init-db
```

5. (Optional) Load sample data:
```bash
flask --app app load-sample-data
```

## Running the Application

```bash
flask --app app run --debug
```

The application will be available at http://localhost:5000

## Project Structure

```
school-badge-website/
├── app.py              # Main application
├── config.py           # Configuration
├── models.py           # Database models
├── requirements.txt    # Dependencies
├── static/
│   ├── css/
│   ├── js/
│   └── images/         # Badge images
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── school.html
│   ├── register.html
│   └── login.html
├── data/
│   └── sample_schools.json
└── README.md
```

## Database Models

- **User**: id, username, password_hash, email, created_at
- **School**: id, name, region, country, city, level, description, badge_url
- **Like**: id, user_id, school_id, created_at

## License

MIT
