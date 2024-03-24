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

## Run the code
### Manually
1. Install all requirements
```bash
pip3 install --no-cache-dir -r requirements.txt
```
2. Export the `BEARER_TOKEN` variable
```bash
export BEARER_TOKEN=place_your_token_here 
```
3Run the uvicorn server
```bash
uvicorn router:content_moderator --reload
```

### Use the included `Dockerfile`
You can use the included `Dockerfile` to run the FastAPI server
1. Replace the BEARER_TOKEN placeholder in the `Dockerfile`
```bash
ENV BEARER_TOKEN=bearer_token_placeholder
```
2. Build the container
```bash
 docker build -t content_moderator . 
```
3. Run the container
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

### Documentation
Whether this is an internal or external facing API, we need to develop sufficient documentation. Maybe the OpenAPI
documentation is enough for this case. FastAPI provides extensive support for documenting the 
different endpoints.

### Infrastructure Setup
Rolling this out into production might first involve multiple deployments - namely staging, dev, canary and finally production - 
all these environments should be appropriately configured. Whether manually using a cloud console or via
an infrastructure-as-code language (e.g. Terraform). I would be an advocate of the second since it's much 
more declarative and is under version control - thus in case of erroneous deployment, we can rollback.

### CI/CD
The CI/CD pipelines we're using should be updated to include the new service.

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
The current error model is quite naive: The `classify` endpoint requires a `message` query parameter and returns a 
break-down of the text classification based on certain labels (hate, violence etc.). It also returns 
`503: Service Unavailable` during the warm-up period of the serverless Koala classifier from the side of hugging face.
Some error model cases that need to be accounted for:
- errors produced from the classifier HTTP query
- error produced from marshalling/unmarshalling JSON responses
- factory class errors
- 

### Authentication and authorization
If this API is for internal use only then locating it inside private VPC would be enough. Otherwise, we need 
to decide on an encryption scheme (symmetric, asymmetric) and different ways of incorporating this into our
API (auth0 etc...)


### Non-functional requirement
1. Legal requirements:
2. Product requirements:
3. Logging:

### Scaling topics
The easiest way to scale this out would be to deploy the container build from the `Dockerfile` to a cloud container
service like AWS's ECS. The container service can be then configured with certain scaling rules (CPU or mem) so that
the service's number of instances are able to oscillate between certain bounds. Once a load balancer is configured in front
of the service target group and the autoscaling groups are in place there are still two bottlenecks:
1. The number of connections allowed from the side of FastAPI: If the number of requests received by the instance is larger
than the allowed open connections that FastAPI allows some requests might be dropped. This might be ok depending on the
SLA but if not, we might have to increase the number of open connections, increase the service resources or improve the
service algorithmically.
2. The rhythm of requests accommodation from the side of the serverless Koala API deployment provided by hugging face: No 
matter how we optimize the service of receiving requests, the service will always be bound to how quickly the text is propagated
to the Koala API for classification. This can be improved by :
- using on demand on premise instances where we deploy the model ourselves
- caching certain sentences and returning cached classifications: This can be done by computing the Levenshtein/edit distance 
between incoming and cached requests and returning cached classifications if the distance is lower than an acceptable threshold

### Testing
Currently the application is under tested

#### Integration tests
There's only one integration test included under `router_test.py` but because of the hugging face API warm up period. The test
is currently disabled. Once the service startup becomes stable, the test should be enabled and more tests could potentially
be added.

#### Unit tests
Happy paths are tests but not all error paths. Especially once the error model becomes more sophisticated, the unit tests
should be extended as well

### Incremental Rollout
This is only in case we already have a classification system and we want to gradually migrate to a new one. In that case,
we can gradually move traffic from one classification service to the other. This divide can performed on the side of the 
consumer (e.g. 20% of the requests are sent to service X and the rest to service Y) 

## Tech spec sign off 
The tech spec containing the detailed solution design should be signed off by the corresponding team and
kept for historicity purposes.

## Rollback
Once a rollout plan is drafted, we should be able to easily rollback each and every step of the process in case of failure.
We can simplify this process by creating small deployable units. For example, the classification and the metrics collection
can be two different phases of the deployment
1. Deploy the classifier with a naive reporter
2. Deploy a full-fledged metrics reporter like something that reported metrics to a time-series database like Influx

### Interfaces with other components
### Caching
#### HTTP compression


