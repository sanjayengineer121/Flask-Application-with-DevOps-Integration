# Flask-Application-with-DevOps-Integration

Part 1: Flask Application
Create a Task Manager Flask Application:
● Create a simple task manager where users can add, edit, and delete
tasks).
● Include a login page that Uses JWT for login.
Static Files and Templates:
● UI need not be very fancy, the main focus should be on the backend
and deployment
Database Integration:
● Integrate a database (SQLite or any other of your choice).
● Sensitive data like passwords, etc should be encrypted.
Logging:
● Implement logging in your Flask application. Log relevant information,
errors, and debug messages.

Part 2: Deployment on AWS
Docker Setup:
● Create a Dockerfile for the Flask Application.
● Build the docker image with proper name and tags.
SSH Access:
● Use the provided command/credentials to SSH into the EC2 VM.
Flask App Deployment:
● Run the docker image with proper configuration and port assignment.
● Verify that the application is running on the specified http://IP:PORT/.
