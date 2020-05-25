from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response
import requests,base64, datetime, random, time
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer, BadData

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissecret'

sToken = URLSafeTimedSerializer('thisissecret')
ALLOWED_EXTENSIONS = set(['png','jpeg','jpg'])


# Scheduler
from rq import Queue
from redis import Redis
from rq.registry import ScheduledJobRegistry

# Backgroun Function
import jadwal_job

# RedisLabs_Connection
url_redis = "redis-13020.c98.us-east-1-4.ec2.cloud.redislabs.com"
port_redis = "13020"
db_redis = 'restoku'
password_redis = '1U8h7PCGI7zLxfme55d493sdcWC0ioGo'
redis = Redis(host=url_redis, port=port_redis, db=0, password=password_redis)

# Localhost Connection
# redis = Redis()

queue = Queue(connection=redis)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def islogin():
	if 'user' in session:
		return True
	else:
		False

@app.before_request
def before_request():
	# Cancle Job
	# https://stackoverflow.com/questions/16793879/cancel-an-already-executing-task-in-python-rq


	now = time.time()
	# print(type(now))
	# print(now)
	if 'exp' in session:
		# print("session = {}".format(session['exp']))
		# print("now = {}".format(now))
		# print("{} - {} = {}".format(session['exp'],now,int(session['exp'] - now)))
		# print(int(session['exp'] - now))
		if int(session['exp'] - now) <= 0:
			session.pop('exp')
			session.pop('table')
			session.pop('quantity')
			# print('expired')
		else:
			# print('running')
			pass
	else:
		pass

@app.route('/')
def index():
	url_produk = "http://127.0.0.1:5000/api/product/"
	req_produk = requests.get(url_produk)

	data_produk = []

	if req_produk.json()['status']:
		for i in req_produk.json()['hasil']:
			data = {}
			data['id'] = sToken.dumps(i['id'],salt='id_produk')
			data['id_jenis_product'] = sToken.dumps(i['id_jenis_product'],salt='id_jenis_product')
			data['jenis_product'] = i['jenis_product']
			data['nama_produk'] = i['nama_produk']
			data['harga_produk'] = i['harga_produk']
			data['foto_produk'] = i['foto_produk']
			data['foto_produk_enc'] = sToken.dumps(i['foto_produk'],salt='foto_produk')
			data['description'] = i['description']
			data_produk.append(data)
	return render_template('menu.html',data_produk=data_produk)

@app.route('/login',methods=['POST'])
def login():
	return 'oke'

@app.route('/dashboard')
def dashboard():
	return render_template("blackdashboard/dashboard.html")

@app.route('/level_user',methods=['GET','POST'])
def level_user():
	if request.method == 'GET':
		url_level_user = 'http://127.0.0.1:5000/api/level_user/'
		req_level_user = requests.get(url_level_user)
		data_level_user = []
		if req_level_user.status_code == 200:
			if req_level_user.json()['status'] == "000":
				for i in req_level_user.json()['hasil']:
					data = {}
					data['id'] = sToken.dumps(i['id_level'],salt="id_level_user")
					data['nama_level'] = i['nama_level']
					data_level_user.append(data)

				return render_template('blackdashboard/level_user.html',data_level_user=data_level_user)
			return render_template('blackdashboard/level_user.html',data_level_user=data_level_user)
		return render_template('blackdashboard/level_user.html',data_level_user=data_level_user)
	else:
		d_nama_level = str(request.form['nama_level'])
		json = {
			'nama_level':d_nama_level
		}
		url_level_user = 'http://127.0.0.1:5000/api/level_user/'
		req_level_user = requests.post(url_level_user,json=json)
		if req_level_user.status_code == 200:
			flash(req_level_user.json()['hasil'])
			print(req_level_user.json()['hasil'])
			return redirect(url_for('level_user'))
		else:
			return redirect(url_for('level_user'))

