from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response,jsonify
import requests,base64, datetime, random, time
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer, BadData

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissecret'

sToken = URLSafeTimedSerializer('thisissecret')
ALLOWED_EXTENSIONS = set(['png','jpeg','jpg'])


# Scheduler
from rq import Queue, cancel_job
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
registry = ScheduledJobRegistry(queue=queue)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def islogin():
	if 'user' in session:
		return True
	else:
		False

def isadmin():
	if islogin():
		if session['id_level'] == 1:
			return True
		return False
	return False

def isCashier():
	if islogin():
		if session['id_level'] == 2:
			return True
		return False
	return False

def isChef():
	if islogin():
		if session['id_level'] == 3:
			return True
		return False
	return False

def isregular():
	if islogin():
		if session['id_level'] == 4:
			return True
		return False
	return False

# Base Prod URL
base_api_url = "http://apirestoku.mastya.my.id"
base_file_url = "http://restokuimage.mastya.my.id"

# Base Dev URL
# base_api_url = "http://127.0.0.1:5000"
# base_file_url = "http://127.0.0.1:5001"

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
			session.pop('job_id')
			# print('expired')
		else:
			# print('running')
			pass
	else:
		pass

@app.route('/')
def index():
	url_produk = f"{base_api_url}/api/product/"
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
	if islogin():
		return redirect(url_for('index'))
	else:
		username = request.form['username']
		password = request.form['password']
		url_user = f"{base_api_url}/api/user/"
		req_user = requests.get(url_user,params={'username':username})
		if req_user.status_code == 200:
			if req_user.json()['status'] == '000':
				if req_user.json()['hasil']['password'] == password:
					session['user'] = req_user.json()['hasil']['id']
					session['id_level'] = req_user.json()['hasil']['id_level']
					if session['id_level'] == 1 or session['id_level'] == 2 or session['id_level'] == 3:
						if 'table' in session:
							session.pop('exp')
							session.pop('table')
							session.pop('quantity')
							session.pop('job_id')
						else:
							pass
						flash('Selamat Datang','success')
						return redirect(url_for('dashboard'))
					else:
						return redirect(url_for('index'))
				else:
					flash("username or password invalid",'error')
					return redirect(url_for('index'))
			return redirect(url_for('index'))
		return redirect(url_for('index'))

@app.route('/logout')
def logout():
	if islogin():
		session.pop('user')
		session.pop('id_level')
		return redirect(url_for('index'))
	else:
		return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
	if isadmin() or isCashier() or isChef():
		return render_template("blackdashboard/dashboard.html")
	else:
		return redirect(url_for('index'))

@app.route('/level_user',methods=['GET','POST'])
def level_user():
	if isadmin():
		if request.method == 'GET':
			url_level_user = f"{base_api_url}/api/level_user/"
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
			url_level_user = f"{base_api_url}/api/level_user/"
			req_level_user = requests.post(url_level_user,json=json)
			if req_level_user.status_code == 200:
				flash('Level User Berhasil ditambahkan','success')
				return redirect(url_for('level_user'))
			else:
				flash('Level User Gagal ditambahkan','error')
				return redirect(url_for('level_user'))
	else:
		return redirect(url_for('index'))

@app.route('/edit_level_user/<id_level>',methods=['POST'])
def edit_level_user(id_level):
	if isadmin():
		id_level = sToken.loads(id_level,salt='id_level_user')
		d_nama_level = str(request.form['nama_level'])
		
		json = {
			'id_level':id_level,
			'nama_level':d_nama_level
		}
		url_level_user = f"{base_api_url}/api/level_user/"
		req_level_user = requests.put(url_level_user,json=json)
		if req_level_user.status_code == 200:
			flash('Level User Berhasil Diubah','success')
			return redirect(url_for('level_user'))
		else:
			flash('Level User Gagal Diubah','error')
			return redirect(url_for('level_user'))
	else:
		return redirect(url_for('index'))

