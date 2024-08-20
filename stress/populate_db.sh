#!/bin/bash

cat $1 | xargs -n 1 -P 25 -I {} bash -c 'curl -s -X POST "http://fastapi.localhost:8008/api/v1/urls/" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"url\": \"{}\"}";' | jq .data.hash
