from flask import Flask, request, render_template, redirect, url_for
import requests,base64
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer, BadData

app = Flask(__name__)
sToken = URLSafeTimedSerializer('thisissecret')
ALLOWED_EXTENSIONS = set(['png','jpeg','jpg'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
	return render_template('menu.html')

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
				data_produk.append(data)

			data_jenis_produk = []
			for i in req_jenis_produk.json()['hasil']:
				data = {}
				data['id'] = sToken.dumps(i['id'],salt='id_jenis_product')
				data['nama_jenis_product'] = i['nama_jenis_product']
				data_jenis_produk.append(data)

			return render_template('product.html',data_produk=data_produk,data_jenis_produk=data_jenis_produk)
		else:
			return render_template('product.html')
	else:
		nama_produk = request.form['nama_produk']
		id_jenis_product = sToken.loads(request.form['jenis_product'],salt='id_jenis_product')
		harga_produk = request.form['harga_produk']

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
					"foto_produk": result['link']
				}
				req = requests.post(url,json=json)

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
			"foto_produk": old_filename
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
				"foto_produk": result['link']
			}
			req = requests.put(url,json=json)

			return redirect(url_for('product'))
		else:
			return redirect(url_for('product'))


if __name__ == '__main__':
	app.run(debug=True,port=5002)