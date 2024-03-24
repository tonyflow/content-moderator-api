#  Tech spec
## Introduction and problem statement
The application at hand provides a REST endpoint allowing the user to
classify different text sentences. You can find the OpenAPI documentation for the endpoint under `http://localhost:8000/docs`

Apart from classifying the given text sentences, the API runs a metrics collector on a 
separate thread. The metrics collector will collect and report the metrics included in the statically defined dict `method_names`
using the configured reporter.

The classifier and metrics configuration can be found in the `app_conf.yml`.

For the sake of demonstration, the metrics reporting interval is set to 4 seconds (so that the logs are not flooded with metric messages) and the
metrics reporter is set to `stdout`. The functionality of the collector and the reporter can be more easily observed
that way.

## Ways to run the code
### Manually
1. Install all requirements
```bash
pip3 install --no-cache-dir -r requirements.txt
```
2. Run the uvicorn server
```bash
uvicorn router:content_moderator --reload
```

### Use the included `Dockerfile`
You can use the included `Dockerfile` to run the FastAPI server
1. Build the container
```bash
 docker build -t content_moderator . 
```
2. Run the container
```bash
 docker run --rm -p 8000:8000 content_moderator
```

Using either approaches you can access the API under http://localhost:8000/

## Technology Stack
There were two candidates for building the API: FastAPI and Flask. Because FastAPI:
- Is highly customizable
- Has out-of-the-box support for async code execution 

## Documentation

## Production Rollout
### Error Model
### Authentication and authorization



### Scaling topics
#### HTTP compression


