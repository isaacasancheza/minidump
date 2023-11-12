#!/usr/bin/env sh
pipenv requirements > requirements.txt \
&& docker run --rm --mount type=bind,source="$(pwd)",target=/var/task public.ecr.aws/sam/build-python3.11 /bin/sh -c "pip install -r requirements.txt -t chalice/vendor/python" \
&& rm requirements.txt
