# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /code

# Copy the requirements file into the container at /code
COPY ./requirements.txt /code/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the rest of the frontend application code
COPY . /code/

# Make port 8081 available
EXPOSE 8081

# Run the frontend application when the container launches
# Use 0.0.0.0 to be accessible from outside the container
CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "8081"]
