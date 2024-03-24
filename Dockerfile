FROM python as content_moderator_image

WORKDIR /usr/niko/content-moderator

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
CMD [ "uvicorn", "router:content_moderator --reload" ]