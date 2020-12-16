FROM python:3
COPY ./src/config.json /code/
COPY ./src/SimilarityService /code/similarityservice/
WORKDIR code/similarityservice
RUN pip install -r requirements.txt
CMD ["python", "similarity_service.py"]