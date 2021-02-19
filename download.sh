#!/bin/bash

until python download.py; do
  echo Download disrupted, retrying in 10 seconds...
  sleep 10
done