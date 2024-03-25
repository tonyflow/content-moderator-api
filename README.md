#  Tech spec
## Introduction and problem statement
The application at hand provides a REST endpoint allowing the user to
classify different text sentences. You can find the OpenAPI documentation for the endpoint under http://localhost:8000/docs
The classification is based on the [KoalaAI Text Moderation model](https://huggingface.co/KoalaAI/Text-Moderation) provided by [huggingface.co](https://huggingface.co/).

The endpoint is
```
POST /classify
```
with request body
```json
{
   "text": "the text to classify here"
}
```

A few reasons why a POST was selected over a GET to convey these data
1. GET has a size limit of about 2000 characters. POST can accommodate much larger requests
2. GET requests become part of the URL. This information can be sensitive and exposing them on a URL is not privacy centric
3. Using post we have complete control over character encoding and this can be important as we discuss further on in the
"large" requests section

Apart from classifying the given text sentences, the API runs a metrics collector on a separate thread. The metrics collector will collect 
and report the metrics included in the statically defined dict `method_names` using the configured reporter.

For the sake of demonstration, the metrics reporting interval is set to 4 seconds (so that the logs are not flooded with metric messages) and the
metrics reporter is set to `stdout`. The functionality of the collector and the reporter can be more easily observed
that way.

The classifier and metrics configuration can be found in the `app_conf.yml`.

## Run the code
The requests to the hugging face API need to be authenticated. This requires an access token which can be provided by 
hugging face.
### Manually
1. Install all requirements
```bash
pip3 install --no-cache-dir -r requirements.txt
```
2. Export the `BEARER_TOKEN` variable
```bash
export BEARER_TOKEN=place_your_token_here 
```
3. Run the uvicorn server
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
### API
There were two candidates for building the API: FastAPI and Flask. The choice of FastAPI was more prominent since FastAPI:
- Is highly customizable (more so than Flask)
- Uses Pedantic that allows for out-of-the-box stricter typing
- Has out-of-the-box support for async code execution. Flask does not 
- Has automatic OpenAPI docs production
- Despite it being relatively new, has extensive documentation and supportive community
- Is proven to be faster than Flask

### Scheduling
Instead of using vanilla Python for scheduling the metrics collection, I chose the `schedule` package which provides
a simple interface to schedule recurring jobs.

## Production Rollout
The following is a selection of topics where we try to address different aspects of the content moderator 
rollout to production. The list is not exhaustive and tries to focus on rolling out an MVP. Some bonus optimization 
points are also included.

### Documentation
Whether this is an internal or external facing API, we need to develop sufficient documentation. Maybe the OpenAPI
documentation is enough for this case. On top, FastAPI provides extensive support for documenting the different endpoints
through annotations.

### Infrastructure Setup
Rolling this out into production might first involve multiple deployments - namely staging, dev, canary and finally production.
All these environments should be appropriately configured. Whether manually using a cloud console or via
an infrastructure-as-code language (e.g. Terraform). I would be an advocate of the second since it's much 
more declarative and is under version control - thus in case of erroneous deployment, we can roll back.

### CI/CD
The CI/CD pipelines we're using should be updated to include the new service.

### Metrics Dashboard and Alerts
Despite having a solution in place for collecting and reporting metrics, we need to set up
the environment for displaying these metrics. What's more, we might need to create certain alerts
and agree on certain SLAs. Based on the SLAs, we need to subscribe or not to these alerts based on 
their severity.

### Success metrics
In collaboration with product and/or other teams we need to agree on tangible product/business level metrics.
These metrics will allow us to actually track the added value of the feature outside the close confines of
the engineering team. Sometimes these metrics are hard to pinpoint and I would not label this as a blocker
for the project's rollout since it's an MVP. 

### Error Model
The current error model is quite naive: The `classify` endpoint requires a `message` query parameter and returns a 
break-down of the text classification based on certain labels (hate, violence etc.). It also returns 
`503: Service Unavailable` during the warm-up period of the serverless Koala classifier from the side of hugging face.
Some error model cases that need to be accounted for:
- errors produced from the classifier HTTP query
- errors produced from marshalling/unmarshalling JSON responses
- factory class errors
- errors producing from capping input text
- unhandled exceptions: stack traces should not be exposed to the end user
- other

### Authentication and authorization
If this API is for internal use only then locating it inside a VPC would be enough. Otherwise, we need 
to decide on an encryption scheme (symmetric, asymmetric) and different ways of incorporating this into our
API (auth0 etc...)

### Legal & compliance
This has to be discussed with product/business/legal teams. If there are any considerations we need to take into account.

### Performance / Traffic estimation
This goes hand in hand with the next section. We need to have a ballpark estimation about the expected traffic.
Since it's an MVP this could be low, but we still need to have some numbers from product.

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
   - using on-demand and regional(for proximity purposes) instances where we deploy the model ourselves
   - caching certain sentences and returning cached classifications: This can be done by computing the Levenshtein/edit distance 
between incoming and cached requests and returning cached classifications if the distance is lower than an acceptable threshold

### Testing
Currently, the application is under tested

#### Integration tests
There's only one integration test included under `router_test.py` but because of the hugging face API warm up period. The test
is currently disabled. Once the service startup becomes stable, the test should be enabled and more tests could potentially
be added.

#### Unit tests
Happy paths are tested but not all error paths. Especially once the error model becomes more sophisticated, the unit tests
should be extended as well.

Some quality unit tests should also be included e.g.
- ***I had a very bad day*** should have high values on certain labels
- ***This is a beautiful day*** should have high values on other labels

### Incremental Rollout
This is only in case we already have a classification system and we want to gradually migrate to a new one. In that case,
we can gradually move traffic from one classification service to the other. This divide can be performed on the side of the 
consumer (e.g. 20% of the requests are sent to service X and the rest to service Y)

### Rollback
Once a rollout plan is drafted, we should be able to easily roll back each and every step of the process in case of failure.
We can simplify this process by creating small deployable units. For example, the classification and the metrics collection
can be two different phases of the deployment
1. Deploy the classifier with a naive reporter
2. Deploy a fully-fledged metrics reporter like something that reports metrics to a time-series database like Influx

### Caching
In case of "similar" input we could leverage an in-memory cache in order to save the hop to the remote API. For the MVP though
cache optimization might not crucial. Bloom filters can be used to make the decision of whether we can use the cache or not 
faster by telling us what kind of data are definitely ***not*** in the cache.

### "Large" requests
At this point the API does not cap the input text. Theoretically, the user can send an arbitrarily long text to classify.
If an unrestricted text is a hard requirement, there are a few ways to address this using:
- HTTP compression: Compression from the side of the client. Server side should be configured accordingly
- Encoding: Use a common algorithm like Huffman to encode the text sent
Making the requests smaller can decrease the bandwidth use and in turn increase the number of requests served

### Interfaces with other components
If the API is to be used internally as well, I'd advocate for the [principle of least privilege](https://en.wikipedia.org/wiki/Principle_of_least_privilege).
This means that the network security around the service should only allow a certain list of internal clients to access it.
This can easily be achieved with security groups or access lists.

The attending engineer should make sure that these clients are updated appropriately and abide by the agreed contract.

### Code Review
At least one more engineer should review and approve the involved code before this being rolled out to production. There
are already some areas of improvement:
- Rely on FastAPI decorators for bootstrapping and cleaning up the application
- Constrain the length of messages that can be sent for classification. Longer messages could be accommodated by a different endpoint.
The endpoint could be a POST request with a request body in that case.
- Implement an actual metrics reporter. Currently, we are just printing the metrics to stdout. These metrics should be 
persisted somewhere (e.g. time-series database) in order to be displayed and provide concrete insights

### Tech spec sign off 
The tech spec containing the detailed solution design should be signed off by the corresponding team and
kept for historicity purposes.

### Post Rollout phase
The attending engineer should monitor the rollout - check all the metrics, dashboards and alerts mentioned above - and make 
sure that service is behaving as expected. This should happen at least during the day of the deployment. Dependent teams
should be notified about the deployment as well as the abilities of the MVP.