@app.route('/delete_level_user/<id_level>')
def delete_level_user(id_level):
	if isadmin():
		id_level = sToken.loads(id_level,salt='id_level_user')
		params = {
			'id_level':id_level,
		}
		url_level_user = f"{base_api_url}/api/level_user/"
		req_level_user = requests.delete(url_level_user,params=params)
		if req_level_user.status_code == 200:
			flash('Level User Berhasil Dihapus','success')
			return redirect(url_for('level_user'))
		else:
			flash('Level User Gagal Dihapus','success')
			return redirect(url_for('level_user'))	
	return redirect(url_for('index'))

@app.route('/user',methods=['GET',"POST"])
def user():
	if isadmin():
		if request.method == 'GET':
			url_user = f"{base_api_url}/api/user/"
			req_user = requests.get(url_user)
			url_level_user = f"{base_api_url}/api/level_user/"
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
			url_user = f"{base_api_url}/api/user/"
			req_user = requests.post(url_user,json=json)
			flash('User Berhasil ditambahkan','success')
			return redirect(request.url)
	else:
		return redirect(url_for('index'))

@app.route('/edit-user/<id_user>',methods=['POST'])
def edit_user(id_user):
	if isadmin():
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
		url_user = f"{base_api_url}/api/user/"
		req_user = requests.put(url_user,json=json)
		flash('User Berhasil Diubah','success')
		return redirect(url_for('user'))
	else:
		return redirect(url_for('index'))

@app.route('/remove-user/<id_user>')
def remove_user(id_user):
	if isadmin():
		id_user = sToken.loads(id_user,salt='id_user')
		url_user = f"{base_api_url}/api/user/"
		req_user = requests.delete(url_user,params={'id_user':id_user})
		flash('User Berhasil Dihapus','success')
		return redirect(url_for('user'))
	else:
		return redirect(url_for('index'))

@app.route('/product_category',methods=['GET','POST'])
def product_category():
	if isadmin():
		if request.method == 'GET':
			url_jenis_produk = f"{base_api_url}/api/jenis_product/"
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
			url_jenis_produk = f"{base_api_url}/api/jenis_product/"
			req_jenis_produk = requests.post(url_jenis_produk,json=json)
			if req_jenis_produk.status_code == 200:
				flash('Kategori Produk Berhasil ditambahkan','success')
				return redirect(url_for('product_category'))
			else:
				flash('Kategori Produk Gagal ditambahkan','error')
				return redirect(url_for('product_category'))
	else:
		return redirect(url_for('index'))

@app.route('/edit_product_category/<id_jenis_product>',methods=['POST'])
def edit_product_category(id_jenis_product):
	if isadmin():
		id_jenis_product = sToken.loads(id_jenis_product,salt='id_jenis_product')
		d_nama_kategori = request.form['category_name']
		json = {
			'id_jenis_product':id_jenis_product,
			'nama_jenis_product':d_nama_kategori
		}
		url_jenis_produk = f"{base_api_url}/api/jenis_product/"
		req_jenis_produk = requests.put(url_jenis_produk,json=json)
		if req_jenis_produk.status_code == 200:
			flash('Kategori Produk Berhasil Diubah','success')
			return redirect(url_for('product_category'))
		else:
			flash('Kategori Produk Berhasil ditambahkan','error')
			return redirect(url_for('product_category'))
	else:
		return redirect(url_for('index'))

@app.route('/delete_product_category/<id_jenis_product>')
def delete_product_category(id_jenis_product):
	if isadmin():
		id_jenis_product = sToken.loads(id_jenis_product,salt='id_jenis_product')
		params = {
			'id_jenis_product':id_jenis_product,
		}
		url_jenis_produk = f"{base_api_url}/api/jenis_product/"
		req_jenis_produk = requests.delete(url_jenis_produk,params=params)
		if req_jenis_produk.status_code == 200:
			flash('Kategori Produk Berhasil Dihapus','success')
			return redirect(url_for('product_category'))
		else:
			flash('Kategori Produk Gagal ditambahkan','error')
			return redirect(url_for('product_category'))
	else:
		return redirect(url_for('index'))


