FROM tensorflow/tensorflow

ADD requirements.txt .

RUN pip install -r requirements.txt

COPY HW2.py /app/HW2.py

CMD ["python","/app/HW2.py"]
