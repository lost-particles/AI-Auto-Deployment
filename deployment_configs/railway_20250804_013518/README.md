# Flask App for Railway

This is a simple Flask app designed for deployment on Railway.app.

## Usage

1.  Create a Railway project.
2.  Initialize a new project from a Git repository (this one).
3.  Railway automatically detects the `Dockerfile` and `railway.toml` file to build and deploy.
4.  The app will be deployed and publicly accessible.

## Configuration

The `railway.toml` file configures the build and deploy process for Railway. Specifically, it sets the `startCommand` to use `gunicorn` for serving the Flask application, ensuring it binds to the port provided by the Railway environment (`$PORT`).

## Notes

*   The application exposes a simple "Hello, World!" endpoint.
*   The `requirements.txt` specifies project dependencies.