@app.route('/product',methods=['POST',"GET"])
def product():
	if isadmin():
		if request.method == "GET":
			url_produk = f"{base_api_url}/api/product/"
			url_jenis_produk = f"{base_api_url}/api/jenis_product/"
			
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
				photo_link = f"{base_file_url}/api/restokuimage/"
				req_photo = requests.post(photo_link,json=json)
				result = req_photo.json()
				if result['status'] == 'error':
					return redirect(request.url)
				elif result['status'] == 'success':
					url = f"{base_api_url}/api/product/"
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
							flash('Produk Berhasil ditambahkan','success')
							return redirect(url_for('product'))
						else:
							flash("Opps Something Wrong in delete photo when product name is already exists",'error')
							return redirect(url_for('product'))
					else:
						flash("Opps Something Wrong",'error')
						return redirect(url_for('product'))
				else:
					flash("Opps Something Wrong",'error')
					return redirect(url_for('product'))
	else:
		return redirect(url_for('index'))

@app.route('/editproduct/<idproduct>/<filenamephoto>', methods=['POST'])
def editproduct(idproduct,filenamephoto):
	if isadmin():
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
			url = f"{base_api_url}/api/product/"
			json = {
				"id_product":id_produk,
				"nama_produk": nama_produk,
				"harga_produk": int(harga_produk),
				"id_jenis_product": id_jenis_product,
				"foto_produk": old_filename,
				'description': description
			}
			req = requests.put(url,json=json)
			flash("Produk Berhasil Diubah",'success')
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
			photo_link = f"{base_file_url}/api/restokuimage/"
			req_photo = requests.put(photo_link,json=json)
			result = req_photo.json()
			if result['status'] == 'error':
				return redirect(request.url)
			elif result['status'] == 'success':
				url = f"{base_api_url}/api/product/"
				json = {
					"id_product":id_produk,
					"nama_produk": nama_produk,
					"harga_produk": harga_produk,
					"id_jenis_product": id_jenis_product,
					"foto_produk": result['link'],
					'description': description
				}
				req = requests.put(url,json=json)
				flash("Produk Berhasil Diubah",'success')
				return redirect(url_for('product'))
			else:
				flash("Produk Gagal Diubah",'error')
				return redirect(url_for('product'))
	else:
		return redirect(url_for('index'))

@app.route("/deleteproduct/<idproduct>/<filenamephoto>")
def deleteproduct(idproduct,filenamephoto):
	id_produk = sToken.loads(idproduct,salt='id_produk')
	old_filename = sToken.loads(filenamephoto,salt='foto_produk')


	url_api = f"{base_api_url}/api/product/"
	url_file = f"{base_file_url}/api/restokuimage/"
	json_file = {"old_filename":old_filename}
	req_file = requests.delete(url_file,json=json_file)
	if req_file.status_code == 200:
		if req_file.json()['status'] == 'success':
			params = {"id_product":id_produk}
			req_api = requests.delete(url_api,params=params)
			flash("Produk Berhasil Dihapus",'success')
			return redirect(url_for('product'))
		else:
			flash("Produk Gagal Diubah",'error')
			return redirect(url_for('product'))
	else:
		flash("Opps Something Wrong",'error')
		return redirect(url_for('product'))

@app.route('/table',methods=['GET','POST'])
def table():
	if isadmin():
		if request.method == 'GET':
			url_api = f"{base_api_url}/api/table/"
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

			url_api = f"{base_api_url}/api/table/"
			json = {'nama_table':nama_table}
			req_table = requests.post(url_api,json=json)
			if req_table.json()['status'] == '000':
				flash("Meja Berhasil ditambahkan",'success')
				return redirect(url_for('table'))
			else:
				flash("Meja Gagal ditambahkan",'error')
				return redirect(url_for('table'))
	else:
		return redirect(url_for('index'))

