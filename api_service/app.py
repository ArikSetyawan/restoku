from flask import Flask,jsonify, request
from flask_restful import Api, Resource, reqparse
from peewee import *
import random, datetime, string

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

class checkout(BaseModel):
	id = AutoField(primary_key=True)
	trx_id = CharField()
	waktu_trx = DateTimeField()
	id_table = ForeignKeyField(table)
	id_user = ForeignKeyField(user,null=True)
	id_product = ForeignKeyField(product)
	quantity = IntegerField()
	sub_price = IntegerField()
	status = CharField(default='payment')
	payment = BooleanField(default=False)


def create_tables():
	with database:
		database.create_tables([level_user,user, jenis_product,product,table,cart,checkout])

def generate_datetime():
	tanggal = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	return tanggal

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
		parser.add_argument('username',type=str,help='must str, username')
		args = parser.parse_args()
		if args['id_user'] is None and args['username'] is None:
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
				if args['id_user'] != None and args['username'] != None :
					q_user = user.get(user.id == args['id_user'])
				elif args['id_user'] is None:
					q_user = user.get(user.username == args['username'])
				else:
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
		d_table = table.delete().where(table.id == args['id_table'])
		d_table.execute()
		return jsonify({"hasil":"table deleted Successful",'status':"000"})

class resource_cart(Resource):
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('id_table', required=True, type=int, help='must int, id_table')
		parser.add_argument('id_cart', type=int, help='must int, id_cart')
		args = parser.parse_args()
		if args['id_cart'] is None:
			# Query Cart
			q_cart = cart.select().where(cart.id_table == args['id_table'])
			data_cart = []
			if q_cart.exists():
				for i in q_cart:
					data = {}
					data['id'] = i.id
					data['id_table'] = int(str(i.id_table))
					data['nama_table'] = i.id_table.nama_table
					data['id_user'] = i.id_user
					data['id_product'] = int(str(i.id_product))
					data['nama_produk'] = i.id_product.nama_produk
					data['foto_produk'] = i.id_product.foto_produk
					data['description'] = i.id_product.description
					data['harga_produk'] = i.id_product.harga_produk
					data['quantity'] = i.quantity
					data['sub_price'] = i.sub_price
					data_cart.append(data)
				datas = {}
				datas['item'] = data_cart
				datas['qty_all_item'] = cart.select(fn.SUM(cart.quantity)).where(cart.id_table == args['id_table']).scalar()
				datas['grand_price'] = cart.select(fn.SUM(cart.sub_price)).where(cart.id_table == args['id_table']).scalar()
				return jsonify({"hasil":datas,'status':'000'})
			else:
				datas = {}
				datas['item'] = data_cart
				datas['qty_all_item'] = cart.select(fn.SUM(cart.quantity)).where(cart.id_table == args['id_table']).scalar()
				datas['grand_price'] = cart.select(fn.SUM(cart.sub_price)).where(cart.id_table == args['id_table']).scalar()
				return jsonify({"hasil":datas,'status':'001'})
		else:
			try:
				# Query Cart
				q_cart = cart.get((cart.id_table == args['id_table'])&(cart.id == args['id_cart']))
				data_cart = {}
				data_cart['id'] = q_cart.id
				data_cart['id_table'] = int(str(q_cart.id_table))
				data_cart['nama_table'] = q_cart.id_table.nama_table
				data_cart['id_user'] = q_cart.id_user
				data_cart['id_product'] = int(str(q_cart.id_product))
				data_cart['nama_produk'] = q_cart.id_product.nama_produk
				data_cart['foto_produk'] = q_cart.id_product.foto_produk
				data_cart['description'] = q_cart.id_product.description
				data_cart['harga_produk'] = q_cart.id_product.harga_produk
				data_cart['quantity'] = q_cart.quantity
				data_cart['sub_price'] = q_cart.sub_price

				return jsonify({"hasil":data_cart,'status':'000'})
			except DoesNotExist:
				return jsonify({"hasil":'Cart Tidak Tersedia tidak tersedia','status':'001'})

	def post(self):
		try:
			datas = request.json
			id_product = str(datas['id_product'])
			id_table = int(datas['id_table'])
			quantity = int(datas['quantity'])
			
			cek_cart = cart.select().where((cart.id_table == id_table)&(cart.id_product == id_product))
			sub_price = int(product.get(product.id == id_product).harga_produk) * quantity
			if cek_cart.exists():
				cek_cart = cek_cart.get()
				quantity = int(cek_cart.quantity) + int(quantity)
				sub_price = int(cek_cart.sub_price) + int(sub_price)
				d_cart = cart.update(quantity=quantity,sub_price=sub_price).where(cart.id_table == id_table)
				d_cart.execute()

				qty_all = cart.select(fn.SUM(cart.quantity)).where(cart.id_table == id_table).scalar()
				return jsonify({"hasil":"Added To Cart Successful",'status':"000","quantity":qty_all})
			else:
				sub_price = int(product.get(product.id == id_product).harga_produk) * quantity
				cart.create(
					id_product=id_product,
					id_table = id_table,
					quantity= quantity,
					sub_price= sub_price
				)
				qty_all = cart.select(fn.SUM(cart.quantity)).where(cart.id_table == id_table).scalar()
				return jsonify({"hasil":"Added To Cart Successful",'status':"000","quantity":qty_all})
		except KeyError:
			return jsonify({"hasil":"json data key invalid","status":"003"})
		except TypeError:
			return jsonify({"hasil":"json data required","status":"004"})
		except ValueError:
			return jsonify({"hasil":"json data type invalid",'status':'005'})

	def put(self):
		try:
			datas = request.json
			id_cart = int(datas['id_cart'])
			id_product = int(datas['id_product'])
			id_table = int(datas['id_table'])
			quantity = int(datas['quantity'])

			harga_produk = product.get(product.id == id_product).harga_produk
			sub_price = quantity * harga_produk

			d_cart = cart.update(
				quantity=quantity,
				sub_price=sub_price).where((cart.id_table == id_table)&(cart.id == id_cart)&(cart.id_product == id_product))
			d_cart.execute()
			qty_all = cart.select(fn.SUM(cart.quantity)).where(cart.id_table == id_table).scalar()
			return jsonify({"hasil":"Cart Edited Successful","status":"000","quantity":qty_all})
		except DoesNotExist:
			return jsonify({"hasil":"Some Error~","status":"009"})
		except KeyError:
			return jsonify({"hasil":"json data key invalid","status":"003"})
		except TypeError:
			return jsonify({"hasil":"json data required","status":"004"})
		except ValueError:
			return jsonify({"hasil":"json data type invalid",'status':'005'})
	
	def delete(self):
		parser = reqparse.RequestParser()
		parser.add_argument('id_table', required=True, type=int, help='must int, id_table')
		parser.add_argument('id_cart', type=int, help='must int, id_cart')
		args = parser.parse_args()
		if args['id_cart'] is None:
			d_cart = cart.delete().where(cart.id_table == args['id_table'])
			d_cart.execute()
			return jsonify({"hasil":"Deleted",'status':'000'})
		else:
			d_cart = cart.delete().where((cart.id == args['id_cart'])&(cart.id_table == args['id_table']))
			d_cart.execute()
			qty_all = cart.select(fn.SUM(cart.quantity)).where(cart.id_table == args['id_table']).scalar()
			return jsonify({"hasil":'cart {} Deleted'.format(args['id_cart']),'status':'000','quantity':qty_all})


