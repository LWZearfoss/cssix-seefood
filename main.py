import argparse
import cloudstorage
import google.cloud
import io
from flask import Flask, redirect, render_template, request, url_for
from google.appengine.ext import blobstore, ndb
from google.appengine.api import app_identity, images

app = Flask(__name__)

class Image(ndb.Model):
    image_url = ndb.StringProperty()
    image_blob = ndb.BlobKeyProperty()

@app.route('/', methods=['GET', 'POST'])
def upload_form():
    if request.method == 'GET':
        return render_template('form.html')
    else:
        image_file = request.files['file']
        image_data = image_file.stream.read()

        filename = '/' + app_identity.get_default_gcs_bucket_name() + '/' + \
            image_file.filename

        with cloudstorage.open(
            filename, mode='w', content_type=image_file.mimetype,
            retry_params=cloudstorage.RetryParams(backoff_factor=1.1)
        ) as gcs:
            gcs.write(image_data)

        blob_key = blobstore.create_gs_key('/gs' + filename)
        image_url = images.get_serving_url(blob_key=blob_key)

        image = Image(
            image_url=image_url,
            image_blob=blobstore.BlobKey(blob_key),
        )
        image.put()

        return redirect(url_for('map', id=image.key.urlsafe()))

def detect_web_uri(uri):
    client = vision.ImageAnnotatorClient()
    image = vision.types.Image()
    image.source.image_uri = uri

    response = client.web_detection(image=image)
    annotations = response.web_detection

    if annotations.web_entities:
        query = annotations.web_entities[0].score
        return query

@app.route('/map/<id>')
def map(id):
    image_key = ndb.Key(urlsafe=id)
    image = image_key.get()
    return render_template('map.html')