@app.route('/edit_level_user/<id_level>',methods=['POST'])
def edit_level_user(id_level):
	id_level = sToken.loads(id_level,salt='id_level_user')
	d_nama_level = str(request.form['nama_level'])
	
	json = {
		'id_level':id_level,
		'nama_level':d_nama_level
	}
	url_level_user = 'http://127.0.0.1:5000/api/level_user/'
	req_level_user = requests.put(url_level_user,json=json)
	if req_level_user.status_code == 200:
		flash(req_level_user.json()['hasil'])
		print(req_level_user.json()['hasil'])
		return redirect(url_for('level_user'))
	else:
		return redirect(url_for('level_user'))

@app.route('/delete_level_user/<id_level>')
def delete_level_user(id_level):
	id_level = sToken.loads(id_level,salt='id_level_user')
	params = {
		'id_level':id_level,
	}
	url_level_user = 'http://127.0.0.1:5000/api/level_user/'
	req_level_user = requests.delete(url_level_user,params=params)
	if req_level_user.status_code == 200:
		flash(req_level_user.json()['hasil'])
		print(req_level_user.json()['hasil'])
		return redirect(url_for('level_user'))
	else:
		return redirect(url_for('level_user'))	

@app.route('/user',methods=['GET',"POST"])
def user():
	if request.method == 'GET':
		url_user = "http://127.0.0.1:5000/api/user/"
		req_user = requests.get(url_user)
		url_level_user = "http://127.0.0.1:5000/api/level_user/"
		req_level_user = requests.get(url_level_user)
		data_user = []
		data_level_user = []
		if req_user.status_code and req_level_user.status_code == 200:
			if req_user.json()['status'] and req_level_user.json()['status'] == "000":
				for i in req_user.json()['hasil']:
					data = {}
					data['id'] = sToken.dumps(i['id'],salt='id_user')
					data['id_level'] = sToken.dumps(i['id_level'],salt='id_level_user')
					data['nama_level'] = i['nama_level']
					data['username'] = i['username']
					data['password'] = i['password']
					data['nama_user'] = i['nama_user']
					data['point'] = i['point']
					data_user.append(data)

				for j in req_level_user.json()['hasil']:
					data = {}
					data['id'] = sToken.dumps(j['id_level'],salt='id_level_user')
					data['nama_level'] = j['nama_level']
					data_level_user.append(data)
				return render_template('/blackdashboard/user.html',data_user=data_user,data_level_user=data_level_user)
			return render_template('/blackdashboard/user.html',data_user=data_user,data_level_user=data_level_user)
		return render_template('/blackdashboard/user.html',data_user=data_user,data_level_user=data_level_user)
	else:
		id_level = request.form['level_user']
		nama_user = request.form['name']
		username = request.form['username']
		password = request.form['password']

		json = {
			'id_level':sToken.loads(id_level,salt='id_level_user'),
			'nama_user' : nama_user,
			'username':username,
			'password':password
		}
		url_user = "http://127.0.0.1:5000/api/user/"
		req_user = requests.post(url_user,json=json)
		return redirect(request.url)

@app.route('/edit-user/<id_user>',methods=['POST'])
def edit_user(id_user):
	id_level = request.form['level_user']
	nama_user = request.form['name']
	username = request.form['username']
	password = request.form['password']

	json = {
		'id_user':sToken.loads(id_user,salt='id_user'),
		'id_level':sToken.loads(id_level,salt='id_level_user'),
		'nama_user' : nama_user,
		'username':username,
		'password':password
	}
	url_user = "http://127.0.0.1:5000/api/user/"
	req_user = requests.put(url_user,json=json)
	return redirect(url_for('user'))

@app.route('/remove-user/<id_user>')
def remove_user(id_user):
	id_user = sToken.loads(id_user,salt='id_user')
	url_user = "http://127.0.0.1:5000/api/user/"
	req_user = requests.delete(url_user,params={'id_user':id_user})
	return redirect(url_for('user'))

