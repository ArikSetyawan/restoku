from flask import Flask,jsonify, request
from flask_restful import Api, Resource, reqparse
from peewee import *

# status docs:
# 000 = Success
# 000 = DoesNotExist


db = 'myresto.db'
database = SqliteDatabase(db)
class BaseModel(Model):
	class Meta:
		database=database

class level_user(BaseModel):
	id = AutoField(primary_key=True)
	nama_level = CharField(unique=True)

class user(BaseModel):
	id = AutoField(primary_key=True)
	id_level = ForeignKeyField(level_user)
	username = CharField(unique=True)
	password = CharField()
	nama_user = CharField()
	point = IntegerField(default=0)

class jenis_product(BaseModel):
	id = AutoField(primary_key=True)
	nama_jenis_product = CharField(unique=True)

class product(BaseModel):
	id = AutoField(primary_key=True)
	id_jenis_product = ForeignKeyField(jenis_product)
	nama_produk = CharField(unique=True)
	harga_produk = IntegerField()
	foto_produk = CharField(unique=True)
	description = TextField()

class table(BaseModel):
	id = AutoField(primary_key=True)
	nama_table = CharField(unique=True)
	available = BooleanField(default=True)

class cart(BaseModel):
	id = AutoField(primary_key=True)
	id_table = ForeignKeyField(table)
	id_user = ForeignKeyField(user,null=True)
	id_product = ForeignKeyField(product)
	quantity = IntegerField()
	sub_price = IntegerField()

def create_tables():
	with database:
		database.create_tables([level_user,user, jenis_product,product,table,cart])

app = Flask(__name__)
api = Api(app)

class resource_level_user(Resource):
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument("id_level", type=int, help="must int, id_level")
		args = parser.parse_args()
		if args['id_level'] is None:
			# kueri level user
			q_level_user = level_user.select()
			data_level_user = []
			if q_level_user.exists():
				for i in q_level_user:
					data = {}
					data['id_level'] = i.id
					data['nama_level'] = i.nama_level
					data_level_user.append(data)
				return jsonify({"hasil":data_level_user,"status":'000'})
			else:
				return jsonify({"hasil":data_level_user,"status":'001'})
		else:
			# kueri level_user
			try:
				id_level = args['id_level']
				q_level_user = level_user.get(level_user.id == id_level)
				data_level_user = {'id_level':q_level_user.id,'nama_level':q_level_user.nama_level}
				return jsonify({"hasil":data_level_user,"status":'000'})
			except DoesNotExist:
				return jsonify({"hasil":"Level User Tak Ditemukan",'status':'001'})

	def post(self):
		try:
			datas = request.json
			nama_level = str(datas['nama_level'])
			level_user.create(nama_level=nama_level)
			return jsonify({"hasil":"Success Created","status":"000"})
		except IntegrityError:
			return jsonify({"hasil":"level already created","status":"002"})
		except KeyError:
			return jsonify({"hasil":"json data key invalid","status":"003"})
		except TypeError:
			return jsonify({"hasil":"json data required","status":"004"})

	def put(self):
		try:
			datas = request.json
			id_level = int(datas['id_level'])
			nama_level = str(datas['nama_level'])
			data_level_user = level_user.update(nama_level=nama_level).where(level_user.id == id_level)
			data_level_user.execute()
			return jsonify({"hasil":"Level Edited Successful",'status':'000'})
		except IntegrityError:
			return jsonify({"hasil":"level already created","status":"002"})
		except KeyError:
			return jsonify({"hasil":"json data key invalid","status":"003"})
		except TypeError:
			return jsonify({"hasil":"json data required","status":"004"})
		except ValueError:
			return jsonify({"hasil":"json data type invalid",'status':'005'})

	def delete(self):
		try:
			parser = reqparse.RequestParser()
			parser.add_argument("id_level",type=int,required=True,help='must Int, id_level')
			args = parser.parse_args()
			d_level_user = level_user.delete().where(level_user.id == args['id_level'])
			d_level_user.execute()
			return jsonify({"hasil":"level_user Deleted","status":"000"})
		except KeyError:
			return jsonify({"hasil":"json data key invalid","status":"003"})