@app.route('/update-table/<id_table>',methods=['POST'])
def update_table(id_table):
	if isadmin():
		id_table = sToken.loads(id_table,salt='id_table')
		nama_table = str(request.form['nama_table'])

		url_api = f"{base_api_url}/api/table/"
		json = {'id_table':id_table,'nama_table':nama_table}
		req_table = requests.put(url_api,json=json)
		if req_table.json()['status'] == '000':
			flash("Meja Berhasil Diubah",'success')
			return redirect(url_for('table'))
		else:
			flash("Meja Gagal Diubah",'error')
			return redirect(url_for('table'))
	else:
		return redirect(url_for('index'))

@app.route('/remove-table/<id_table>')
def remove_table(id_table):
	if isadmin():
		id_table = sToken.loads(id_table,salt='id_table')
		url_api = f"{base_api_url}/api/table/"
		req_table = requests.delete(url_api,params={'id_table':id_table})
		flash("Meja Berhasil Dihapus",'success')
		return redirect(url_for('table'))
	else:
		return redirect(url_for('index'))

@app.route('/orders')
def orders():
	if isadmin() or isCashier() or isChef() :
		url_order = f"{base_api_url}/api/orders/"
		req_order = requests.get(url_order)

		orders = []
		if req_order.status_code == 200:
			if req_order.json()['status'] == '000':
				# select all trx_id where payment = False and trx_id = args[trx_id]
				all_trx_id  = req_order.json()['hasil']
				for i in all_trx_id:
					data_trx = {}
					item_trx = []
					# select trx
					trx =  i['item']
					for j in trx:
						data = {}
						data['id'] = sToken.dumps(j['id'], salt='id_checkout') 
						data['id_product'] = sToken.dumps(j['id_product'],salt='id_product')
						data['nama_produk'] = j['nama_produk']
						data['foto_produk'] = j['foto_produk']
						data['quantity'] = j['quantity']
						item_trx.append(data)
					data_trx['status'] = i['status']
					data_trx['item'] = item_trx
					data_trx['payment'] = i['payment']
					data_trx['qty_all_item'] = i['qty_all_item']
					data_trx['grand_price'] = i['grand_price']
					data_trx['trx_id'] = i['trx_id']
					data_trx['waktu_trx'] = i['waktu_trx']
					data_trx['table'] = i['table']
					orders.append(data_trx)
				# print(orders)
				# return jsonify({'hasil':orders})
				return render_template('blackdashboard/orders.html',data_orders=orders)
			else:
				return 'Opps {}'.format(req_checkout.json()['hasil'])
		else:
			return 'Opps Internal Server Error'
	else:
		return redirect(url_for('index'))