@app.route('/product_category',methods=['GET','POST'])
def product_category():
	if request.method == 'GET':
		url_jenis_produk = "http://127.0.0.1:5000/api/jenis_product/"
		req_jenis_produk = requests.get(url_jenis_produk)
		data_jenis_produk = []
		if req_jenis_produk.status_code == 200:
			if req_jenis_produk.json()['status'] == "000":
				for i in req_jenis_produk.json()['hasil']:
					data = {}
					data['id'] = sToken.dumps(i['id'],salt='id_jenis_product')
					data['nama_jenis_product'] = i['nama_jenis_product']
					data_jenis_produk.append(data)
				return render_template('blackdashboard/product_category.html',data_jenis_produk=data_jenis_produk)
			return render_template('blackdashboard/product_category.html',data_jenis_produk=data_jenis_produk)
		return render_template('blackdashboard/product_category.html',data_jenis_produk=data_jenis_produk)
	else:
		d_nama_kategori = request.form['category_name']
		json = {
			'nama_jenis_product':d_nama_kategori
		}
		url_jenis_produk = "http://127.0.0.1:5000/api/jenis_product/"
		req_jenis_produk = requests.post(url_jenis_produk,json=json)
		if req_jenis_produk.status_code == 200:
			flash(req_jenis_produk.json()['hasil'])
			print(req_jenis_produk.json()['hasil'])
			return redirect(url_for('product_category'))
		else:
			flash(req_jenis_produk.json()['hasil'])
			print(req_jenis_produk.json()['hasil'])
			return redirect(url_for('product_category'))

@app.route('/edit_product_category/<id_jenis_product>',methods=['POST'])
def edit_product_category(id_jenis_product):
	id_jenis_product = sToken.loads(id_jenis_product,salt='id_jenis_product')
	d_nama_kategori = request.form['category_name']
	json = {
		'id_jenis_product':id_jenis_product,
		'nama_jenis_product':d_nama_kategori
	}
	url_jenis_produk = "http://127.0.0.1:5000/api/jenis_product/"
	req_jenis_produk = requests.put(url_jenis_produk,json=json)
	if req_jenis_produk.status_code == 200:
		flash(req_jenis_produk.json()['hasil'])
		print(req_jenis_produk.json()['hasil'])
		return redirect(url_for('product_category'))
	else:
		flash(req_jenis_produk.json()['hasil'])
		print(req_jenis_produk.json()['hasil'])
		return redirect(url_for('product_category'))

@app.route('/delete_product_category/<id_jenis_product>')
def delete_product_category(id_jenis_product):
	id_jenis_product = sToken.loads(id_jenis_product,salt='id_jenis_product')
	params = {
		'id_jenis_product':id_jenis_product,
	}
	url_jenis_produk = "http://127.0.0.1:5000/api/jenis_product/"
	req_jenis_produk = requests.delete(url_jenis_produk,params=params)
	if req_jenis_produk.status_code == 200:
		flash(req_jenis_produk.json()['hasil'])
		print(req_jenis_produk.json()['hasil'])
		return redirect(url_for('product_category'))
	else:
		flash(req_jenis_produk.json()['hasil'])
		print(req_jenis_produk.json()['hasil'])
		return redirect(url_for('product_category'))


