# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . /usr/src/app

EXPOSE 3306
# Run the Python script when the container launches
CMD ["python", "./dbmysql.py"]
