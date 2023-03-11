#!/bin/bash

# Checks for updates
git pull

# Places function and dependencies in their proper directories
pip install -r requirements.txt --target=lambda

# Clones or pulls postgres db dependency
if cd awslambda-psycopg2; then
  git pull
  cd ..
else
  git clone https://github.com/jkehler/awslambda-psycopg2.git
fi

# Places dependency files in their proper directory
mkdir lambda/psycopg2
cp -pr awslambda-psycopg2/psycopg2-3.9/* lambda/psycopg2/

cd lambda
zip -r ../function.zip .
