FROM python:3.8
RUN pip install --upgrade pip

WORKDIR /app 

COPY requirements.txt ./requirements.txt


RUN pip install -r requirements.txt

EXPOSE 8501

COPY . /app

ENTRYPOINT ["streamlit","run"]

CMD ["Home.py"]