@app.route('/orders/<trx_id>/<acceptorrefuse>')
def payment(trx_id,acceptorrefuse):
	if isadmin() or isCashier() or isChef() :
		if acceptorrefuse == 'accept':
			if isadmin() or isCashier():
				url_order = f"{base_api_url}/api/orders/"
				req_order = requests.post(url_order,params={'trx_id':trx_id})
				if req_order.status_code == 200:
					req_order = req_order.json()
					if req_order['status'] == '000':
						flash("Pesanan dimasak","success")
						return redirect(url_for('orders'))
					flash("Opps Something Wrong!","error")
					return redirect(url_for('orders'))
				flash("Something Wrong","error")
				return redirect(url_for('orders'))
			return redirect(url_for('orders'))
		elif acceptorrefuse == 'refuse':
			if isadmin() or isCashier():
				url_order = f"{base_api_url}/api/orders/"
				req_order = requests.delete(url_order,params={'trx_id':trx_id})
				if req_order.status_code == 200:
					req_order = req_order.json()
					if req_order['status'] == '000':
						flash("Pesanan ditolak","success")
						return redirect(url_for('orders'))
					flash("Opps Something Wrong","error")
					return redirect(url_for('orders'))
				flash("Something Wrong","error")
				return redirect(url_for('orders'))
			return redirect(url_for('orders'))
		elif acceptorrefuse == 'finish':
			if isadmin() or isChef():
				url_order = f"{base_api_url}/api/orders/"
				req_order = requests.put(url_order,params={'trx_id':trx_id})
				if req_order.status_code == 200:
					req_order = req_order.json()
					if req_order['status'] == '000':
						flash("Pesanan siap disajikan","success")
						return redirect(url_for('orders'))
					flash("Opps Something Wrong!","error")
					return redirect(url_for('orders'))
				flash("Something Wrong","error")
				return redirect(url_for('orders'))
			return redirect(url_for('orders'))
		else:
			return redirect(url_for('index'))
	else:
		return redirect(url_for('index'))


# Customers Area
@app.route('/scan-table')
def scan_table():
	if 'table' in session or isadmin() or isCashier() or isChef():
		return redirect(url_for('index'))
	return render_template('scan_table.html')

@app.route('/scan-table/<id_table>')
def scan_table_id(id_table):
	if 'table' in session or isadmin() or isCashier() or isChef():
		return redirect(url_for('index'))
	dec_id_table = sToken.loads(id_table,salt='id_table')
	session['table'] = dec_id_table
	session['quantity'] = 0

	job = queue.enqueue_in(datetime.timedelta(minutes=5),jadwal_job.background_task,dec_id_table)
	session['job_id'] = job.id

	flash('Silahkan Order Menu','success')
	resp = make_response(redirect(url_for('index')))
	expire_date = datetime.datetime.now()
	expire_date = expire_date + datetime.timedelta(minutes=5)
	resp.set_cookie('table',id_table,expires=expire_date)
	resp.set_cookie('exp',"{}".format(expire_date.timestamp()),expires=expire_date)
	session['exp'] = expire_date.timestamp()
	return resp

@app.route('/cart')
def cart():
	if isadmin() or isCashier() or isChef():
		return redirect(url_for('index'))
	if 'table' in session:
		url_cart = f"{base_api_url}/api/cart/"
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
	if isadmin() or isCashier() or isChef():
		return redirect(url_for('index'))
	if 'table' in session:
		id_produk = sToken.loads(id_produk,salt='id_produk')
		jumlah = 1
		meja = session['table']
		
		json = {
			'id_product':id_produk,
			'id_table':meja,
			'quantity':jumlah,
		}
		url_cart = f"{base_api_url}/api/cart/"
		req_cart = requests.post(url_cart,json=json)
		session['quantity'] = req_cart.json()['quantity'] if req_cart.json()['quantity'] != None else 0
		flash('Berhasil ditambahkan kedalam cart','success')
		return redirect(url_for('index'))
	flash('Gagal ditambahkan kedalam cart','error')
	return redirect(url_for('index'))

@app.route('/update-cart-item',methods=['POST'])
def update_cart_item():
	if isadmin() or isCashier() or isChef():
		return redirect(url_for('index'))
	if 'table' in session:
		id_cart = request.form['id_cart']
		id_cart = sToken.loads(id_cart,salt='id_cart')
		qty = request.form['quantity']

		# Get Cart Item Data
		url_cart = f"{base_api_url}/api/cart/"
		req_cart = requests.get(url=url_cart,params={'id_table':session['table'],'id_cart':id_cart})
		
		if req_cart.status_code == 200 and req_cart.json()['status'] == "000":
			# Updating Cart
			json = {
				'id_cart':id_cart,
				'id_product':req_cart.json()['hasil']['id_product'],
				'id_table':session['table'],
				'quantity':qty
			}
			url_cart = f"{base_api_url}/api/cart/"
			req_cart = requests.put(url_cart,json=json)
			session['quantity'] = req_cart.json()['quantity'] if req_cart.json()['quantity'] != None else 0
			return 'Berhasil Di Ubah'
		else:
			return 'gagal'
	else:
		return 'gagal'