@app.route('/product',methods=['POST',"GET"])
def product():
	if request.method == "GET":
		url_produk = "http://127.0.0.1:5000/api/product/"
		url_jenis_produk = "http://127.0.0.1:5000/api/jenis_product/"
		
		req_produk = requests.get(url_produk)
		req_jenis_produk = requests.get(url_jenis_produk)
		
		if req_produk.json()['status'] and req_jenis_produk.json()['status'] == "000":
			data_produk = []
			for i in req_produk.json()['hasil']:
				data = {}
				data['id'] = sToken.dumps(i['id'],salt='id_produk')
				data['id_jenis_product'] = sToken.dumps(i['id_jenis_product'],salt='id_jenis_product')
				data['jenis_product'] = i['jenis_product']
				data['nama_produk'] = i['nama_produk']
				data['harga_produk'] = i['harga_produk']
				data['foto_produk'] = i['foto_produk']
				data['foto_produk_enc'] = sToken.dumps(i['foto_produk'],salt='foto_produk')
				data['description'] = i['description']
				data_produk.append(data)

			data_jenis_produk = []
			for i in req_jenis_produk.json()['hasil']:
				data = {}
				data['id'] = sToken.dumps(i['id'],salt='id_jenis_product')
				data['nama_jenis_product'] = i['nama_jenis_product']
				data_jenis_produk.append(data)

			return render_template('blackdashboard/products.html',data_produk=data_produk,data_jenis_produk=data_jenis_produk)
		else:
			return render_template('product.html')
	else:
		nama_produk = request.form['nama_produk']
		id_jenis_product = sToken.loads(request.form['jenis_product'],salt='id_jenis_product')
		harga_produk = request.form['harga_produk']
		description = request.form['description']

		if 'file' not in request.files:
			return redirect(request.url)
		file = request.files['file']
		# if user does not select file, browser also
		# submit an empty part without filename
		if file.filename == '':
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)

			base64file = base64.b64encode(file.read()).decode("utf-8")
			
			ext = filename.split(".")

			form = None

			for i in ext:
				allowed = ['jpg','jpeg','png']
				if i in allowed:
					form = i
					break

			if form == None:
				return 'not supported format file'
			else:
				pass

			ext = form
					
			json = {
				'gambar' : base64file,
				'ext' : ext
			}
			photo_link = 'http://127.0.0.1:5001/api/restokuimage/'
			# photo_link = 'https://restoimg.herokuapp.com/api/restokuimage/'
			req_photo = requests.post(photo_link,json=json)
			result = req_photo.json()
			if result['status'] == 'error':
				return redirect(request.url)
			elif result['status'] == 'success':
				url = 'http://127.0.0.1:5000/api/product/'
				json = {
					"nama_produk": nama_produk,
					"harga_produk": harga_produk,
					"id_jenis_product": id_jenis_product,
					"foto_produk": result['link'],
					'description': description
				}
				req = requests.post(url,json=json)
				if req.json()['status'] == "000":
					return redirect(url_for('product'))
				elif req.json()['status'] == '002':
					json_file = {"old_filename":req.json()['foto_produk']}
					req_file = requests.delete(photo_link,json=json_file)
					if req_file.json()['status'] == 'success':
						flash(req.json()['hasil'])
						print((req.json()['hasil']))
						return redirect(url_for('product'))
					else:
						flash("Opps Something Wrong in delete photo when product name is already exists")
						print("Opps Something Wrong in delete photo when product name is already exists")
						return redirect(url_for('product'))
				else:
					flash(req.json()['hasil'])
					return redirect(url_for('product'))
			else:
				return redirect(url_for('product'))

