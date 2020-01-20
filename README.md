# cloud-runner

Turn command line executable into http services

## Features
- Call with a single http request
- Retrieve stdout / stderr / exit code
- Concurrent execution is supported
- Support command line arguments, environment variables, file parameters, timeout


## Usage
Build the base image provided in this repo: `docker build -p runner:latest .`

Create a dockerfile that extends the base image
```
FROM runner:latest

# Install any dependency
RUN apt-get update && apt-get install -y --no-install-recommends cowsay

# Define PROCESS_EXECUTABLE 
ENV PROCESS_EXECUTABLE=/usr/games/cowsay
```

Deploy to Cloud Run

Test: `curl -X POST -d="{\"params\": [\"hello world\"]}" <SERVICE_URL>`
