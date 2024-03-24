#  Tech spec
## Introduction and problem statement
The application at hand provides a REST endpoint allowing the user to
classify different text sentences. You can find the OpenAPI documentation for the endpoint under http://localhost:8000/docs

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
- Has automatic OpenAPI docs production
- Despite it being relatively new, has extensive documentation and supportive community

## Production Rollout
The following is a selection of topics where we try to address different aspects of the content moderator 
rollout to production

## Documentation
1. Internal:
2. External:

### Infrastructure Setup

### CI/CD
### Metrics Dashboard and Alerts
Despite having a solution in place for collecting and reporting metrics, we need to set up
the environment for displaying these metrics. What's more, we might need to create certain alerts
and agree on certain SLAs. Based on the SLAs, we need to subscribe or not to these alerts based on 
their severity.

### Success metrics
In collaboration with product or other teams we need to agree on tangible product/business level metrics.
These metrics will allow us to actually track the added value of the feature outside the close confines of
the engineering team. Sometimes these metrics are hard to pinpoint and I would not label this as a blocker
for the project's rollout.

### Error Model

### Authentication and authorization

### Non-functional requirement
1. Legal requirements:
2. Product requirements:
3. Logging:

### Scaling topics

### Testing
Integration or unit tests

### Incremental Rollout


### Interfaces with other components
### Caching
#### HTTP compression