class resource_user(Resource):
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('id_user',type=int,help='must int, id_user')
		args = parser.parse_args()
		if args['id_user'] is None:
			# QUery User
			q_user = user.select()
			data_user = []
			if q_user.exists():
				for i in q_user:
					data = {}
					data['id'] = i.id
					data['id_level'] = int(str(i.id_level))
					data['nama_level'] = i.id_level.nama_level
					data['username'] = i.username
					data['password'] = i.password
					data['nama_user'] = i.nama_user
					data['point'] = i.point
					data_user.append(data)
				return jsonify({"hasil":data_user,"status":'000'})
			else:
				return jsonify({"hasil":data_user,"status":'001'})
		else:
			try:
				# Query User
				q_user = user.get(user.id == args['id_user'])
				data_user = {
					'id' : q_user.id,
					'id_level' : int(str(q_user.id_level)),
					'nama_level' : q_user.id_level.nama_level,
					'username' : q_user.username,
					'password' : q_user.password,
					'nama_user' : q_user.nama_user,
					'point' : q_user.point,
				}
				return jsonify({"hasil":data_user,'status':"000"})
			except DoesNotExist:
				return jsonify({"hasil":"user tak ditemukan",'status':"001"})

	def post(self):
		try:
			data = request.json
			id_level = int(data['id_level'])
			username = str(data['username'])
			password = str(data['password'])
			nama_user = str(data['nama_user'])

			user.create(
				id_level = id_level,
				username = username,
				password = password,
				nama_user = nama_user)

			return jsonify({"hasil":"User created","status":"000"})
		except IntegrityError:
			return jsonify({"hasil":"User already created",'status':"002"})
		except KeyError:
			return jsonify({"hasil":"json data key invalid","status":"003"})
		except TypeError:
			return jsonify({"hasil":"json data required","status":"004"})
		except ValueError:
			return jsonify({"hasil":"json data type invalid",'status':'005'})

	def put(self):
		try:
			data = request.json
			id_user = int(data['id_user'])
			id_level = int(data['id_level'])
			username = str(data['username'])
			password = str(data['password'])
			nama_user = str(data['nama_user'])

			d_user = user.update(
				id_level = id_level,
				username = username,
				password = password,
				nama_user = nama_user).where(user.id == id_user)
			d_user.execute()

			return jsonify({"hasil":"User Edited","status":"000"})
		except IntegrityError:
			return jsonify({"hasil":"User already created",'status':"002"})
		except KeyError:
			return jsonify({"hasil":"json data key invalid","status":"003"})
		except TypeError:
			return jsonify({"hasil":"json data required","status":"004"})
		except ValueError:
			return jsonify({"hasil":"json data type invalid",'status':'005'})

	def delete(self):
		try:
			parser = reqparse.RequestParser()
			parser.add_argument("id_user",type=int,required=True,help='must Int, id_user')
			args = parser.parse_args()
			d_user = user.delete().where(user.id == args['id_user'])
			d_user.execute()
			return jsonify({"hasil":"User Deleted","status":"000"})
		except KeyError:
			return jsonify({"hasil":"json data key invalid","status":"003"})


