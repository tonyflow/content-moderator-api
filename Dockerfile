FROM python as content_moderator_image

WORKDIR /usr/niko/content-moderator

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "router:content_moderator", "--reload", "--host", "0.0.0.0", "--port", "8000"]