class resource_order(Resource):
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('trx_id',type=str,help='must str,transaction id')
		parser.add_argument('id_user',type=int,help='must int,id user')
		args = parser.parse_args()

		if args['trx_id'] is None and args['id_user'] is None :
			orders = []

			# select all trx_id where payment = False
			all_trx_id  = checkout.select().group_by(checkout.trx_id).order_by(checkout.waktu_trx.desc())
			for i in all_trx_id:
				data_trx = {}
				item_trx = []
				# select trx
				trx =  checkout.select().where(checkout.trx_id == i.trx_id)
				for j in trx:
					data = {}
					data['id'] = j.id
					data['id_product'] = int(str(j.id_product))
					data['nama_produk'] = j.id_product.nama_produk
					data['foto_produk'] = j.id_product.foto_produk
					data['quantity'] = j.quantity
					item_trx.append(data)
				data_trx['status'] = i.status
				data_trx['item'] = item_trx
				data_trx['payment'] = i.payment
				data_trx['qty_all_item'] = checkout.select(fn.SUM(checkout.quantity)).where(checkout.trx_id == i.trx_id).scalar()
				data_trx['grand_price'] = checkout.select(fn.SUM(checkout.sub_price)).where(checkout.trx_id == i.trx_id).scalar()
				data_trx['trx_id'] = i.trx_id
				data_trx['waktu_trx'] = i.waktu_trx
				data_trx['table'] = i.id_table.nama_table
				orders.append(data_trx)
			return jsonify({"hasil":orders,'status':'000'})
		elif args['trx_id'] is not None and args['id_user'] is None:
			orders = []

			# select all trx_id where payment = False and trx_id = args[trx_id]
			all_trx_id  = checkout.select().where((checkout.trx_id == args['trx_id'])).group_by(checkout.trx_id).order_by(checkout.waktu_trx.desc())
			for i in all_trx_id:
				data_trx = {}
				item_trx = []
				# select trx
				trx =  checkout.select().where(checkout.trx_id == i.trx_id)
				for j in trx:
					data = {}
					data['id'] = j.id
					data['id_product'] = int(str(j.id_product))
					data['nama_produk'] = j.id_product.nama_produk
					data['foto_produk'] = j.id_product.foto_produk
					data['quantity'] = j.quantity
					item_trx.append(data)
				data_trx['status'] = i.status
				data_trx['payment'] = i.payment
				data_trx['item'] = item_trx
				data_trx['qty_all_item'] = checkout.select(fn.SUM(checkout.quantity)).where(checkout.trx_id == i.trx_id).scalar()
				data_trx['grand_price'] = checkout.select(fn.SUM(checkout.sub_price)).where(checkout.trx_id == i.trx_id).scalar()
				data_trx['trx_id'] = i.trx_id
				data_trx['waktu_trx'] = i.waktu_trx
				data_trx['table'] = i.id_table.nama_table
				orders.append(data_trx)
			return jsonify({"hasil":orders,'status':'000'})
		elif args['trx_id'] is None and args['id_user'] is not None:
			orders = []

			# select all trx_id where payment = False and trx_id = args[trx_id]
			all_trx_id  = checkout.select().where((checkout.id_user == args['id_user'])).group_by(checkout.trx_id).order_by(checkout.waktu_trx.desc())
			for i in all_trx_id:
				data_trx = {}
				item_trx = []
				# select trx
				trx =  checkout.select().where(checkout.trx_id == i.trx_id)
				for j in trx:
					data = {}
					data['id'] = j.id
					data['id_product'] = int(str(j.id_product))
					data['nama_produk'] = j.id_product.nama_produk
					data['foto_produk'] = j.id_product.foto_produk
					data['quantity'] = j.quantity
					item_trx.append(data)
				data_trx['status'] = i.status
				data_trx['item'] = item_trx
				data_trx['payment'] = i.payment
				data_trx['qty_all_item'] = checkout.select(fn.SUM(checkout.quantity)).where(checkout.trx_id == i.trx_id).scalar()
				data_trx['grand_price'] = checkout.select(fn.SUM(checkout.sub_price)).where(checkout.trx_id == i.trx_id).scalar()
				data_trx['trx_id'] = i.trx_id
				data_trx['waktu_trx'] = i.waktu_trx
				data_trx['table'] = i.id_table.nama_table
				orders.append(data_trx)
			return jsonify({"hasil":orders,'status':'000'})
		else:
			return jsonify({"hasil":'dont put trx_id and id_user. use one of those','status':'000'})

	# Function for accept transaction if customer already pay the bills
	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument('trx_id',required=True,type=str,help='trx_id,must str')
		args = parser.parse_args()

		# Check transaction is exists
		transaction = checkout.select().where((checkout.trx_id == args['trx_id'])&(checkout.payment == False))
		if transaction.exists():
			transaction = checkout.update(payment=True,status='dimasak').where(checkout.trx_id == args['trx_id'])
			transaction.execute()
			return jsonify({"hasil":"Transaction Processed",'status':'000'})
		else:
			return jsonify({"hasil":"Transaction Not Found",'status':'001'})

	# Function for finish the transaction and serve food to customer
	def put(self):
		parser = reqparse.RequestParser()
		parser.add_argument('trx_id',required=True,type=str,help='trx_id,must str')
		args = parser.parse_args()
		
		# Check transaction is exists
		transaction = checkout.select().where((checkout.trx_id == args['trx_id'])&(checkout.payment == True)&(checkout.status == 'dimasak'))
		if transaction.exists():
			transaction = checkout.update(status='selesai').where(checkout.trx_id == args['trx_id'])
			transaction.execute()
			return jsonify({"hasil":"Transaction Complete",'status':'000'})
		else:
			return jsonify({"hasil":"Transaction Not Found",'status':'001'})

	# function for delete transaction if customer refuse to pay bills
	def delete(self):
		parser = reqparse.RequestParser()
		parser.add_argument('trx_id',required=True,type=str,help='trx_id,must str')
		args = parser.parse_args()

		# Check transaction is exists
		transaction = checkout.select().where((checkout.trx_id == args['trx_id'])&(checkout.payment == False))
		if transaction.exists():
			transaction = checkout.delete().where(checkout.trx_id == args['trx_id'])
			transaction.execute()
			return jsonify({"hasil":"Transaction Deleted",'status':'000'})
		else:
			return jsonify({"hasil":"Transaction Not Found",'status':'001'})

