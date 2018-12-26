#!/bin/bash

set -e
set -x

body='{
"request": {
"branch":"release/3.6.1",
"env": { "CI_BRANCH": "${TRAVIS_BRANCH}"
}}}'

curl -s -X POST \
   -H "Content-Type: application/json" \
   -H "Accept: application/json" \
   -H "Travis-API-Version: 3" \
   -H "Authorization: token ${TRAVIS_TOKEN}" \
   -d "$body" \
   https://api.travis-ci.com/repo/bincrafters%2Fprotobuf-integration-test/requests