class resource_jenis_product(Resource):
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('id_jenis_product',type=int,help='must int, id_jenis_product')
		args = parser.parse_args()
		if args['id_jenis_product'] is None:
			q_jenis_product = jenis_product.select()
			data_jenis_product = []
			if q_jenis_product.exists():
				for i in q_jenis_product:
					data = {}
					data['id'] = i.id
					data['nama_jenis_product'] = i.nama_jenis_product
					data_jenis_product.append(data)
				return jsonify({"hasil":data_jenis_product,"status":"000"})
			else:
				return jsonify({"hasil":data_jenis_product,"status":"001"})
		else:
			try:
				q_jenis_product = jenis_product.get(jenis_product.id == args['id_jenis_product'])
				data_jenis_product = {
					'id':q_jenis_product.id,
					"nama_jenis_product":q_jenis_product.nama_jenis_product
				}
				return jsonify({"hasil":data_jenis_product,'status':"000"})
			except DoesNotExist:
				return jsonify({"hasil":"jenis_product tidak ditemukan","status":"001"})

	def post(self):
		try:
			data = request.json
			nama_jenis_product = str(data['nama_jenis_product'])
			jenis_product.create(nama_jenis_product=nama_jenis_product)
			return jsonify({"hasil":"jenis_product created","status":"000"})
		except IntegrityError:
			return jsonify({"hasil":"jenis_product already created",'status':"002"})
		except KeyError:
			return jsonify({"hasil":"json data key invalid","status":"003"})
		except TypeError:
			return jsonify({"hasil":"json data required","status":"004"})
		except ValueError:
			return jsonify({"hasil":"json data type invalid",'status':'005'})

	def put(self):
		try:
			data = request.json
			id_jenis_product = int(data['id_jenis_product'])
			nama_jenis_product = str(data['nama_jenis_product'])
			update_jenis_product = jenis_product.update(
				nama_jenis_product=nama_jenis_product).where(jenis_product.id == id_jenis_product)
			update_jenis_product.execute()
			return jsonify({"hasil":"jenis_product updated","status":"000"})
		except IntegrityError:
			return jsonify({"hasil":"jenis_product already created",'status':"002"})
		except KeyError:
			return jsonify({"hasil":"json data key invalid","status":"003"})
		except TypeError:
			return jsonify({"hasil":"json data required","status":"004"})
		except ValueError:
			return jsonify({"hasil":"json data type invalid",'status':'005'})

	def delete(self):
		try:
			parser = reqparse.RequestParser()
			parser.add_argument('id_jenis_product',type=int,required=True,help='must int,required,id_jenis_product')
			args = parser.parse_args()
			d_jenis_product = jenis_product.delete().where(jenis_product.id == args['id_jenis_product'])
			d_jenis_product.execute()
			return jsonify({"hasil":"jenis_product deleted",'status':"000"}) 
		except KeyError:
			return jsonify({"hasil":"json data key invalid","status":"003"})



class resource_product(Resource):
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('id_product', type=int, help='must int, id_product')
		args = parser.parse_args()
		if args['id_product'] is None:
			# Query product
			q_product = product.select()
			data_product = []
			if q_product.exists():
				for i in q_product:
					data = {}
					data['id'] = i.id
					data['id_jenis_product'] = int(str(i.id_jenis_product))
					data['jenis_product'] = i.id_jenis_product.nama_jenis_product
					data['nama_produk'] = i.nama_produk
					data['harga_produk'] = i.harga_produk
					data['foto_produk'] = i.foto_produk
					data['description'] = i.description
					data_product.append(data)
				return jsonify({"hasil":data_product,'status':'000'})
			else:
				return jsonify({"hasil":data_product,'status':'001'})
		else:
			try:
				# Query Product
				q_product = product.get(product.id == args['id_product'])
				data_product = {
					'id': q_product.id,
					'id_jenis_product' : int(str(q_product.id_jenis_product)),
					'jenis_product' : q_product.id_jenis_product.nama_jenis_product,
					'nama_produk' : q_product.nama_produk,
					'harga_produk' : q_product.harga_produk,
					'foto_produk' : q_product.foto_produk,
					'description' : q_product.description
				}
				return jsonify({"hasil":data_product,'status':'000'})
			except DoesNotExist:
				return jsonify({"hasil":'Product tidak tersedia','status':'001'})

	def post(self):
		try:
			datas = request.json
			nama_produk = str(datas['nama_produk'])
			id_jenis_product = int(datas['id_jenis_product'])
			harga_produk = int(datas['harga_produk'])
			foto_produk = str(datas['foto_produk'])
			description = str(datas['description'])

			product.create(
					nama_produk=nama_produk,
					id_jenis_product=id_jenis_product,
					harga_produk=harga_produk,
					foto_produk=foto_produk,
					description=description
				)
			return jsonify({"hasil":"Product Added Successful",'status':"000"})
		except IntegrityError:
			return jsonify({"hasil":"Product already created","status":"002","foto_produk":foto_produk})
		except KeyError:
			return jsonify({"hasil":"json data key invalid","status":"003"})
		except TypeError:
			return jsonify({"hasil":"json data required","status":"004"})
		except ValueError:
			return jsonify({"hasil":"json data type invalid",'status':'005'})

	def put(self):
		try:
			datas = request.json
			id_product = int(datas['id_product'])
			nama_produk = str(datas['nama_produk'])
			id_jenis_product = int(datas['id_jenis_product'])
			harga_produk = int(datas['harga_produk'])
			foto_produk = str(datas['foto_produk'])
			description = str(datas['description'])

			d_produk = product.update(
					nama_produk = nama_produk,
					id_jenis_product=id_jenis_product,
					harga_produk = harga_produk,
					foto_produk=foto_produk,
					description=description).where(product.id == id_product)
			d_produk.execute()
			return jsonify({"hasil":"Product Edited Successful",'status':"000"})
		except IntegrityError:
			return jsonify({"hasil":"level already created","status":"002"})
		except KeyError:
			return jsonify({"hasil":"json data key invalid","status":"003"})
		except TypeError:
			return jsonify({"hasil":"json data required","status":"004"})
		except ValueError:
			return jsonify({"hasil":"json data type invalid",'status':'005'})

	def delete(self):
		try:
			parser = reqparse.RequestParser()
			parser.add_argument('id_product',type=int,required=True,help='id Product,must int')
			args = parser.parse_args()

			d_produk = product.delete().where(product.id == args['id_product'])
			d_produk.execute()
			return jsonify({"hasil":"Product Berhasil Didelete",'status':"000"})
		except KeyError:
			return jsonify({"hasil":"json data key invalid","status":"003"})

