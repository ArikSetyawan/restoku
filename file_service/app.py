from flask import Flask, request, jsonify
from flask_restx import Api, Resource, reqparse
from peewee import *
import os, string, random, base64, io
from PIL import Image

from playhouse.db_url import connect
# Models

# SQLITE
db = 'myresto_fileservice.db'
database = SqliteDatabase(db)


# POSTGRESQL
# database = connect(os.environ.get('DATABASE_URL'))

class BaseModel(Model):
	class Meta:
		database = database

class image_file(BaseModel):
	id = AutoField(primary_key=True)
	nama_file = CharField(unique=True)
	link = CharField(unique=True)

def create_tables():
	with database:
		database.create_tables([image_file])


app = Flask(__name__)
api = Api(app,doc=False)

base_dev_url = "http://127.0.0.1:5001"
base_prod_url = "http://restokuimage.mastya.my.id"

# config
app.config['imgdir'] = 'static/img/product'

class index(Resource):
	def get(self):
		datas = image_file.select()
		data_image = []
		if datas.exists():
			for i in datas:
				data = {}
				data['id'] = i.id
				data['nama_file'] = i.nama_file
				data['link'] = i.link
				data_image.append(data)
			return jsonify({"hasil":data_image,"status":"success"})
		else:
			return jsonify({"hasil":data_image,"status":"gagal"})

class resource_image_upload(Resource):
	def post(self):
		try:
			datas = request.json
			gambar = datas['gambar']
			ext = datas['ext']
			filename = 'restokuimage_'+''.join(random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for _ in range(10))+"."+ext

			image = base64.b64decode(str(gambar))
			img = Image.open(io.BytesIO(image))

			img.save(os.path.join(app.config['imgdir'],filename))


			# file url
			link = '{}/static/img/product/{}'.format(base_prod_url,filename)

			image_file.create(
					nama_file=filename,
					link=link
				)
			return jsonify({"hasil":"created","link":link,"filename":filename,'status':"success"})
		except KeyError:
			respon = jsonify({"hasil":"Gagal","status":"gagal"})
			respon.status_code = 300
			return respon
		except ValueError:
			respon = jsonify({"hasil":"Gagal","status":"gagal"})
			respon.status_code = 400
			return respon

	def put(self):
		try:
			datas = request.json
			gambar = datas['gambar']
			old_filename = datas['old_filename']
			ext = datas['ext']
			filename = 'restokuimage_'+''.join(random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for _ in range(10))+"."+ext

			# menghapus fotolama
			old_filename = image_file.get(image_file.link == old_filename)
			os.remove(os.path.join(app.config['imgdir'],old_filename.nama_file))
			
			image = base64.b64decode(str(gambar))
			img = Image.open(io.BytesIO(image))

			img.save(os.path.join(app.config['imgdir'],filename))

			# file url
			link = '{}/static/img/product/{}'.format(base_prod_url,filename)

			d_image = image_file.update(
						nama_file=filename,
						link=link
						).where(image_file.id == old_filename.id)
			d_image.execute()
			return jsonify({"hasil":"created","link":link,"filename":filename,'status':"success"})
		except DoesNotExists:
			respon = jsonify({"hasil":"Gagal","status":"gagal"})
			respon.status_code = 300
			return respon
		except KeyError:
			respon = jsonify({"hasil":"Gagal","status":"gagal"})
			respon.status_code = 400
			return respon
		except ValueError:
			respon = jsonify({"hasil":"Gagal","status":"gagal"})
			respon.status_code = 500
			return respon

	def delete(self):
		try:
			datas = request.json
			old_filename = str(datas['old_filename'])

			old_filename = image_file.get(image_file.link == old_filename)
			os.remove(os.path.join(app.config['imgdir'],old_filename.nama_file))

			d_image = image_file.delete().where(image_file.id == old_filename.id)
			d_image.execute()
			return jsonify({"hasil":"success","status":"success"})
		except DoesNotExists:
			respon = jsonify({"hasil":"Gagal","status":"gagal"})
			respon.status_code = 300
			return respon
		except KeyError:
			respon = jsonify({"hasil":"Gagal","status":"gagal"})
			respon.status_code = 400
			return respon
		except ValueError:
			respon = jsonify({"hasil":"Gagal","status":"gagal"})
			respon.status_code = 500
			return respon

api.add_resource(resource_image_upload, '/api/restokuimage/')
api.add_resource(index,'/')

if __name__ == "__main__":
	create_tables()
	app.run(port=5001, debug=True)
