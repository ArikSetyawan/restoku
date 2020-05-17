# import requests,time,random
# def background_task():
# 	nama_table = str(random.randint(11,99))
# 	url_api = 'http://127.0.0.1:5000/api/table/'
# 	json = {'nama_table':nama_table}
# 	req_table = requests.post(url_api,json=json)
# 	print("Task Complete")
# 	return "background_task Complete"


import requests
from flask import make_response, session
def background_task(id_table):
	url_cart = "http://127.0.0.1:5000/api/cart/"
	req_cart = requests.delete(url_cart,params={'id_table':id_table})
	print("task Complete")
	return "oke"