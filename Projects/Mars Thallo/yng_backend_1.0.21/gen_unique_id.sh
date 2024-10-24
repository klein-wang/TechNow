#!/bin/bash

#  Generate a unique timestamp in milliseconds
date +%s%3N > /app/marsproject/unique_id

exec "$@"