@app.route('/editproduct/<idproduct>/<filenamephoto>', methods=['POST'])
def editproduct(idproduct,filenamephoto):
	id_produk = sToken.loads(idproduct,salt='id_produk')
	old_filename = sToken.loads(filenamephoto,salt='foto_produk')
		
	nama_produk = request.form['nama_produk']
	id_jenis_product = sToken.loads(request.form['jenis_product'],salt='id_jenis_product')
	harga_produk = request.form['harga_produk']
	description = request.form['description']

	if 'file' not in request.files:
		return redirect(request.url)
	file = request.files['file']
	
	# Handle jika user tidak ingin mengubah gambar
	if file.filename == '':
		url = 'http://127.0.0.1:5000/api/product/'
		json = {
			"id_product":id_produk,
			"nama_produk": nama_produk,
			"harga_produk": int(harga_produk),
			"id_jenis_product": id_jenis_product,
			"foto_produk": old_filename,
			'description': description
		}
		req = requests.put(url,json=json)
		return redirect(url_for('product'))
	
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)

		base64file = base64.b64encode(file.read()).decode("utf-8")
		
		ext = filename.split(".")

		form = None

		for i in ext:
			allowed = ['jpg','jpeg','png']
			if i in allowed:
				form = i
				break

		if form == None:
			return 'not supported format file'
		else:
			pass

		ext = form
				
		json = {
			'gambar' : base64file,
			'ext' : ext,
			'old_filename' : old_filename
		}
		photo_link = 'http://127.0.0.1:5001/api/restokuimage/'
		# photo_link = 'https://restoimg.herokuapp.com/api/restokuimage/'
		req_photo = requests.put(photo_link,json=json)
		result = req_photo.json()
		if result['status'] == 'error':
			return redirect(request.url)
		elif result['status'] == 'success':
			url = 'http://127.0.0.1:5000/api/product/'
			json = {
				"id_product":id_produk,
				"nama_produk": nama_produk,
				"harga_produk": harga_produk,
				"id_jenis_product": id_jenis_product,
				"foto_produk": result['link'],
				'description': description
			}
			req = requests.put(url,json=json)

			return redirect(url_for('product'))
		else:
			return redirect(url_for('product'))

@app.route("/deleteproduct/<idproduct>/<filenamephoto>")
def deleteproduct(idproduct,filenamephoto):
	id_produk = sToken.loads(idproduct,salt='id_produk')
	old_filename = sToken.loads(filenamephoto,salt='foto_produk')


	url_api = 'http://127.0.0.1:5000/api/product/'
	url_file = 'http://127.0.0.1:5001/api/restokuimage/'
	json_file = {"old_filename":old_filename}
	req_file = requests.delete(url_file,json=json_file)
	if req_file.status_code == 200:
		if req_file.json()['status'] == 'success':
			params = {"id_product":id_produk}
			req_api = requests.delete(url_api,params=params)
			print('oke')
			return redirect(url_for('product'))
		else:
			print('gagal')
			return redirect(url_for('product'))
	else:
		print("gagal")
		return redirect(url_for('product'))

@app.route('/scan-table')
def scan_table():
	if 'table' in session:
		return redirect(url_for('index'))
	return render_template('scan_table.html')

@app.route('/scan-table/<id_table>')
def scan_table_id(id_table):
	if 'table' in session:
		return redirect(url_for('index'))
	dec_id_table = sToken.loads(id_table,salt='id_table')
	session['table'] = dec_id_table
	session['quantity'] = 0

	job = queue.enqueue_in(datetime.timedelta(minutes=5),jadwal_job.background_task,dec_id_table)
	print(job.id)
	registry = ScheduledJobRegistry(queue=queue)

	resp = make_response(redirect(url_for('index')))
	expire_date = datetime.datetime.now()
	expire_date = expire_date + datetime.timedelta(minutes=5)
	resp.set_cookie('table',id_table,expires=expire_date)
	resp.set_cookie('exp',"{}".format(expire_date.timestamp()),expires=expire_date)
	session['exp'] = expire_date.timestamp()
	return resp

