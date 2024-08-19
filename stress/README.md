### Simple Stress Test with Locust

Simple stress tests of the redirect API route. The sample HTML report is a tests with 500 RPS and 400 users of the containerize version of the app (see docker-compose file). Slow response times seems to be mainly due to the high number of user, with 20 user and similar RPS rate the response time hit the average of 30ms.

Main limiting factor of testing higher RPS was my laptop CPU usage. But adding reading replicas to the database, more webserver workers and also caching layer (e.g. redis) may help the app reach a couple thousand requests per second.

Many optimizations can still be made in the postgress and load balancer configurations. I has not able to investigate this further due to the lack of time.

##### Setup

```bash
pip install locust
locust -f locust_file.py
# > web interface: http://0.0.0.0:8089/
```
