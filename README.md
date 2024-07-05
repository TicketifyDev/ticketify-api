# Ticketify-API
A comprehensive backend APIs for a ticket booking platform, designed to manage user authentication, event listings, ticket reservations, and administrative functions.

<h3><b>Introduction</b></h3>

This project provides the backend APIs that supports user authentication, event management, ticket booking, and event-organizer registration and approval process.

<h3><b>Features</b></h3>

<ul>
  <li>User authentication and authorization</li>
  <li>Event browsing and searching</li>
  <li>Ticket booking and management</li>
  <li>Admin functionalities for event and user management</li>
  <li>Organizer registration and approval</li>
</ul>

<h3><b>Technologies Used</b></h3>

<ul>
  <li><b>Backend Framework:</b> FastAPI</li>
  <li><b>Database:</b> MongoDB</li>
  <li><b>Authentication:</b> JWT (JSON Web Tokens)</li>
  <li><b>Testing:</b> PyTest</li>
  <li><b>Others:</b> Docker, Alembic for migrations</li>
</ul>

<h3><b>Installation</b></h3>
<h4><b>Prerequisites</b></h4>
<ul>
  <li>Python 3.8+</li>
  <li>MongoDB</li>
  <li>Docker (optional for containerization)</li>
</ul>

<h3><b>Setup</b></h3>
<h4><b>To run this project, follow the instructions outlined below:</b></h4>
<h5>1. Clone the repository:</h5>

```bash
git clone https://github.com/YashwanthSimhaa/Ticketify-API.git
```

<h5>2. Create a Python Virtual Environment:</h5>

```bash
python -m venv ticketify_env
```

<h5>3. Activate the Virtual Environment:</h5>

```bash
ticketify_env\Scripts\activate     #On Linux, use `source ticketify_env/bin/activate`
```

<h5>4. Install dependencies:</h5>

```bash
pip install -r requirements.txt
```

<h5>5. Navigate to source folder</h5>

```bash
cd src
```

<h5>6. Start the server</h5>

```bash
uvicorn main:app --reload
```

<h3><b>Usage</b></h3>
<h4><b>Running Locally</b></h4>
<ul>
  <li>Ensure your MongoDB server is running and accessible.</li>
  <li>Start the FastAPI server using <b>uvicorn</b> as shown in the installation steps.</li>
  <li>Access the API at <b>http://localhost:8000/docs</b></li>
</ul>

<h4><b>Docker</b></h4>
<h5>1. Build and run the containers:</h5>

```bash
docker-compose up --build
```

<h5>2. Access the API at <b>http://localhost:8000/docs</b></h5>
<br>
<h3><b>Contact</b></h3>
<h4>For any questions or suggestions, please contact:</h4>
<ul>
  <li>Yashwanth </li>
  <li><b>Email:</b> yashwanthsimha9258@gmail.com</li>
</ul>
<hr>
<ul>
  <li>Dattatreya </li>
  <li><b>Email:</b> dattatreyapatil74@gmail.com</li>
</ul>
<hr>
<ul>
  <li>Varsha </li>
  <li><b>Email:</b> varshasn2002@gmail.com</li>
</ul>

