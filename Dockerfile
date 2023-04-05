FROM ubuntu:latest

ENV TZ=Asia/Dubai

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezoneENV TZ=Asia/Dubai

# Update whole system and install python pip
RUN apt update

RUN echo 'y' | apt update

RUN echo 'y' | apt install python3-pip

RUN echo 'y' | apt install wget

# Let's install MongoDb
RUN apt-get install gnupg

RUN wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add -

RUN echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list

RUN apt-get update && apt-get install -y mongodb-org

# Enable and start MongoDb

CMD ["mongod"]

# Install Python dependencies

RUN pip install bson && pip install grpcio && pip install grpcio-tools && pip install pycryptodome && pip install pycryptodomex && pip install python-dotenv && pip install pymongo

# App
ADD MOM /home/ubuntu/MOM

EXPOSE 8000

EXPOSE 50051

CMD ["python3", "/home/ubuntu/MOM/Api.py"]