@app.route('/cart')
def cart():
	if 'table' in session:
		url_cart = "http://127.0.0.1:5000/api/cart/"
		req_cart = requests.get(url_cart,params={'id_table':session['table']})
		d_cart = req_cart.json()['hasil']['item']
		data_cart = []
		for i in d_cart :
			data = {}
			data['id'] = sToken.dumps(i['id'],salt='id_cart')
			data['id_table'] =  sToken.dumps(i['id_table'],salt='id_table')
			data['nama_table'] = i['nama_table']
			data['id_user'] = sToken.dumps(i['id_user'],salt='id_user')
			data['id_product'] = sToken.dumps(i['id_product'],salt='id_produk')
			data['nama_produk'] = i['nama_produk']
			data['foto_produk'] = i['foto_produk']
			data['description'] = i['description']
			data['harga_produk'] = i['harga_produk']
			data['quantity'] = i['quantity']
			data['sub_price'] = i['sub_price']
			data_cart.append(data)
		if req_cart.json()['hasil']['qty_all_item'] == None:
			qty_all_item = 0
		else:
			qty_all_item = req_cart.json()['hasil']['qty_all_item']
		grand_price = req_cart.json()['hasil']['grand_price']
		return render_template('cart.html',data_cart=data_cart,qty_all_item=qty_all_item,grand_price=grand_price)
	else:
		return redirect(url_for('index'))

@app.route('/add-to-cart/<id_produk>')
def add_to_cart(id_produk):
	if 'table' in session:
		id_produk = sToken.loads(id_produk,salt='id_produk')
		jumlah = 1
		meja = session['table']
		
		json = {
			'id_product':id_produk,
			'id_table':meja,
			'quantity':jumlah,
		}
		url_cart = "http://127.0.0.1:5000/api/cart/"
		req_cart = requests.post(url_cart,json=json)
		session['quantity'] = req_cart.json()['quantity'] if req_cart.json()['quantity'] != None else 0
		return redirect(url_for('index'))
	return redirect(url_for('index'))

@app.route('/update-cart-item',methods=['POST'])
def update_cart_item():
	id_cart = request.form['id_cart']
	id_cart = sToken.loads(id_cart,salt='id_cart')
	qty = request.form['quantity']

	# Get Cart Item Data
	url_cart = "http://127.0.0.1:5000/api/cart/"
	req_cart = requests.get(url=url_cart,params={'id_table':session['table'],'id_cart':id_cart})
	
	if req_cart.status_code == 200 and req_cart.json()['status'] == "000":
		# Updating Cart
		json = {
			'id_cart':id_cart,
			'id_product':req_cart.json()['hasil']['id_product'],
			'id_table':session['table'],
			'quantity':qty
		}
		url_cart = "http://127.0.0.1:5000/api/cart/"
		req_cart = requests.put(url_cart,json=json)
		session['quantity'] = req_cart.json()['quantity'] if req_cart.json()['quantity'] != None else 0
		return 'Berhasil Di Ubah'
	else:
		return 'gagal'

@app.route('/delete-cart-item/<id_cart>')
def delete_cart_item(id_cart):
	id_cart = sToken.loads(id_cart,salt='id_cart',max_age=300)
	url_cart = "http://127.0.0.1:5000/api/cart/"
	req_cart = requests.delete(url_cart,params={'id_table':session['table'],'id_cart':id_cart})
	session['quantity'] = req_cart.json()['quantity'] if req_cart.json()['quantity'] != None else 0
	return redirect(url_for('cart'))

@app.route('/table',methods=['GET','POST'])
def table():
	if request.method == 'GET':
		url_api = 'http://127.0.0.1:5000/api/table/'
		req_table = requests.get(url_api)
		
		data_table = []

		if req_table.status_code == 200:
			if req_table.json()['status'] == '000':
				for i in req_table.json()['hasil']:
					data = {}
					data['id'] = sToken.dumps(i['id'],salt='id_table')
					data['nama_table'] = i['nama_table']
					data['available'] = i['available']
					data_table.append(data)
			return render_template('blackdashboard/table.html',data_table=data_table)
		return render_template('blackdashboard/table.html',data_table=data_table)
	else:
		nama_table = str(request.form['nama_table'])

		url_api = 'http://127.0.0.1:5000/api/table/'
		json = {'nama_table':nama_table}
		req_table = requests.post(url_api,json=json)
		return redirect(url_for('table'))


if __name__ == '__main__':
	app.run(debug=True,port=5002)