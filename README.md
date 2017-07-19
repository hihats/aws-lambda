# The script collection used at AWS Lambda

## docker-lambda
we can use docker-lambda image for local development.

```bash
$ docker run -v "$PWD":/var/task lambci/lambda:python3.6 json_check.lambda_handler $(printf '%s' $(cat sample.json))
```
