# Travel Planner (Backend)

## 🌍 Description

**Travel Planner (Backend)** is the backend service of the Travel Planner project. This service provides functionality for:
- Managing user profiles.
- Tracking visited and planned places.
- Storing photos of locations.
- Creating a wishlist of future travel destinations.

The project uses **Google OAuth** for secure authentication and integration with user accounts.

---

## 🛠️ Technologies Used

The backend is built using the following technologies:

- **FastAPI**: A modern, fast web framework for building APIs.
- **PostgreSQL**: A powerful open-source relational database for storing application data.
- **Google OAuth**: Secure user authentication and account management.
- **Poetry**: Dependency management and virtual environment setup.
- **Docker & Docker Compose**: Containerization and orchestration for seamless deployment.
- **Pytest**: Testing framework for ensuring application reliability.
- **Ruff**: Linter for Python code to ensure code quality and adherence to standards.
- **Geo API**: For geographical data processing and integration.

---

## 🚀 Installation

### 1. Clone the Repository
Clone the repository to your local machine:

```bash
https://github.com/OleksandrDoronin/travel-planner-fastapi.git
cd src
```

### 2. Set Up the Virtual Environment with Poetry

If you don't have Poetry installed, you can install it by following the instructions [here](https://python-poetry.org/docs/).

Create and activate the virtual environment:

```bash
poetry install
```

Poetry will create a virtual environment and install all required dependencies for the project.

To activate the virtual environment:

```bash
poetry shell
```

Now you can start working on the project in the isolated environment.

---

## 🔧 Environment Configuration

### 1. Copy the Example .env File

Copy the example `.env` file for the respective environments:

```bash
cp .env.example .env.development
cp .env.example .env.production
```

### 2. Configure Environment Variables

Fill in the `.env` files with appropriate values. Here are some variables you need to set:

- `SECRET_KEY`: Secret key. You can generate it using the following bash command:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- `ENCRYPTION_KEY`: Secret key for encryption. You should generate this key yourself, e.g., using a tool or method appropriate for your application.
- `JWT_SECRET_KEY`: Secret key for signing JWT tokens. This can be generated in a similar way to the SECRET_KEY above.
- `GOOGLE_OAUTH_KEY`: Google OAuth client ID. You can get it from the [Google Developer Console](https://console.developers.google.com/).
- `GOOGLE_OAUTH_SECRET`: Google OAuth client secret. This is also available in the [Google Developer Console](https://console.developers.google.com/).
- `GOOGLE_REDIRECT_URI`: The URI where Google will redirect after authentication. Set this in the [Google Developer Console](https://console.developers.google.com/).
- `GEO_NAME_DATA`: API key for the GeoNames geocoding service. You can obtain it from [GeoNames](https://www.geonames.org/).
- Other necessary settings like  etc.

For other necessary settings, you can refer to the .env.example file in the repository, which contains the structure and other configuration examples.

- [`.env.example`](./.env.example)
Make sure to replace the placeholders in the .env files with your actual credentials.
---
### 3. Set the `ENV_FILE` Environment Variable

Before running the application, specify which `.env` file to load by setting the `ENV_FILE` environment variable.

#### On Linux/macOS:

Open your terminal and set the environment variable using `export`:

```bash
export ENV_FILE=.env.development  # or .env.production
```

#### On Windows:

On Windows, use the set command:
```bash
set ENV_FILE=.env.development  # or .env.production
```
Make sure to set the ENV_FILE variable to point to the appropriate .env file before running the application.

## 🐳 Installing Docker and Docker Compose

Before you can use Docker and Docker Compose, you need to install them on your system.

### Installing Docker on Linux

1. **Download and Install Docker:**

   Run the following commands to automatically install Docker:

   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   ```

2. **Install Docker Compose:**

    Download the latest version of Docker Compose:
    ```bash
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-$(uname -s)-$(uname -m)"  -o /usr/local/bin/docker-compose
    sudo mv /usr/local/bin/docker-compose /usr/bin/docker-compose
    sudo chmod +x /usr/bin/docker-compose
    docker compose version
    ```

### Installing Docker on macOS

1. **Install Docker:**

    To install Docker on macOS, use Homebrew:
    ```bash
    brew install docker
    ```

2. **Install Docker Compose:**

    Install Docker Compose via Homebrew as well:
    ```bash
    brew install docker-compose
    ```

## 🐳 Using Docker and Docker Compose

Docker Compose is used to simplify the setup of development and production environments.

### 1. Build and Run the Containers

Use the following commands to start the application in a containerized environment:

```bash
docker-compose up --build
```

If you want to run the containers in the background, you can add the -d flag:

```bash
docker-compose up --build -d
```

### 2. Stop the Containers
To stop the running containers:
```bash
docker-compose stop
```
---
## 🧪 Testing

The project uses **Pytest** for testing the backend.

### 1. Run the Tests

Install Pytest using poetry:
```bash
poetry install --dev
```

Activate the Poetry environment and execute the tests:

```bash
poetry run pytest
```

### 2. Test Coverage

You can also generate a test coverage report:

```bash
poetry run pytest --cov=src
```

---
## 🧹 Code Quality

### Ruff: Python Linter

**Ruff** is used for linting the Python code. It ensures code adheres to best practices and PEP standards.

#### Installation

Install Ruff using Poetry:

```bash
poetry install --dev
```

#### Run Ruff

To lint the codebase, execute:

```bash
poetry run ruff check .
```

Fix automatically detectable issues:

```bash
poetry run ruff check --fix .
```

---

## 🌟 Features

- **User Authentication**: Secure login via Google OAuth.
- **Travel Management**: Add, update, get and delete places.
- **Wishlist**: Maintain a list of desired destinations.
- **Geolocation Support**: Integration with Geo APIs for location data.
- **Dockerized Environment**: Easy setup and deployment with Docker.

---

## 📚 Documentation

The API documentation is available through **Swagger** and **ReDoc** at the following endpoints:

- Swagger: `/docs`
- ReDoc: `/redoc`

---
## ✨ Contribution

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature-name`.
3. Commit your changes: `git commit -m 'Add new feature'`.
4. Push to the branch: `git push origin feature-name`.
5. Submit a pull request.

---

## 🛡️ License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

---

## 💬 Contact

For any questions or feedback, feel free to contact the project owner:

- **Oleksandr Doronin**
- GitHub: [OleksandrDoronin](https://github.com/OleksandrDoronin)