class resource_checkout(Resource):
	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument('id_table',required=True,type=int,help='must int, id_table, required')
		parser.add_argument('id_user',type=int,help='must int, id_table')
		args = parser.parse_args()

		# check user
		if args['id_user'] is not None:
			try:
				# query user
				d_user = user.get(user.id == args['id_user']).id
			except DoesNotExist:
				return jsonify({"hasil":"User Not Found","status":"001"})
		else:
			d_user = None
		
		# query cart
		query_cart = cart.select().where(cart.id_table == args['id_table'])
		# check if any item in cart
		if query_cart.exists():
			# Insert into checkout
			waktu_trx = generate_datetime()
			trx_id = 'TYA-{}-'.format(query_cart.get().id_table.nama_table)+''.join(random.choice(string.digits) for _ in range(14))
			for i in query_cart:
				checkout.create(
					trx_id=trx_id,
					waktu_trx=waktu_trx,
					id_table = i.id_table,
					id_user = d_user,
					id_product = i.id_product,
					quantity = i.quantity,
					sub_price = i.sub_price)
			
			# Make return Orders/bill
			data_cart = []
			for i in query_cart:
				data = {}
				data['nama_table'] = i.id_table.nama_table
				data['nama_produk'] = i.id_product.nama_produk
				data['harga_produk'] = i.id_product.harga_produk
				data['quantity'] = i.quantity
				data['sub_price'] = i.sub_price
				data_cart.append(data)
			orders = {}
			orders['items'] = data_cart
			orders['qty_all_item'] = cart.select(fn.SUM(cart.quantity)).where(cart.id_table == args['id_table']).scalar()
			orders['grand_price'] = cart.select(fn.SUM(cart.sub_price)).where(cart.id_table == args['id_table']).scalar()
			orders['trx_id'] = trx_id
			orders['waktu_trx'] = waktu_trx
			# Delete all item in cart
			d_cart = cart.delete().where(cart.id_table == args['id_table'])
			d_cart.execute()
			return jsonify({"hasil":"checkout Success",'orders':orders,'status':'000'})
		# Return checkout failed because no items found in cart
		else:
			return jsonify({"hasil":"checkout failed. no item found in cart",'status':'001'})


api.add_resource(resource_level_user, '/api/level_user/')
api.add_resource(resource_user, '/api/user/')
api.add_resource(resource_jenis_product,'/api/jenis_product/')
api.add_resource(resource_product, '/api/product/')
api.add_resource(resource_table, '/api/table/')
api.add_resource(resource_cart, '/api/cart/')
api.add_resource(resource_order,'/api/orders/')
api.add_resource(resource_checkout, '/api/checkout/')

if __name__ == '__main__':
	create_tables()
	app.run(debug=True)