class resource_table(Resource):
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('id_table',type=int,help='id_table.Must int')
		args = parser.parse_args()
		if args['id_table'] is None:
			q_table = table.select()
			data_table = []
			if q_table.exists():
				for i in q_table:
					data = {}
					data['id'] = i.id
					data['nama_table'] = i.nama_table
					data['available'] = i.available
					data_table.append(data)
				return jsonify({"hasil":data_table,'status':"000"})
			else:
				return jsonify({"hasil":data_table,'status':"000"})
		else:
			try:
				q_table = table.get(table.id == args['id_table'])
				data_table = {}
				data_table['id'] = q_table.id
				data_table['nama_table'] = q_table.nama_table
				data_table['available'] = q_table.available
				return jsonify({"hasil":data_table,'status':'000'})
			except DoesNotExist:
				return jsonify({'hasil':"table not found",'status':"001"})

	def post(self):
		try:
			datas = request.json
			nama_table = str(datas['nama_table'])
			table.create(nama_table=nama_table)
			return jsonify({"hasil":"table created Successful",'status':"000"})
		except IntegrityError:
			return jsonify({"hasil":"table already created","status":"002"})
		except KeyError:
			return jsonify({"hasil":"json data key invalid","status":"003"})
		except TypeError:
			return jsonify({"hasil":"json data required","status":"004"})
		except ValueError:
			return jsonify({"hasil":"json data type invalid",'status':'005'})

	def put(self):
		try:
			datas = request.json
			id_table = int(datas['id_table'])
			nama_table = str(datas['nama_table'])
			d_table = table.update(nama_table=nama_table).where(table.id == id_table)
			d_table.execute()
			return jsonify({"hasil":"table created Successful",'status':"000"})
		except IntegrityError:
			return jsonify({"hasil":"table already created","status":"002"})
		except KeyError:
			return jsonify({"hasil":"json data key invalid","status":"003"})
		except TypeError:
			return jsonify({"hasil":"json data required","status":"004"})
		except ValueError:
			return jsonify({"hasil":"json data type invalid",'status':'005'})

	def delete(self):
		parser = reqparse.RequestParser()
		parser.add_argument('id_table',type=int,required=True,help='id_table.Must int')
		args = parser.parse_args()
		d_table = table.delete().where(table.id == id_table)
		d_table.execute()
		return jsonify({"hasil":"table deleted Successful",'status':"000"})

api.add_resource(resource_level_user, '/api/level_user/')
api.add_resource(resource_user, '/api/user/')
api.add_resource(resource_jenis_product,'/api/jenis_product/')
api.add_resource(resource_product, '/api/product/')
api.add_resource(resource_table, '/api/table/')

if __name__ == '__main__':
	create_tables()
	app.run(debug=True)