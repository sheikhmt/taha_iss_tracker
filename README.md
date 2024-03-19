# ISS Tracker Flask App

## Description
This project aims to enhance the ISS Tracker developed in previous homework by adding new routes, automating deployment using Docker Compose, and providing detailed documentation for usage and deployment. The Flask app now includes additional routes for accessing specific data from the ISS dataset, Docker containerization for easy deployment, and comprehensive testing.

## Important Files
- **iss_tracker.py**: The Flask application file containing all the routes and logic.
- **requirements.txt**: Lists all the required Python libraries for the project.
- **Dockerfile**: Defines instructions for building the Docker image.
- **docker-compose.yml**: Configures the deployment of the app using Docker Compose.

## Part 1: Flask Routes
The Flask app includes eight routes:
1. `/comment`: Returns the 'comment' list object from the ISS data.
2. `/header`: Returns the 'header' dictionary object from the ISS data.
3. `/metadata`: Returns the 'metadata' dictionary object from the ISS data.
4. `/epochs`: Returns the entire data set of epochs.
5. `/epochs?limit=int&offset=int`: Returns a modified list of epochs given query parameters.
6. `/epochs/<epoch>`: Returns state vectors for a specific epoch.
7. `/epochs/<epoch>/speed`: Returns instantaneous speed for a specific epoch.
8. `/epochs/<epoch>/location`: Returns latitude, longitude, altitude, and geoposition for a specific epoch.
9. `/now`: Returns instantaneous speed, latitude, longitude, altitude, and geoposition for the epoch nearest in time.

## Defensive Programming
All routes utilize defensive programming strategies to handle bad requests, including exception handling and validation of inputs. Appropriate docstrings and type annotations are provided for clarity and maintainability.

## Part 2: Docker Deployment
- **requirements.txt**: Contains a list of non-standard Python libraries required for the project.
- **Dockerfile**: Defines the Docker image and installs necessary Python libraries.
- **docker-compose.yml**: Automates the deployment process by building the image and binding ports.

## Part 3: README Instructions
- **Citation**: The ISS data used in this project is from [provide source].
- **Deployment Instructions**: 
  - Clone the repository and navigate to its directory.
  - Run `docker-compose up --build` to build and deploy the Docker containers.
  - Access the app at `http://localhost:5000`.
- **Curl Routes**:
  - `/comment`: `curl http://localhost:5000/comment`
  - `/header`: `curl http://localhost:5000/header`
  - `/metadata`: `curl http://localhost:5000/metadata`
  - `/epochs`: `curl http://localhost:5000/epochs`
  - `/epochs/<epoch>`: `curl http://localhost:5000/epochs/epoch_id`
  - `/epochs/<epoch>/speed`: `curl http://localhost:5000/epochs/epoch_id/speed`
  - `/epochs/<epoch>/location`: `curl http://localhost:5000/epochs/epoch_id/location`
  - `/now`: `curl http://localhost:5000/now`
- **Unit Testing**:
  - To run containerized unit tests, use the following command:
    ```
    docker-compose run --rm app python -m pytest tests/
    ```

## Part 4: Additional Instructions
- **Interpretation of Outputs**: The application's output provides insights into the ISS's location, speed, and trajectory, enabling users to track its movement in real time.
- **Acknowledgments**: This project uses NASA's public data and some parts of the code. The geodetic calculations have been verified using an online tracker.

## Contributors
- Muhammad Taha
- ChatGPT

