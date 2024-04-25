FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY pipeline.py .
COPY extract.py .
COPY transform.py .
COPY load.py .

CMD [ "pipeline.handler" ]