@app.route('/delete-cart-item/<id_cart>')
def delete_cart_item(id_cart):
	if isadmin() or isCashier() or isChef():
		return redirect(url_for('index'))
	if 'table' in session:
		id_cart = sToken.loads(id_cart,salt='id_cart',max_age=300)
		url_cart = f"{base_api_url}/api/cart/"
		req_cart = requests.delete(url_cart,params={'id_table':session['table'],'id_cart':id_cart})
		session['quantity'] = req_cart.json()['quantity'] if req_cart.json()['quantity'] != None else 0
		flash('Item Berhasil dihapus','success')
		return redirect(url_for('cart'))
	return redirect(url_for('index'))

@app.route('/checkout')
def checkout():
	if 'table' in session:
		url_checkout = f"{base_api_url}/api/checkout/"
		if islogin():
			if isadmin() or isCashier() or isChef():
				return redirect(url_for('index'))
			else:
				params = {'id_table':int(session['table']),'id_user':int(session['user'])}
		else:
			params = {'id_table':int(session['table'])}
		req_checkout = requests.post(url_checkout,params=params)
		if req_checkout.status_code == 200:
			if req_checkout.json()['status'] == '000':
				registry.remove(session['job_id'],delete_job=True)
				session.pop('exp')
				session.pop('table')
				session.pop('quantity')
				session.pop('job_id')
				data_orders = req_checkout.json()['orders']
				return render_template('invoice.html',data_orders=data_orders)
			else:
				flash('checkout failed. no item found in cart','error')
				return redirect(url_for('cart'))
		else:
			flash('Something Wrong')
			return redirect(url_for('cart'))				
	else:
		return redirect(url_for('index'))

@app.route('/profile')
def profile():
	if isregular():
		id_user = session['user']
		url_order = f"{base_api_url}/api/orders/"
		req_order = requests.get(url_order,params={'id_user':id_user})
		orders = []
		url_user = f"{base_api_url}/api/user/"
		req_user = requests.get(url_user,params={'id_user':id_user})

		nama_user = req_user.json()['hasil']['nama_user']
		point = req_user.json()['hasil']['point']
		if req_order.status_code == 200:
			if req_order.json()['status'] == '000':
				all_trx_id  = req_order.json()['hasil']
				for i in all_trx_id:
					data_trx = {}
					item_trx = []
					# select trx
					trx =  i['item']
					for j in trx:
						data = {}
						data['id'] = sToken.dumps(j['id'], salt='id_checkout') 
						data['id_product'] = sToken.dumps(j['id_product'],salt='id_product')
						data['nama_produk'] = j['nama_produk']
						data['foto_produk'] = j['foto_produk']
						data['quantity'] = j['quantity']
						item_trx.append(data)
					data_trx['status'] = i['status']
					data_trx['item'] = item_trx
					data_trx['payment'] = i['payment']
					data_trx['qty_all_item'] = i['qty_all_item']
					data_trx['grand_price'] = i['grand_price']
					data_trx['trx_id'] = i['trx_id']
					data_trx['waktu_trx'] = i['waktu_trx']
					data_trx['table'] = i['table']
					orders.append(data_trx)
				return render_template('blackdashboard/profile_user.html', orders=orders, nama_user=nama_user, point=point)
			return render_template('blackdashboard/profile_user.html', orders=orders, nama_user=nama_user, point=point)
		return render_template('blackdashboard/profile_user.html', orders=orders, nama_user=nama_user, point=point)
	else:
		return redirect(url_for('index'))

if __name__ == '__main__':
	app.run(debug=True,port=5002)