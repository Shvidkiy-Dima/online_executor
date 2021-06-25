#!/bin/sh

sleep 5

celery -A project worker -l info --beat
