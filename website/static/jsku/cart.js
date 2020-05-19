function changeqty (idcrt) {
	let item = document.getElementById(idcrt)
	// console.log(item.id)
	let confirmation = confirm('Apakah Anda Mau Mengubah Jumlah Pesanan? ')
	if (confirmation == true) {
		if (item.value <= 0) {
			window.location.replace("/delete-cart-item/"+item.id)
		}else {
			req = $.ajax({
				url : '/update-cart-item',
				type : 'POST',
				data : {id_cart : item.id,quantity: item.value}
			})
			req.done(function (data) {
				if (data == 'Berhasil Di Ubah'){
					alert(data)
					location.reload()
				}else {
					window.location.replace("/")
				}

			})
		}
	}
	else {
		location.reload()
	// 	req = $.ajax({
	// 		url : '/getcart/'+item.id,
	// 		type : 'GET',
	// 	})
	// 	req.done(function (data) {
	// 		if (data.status == 'oke'){
	// 			item.value = data.hasil.jumlah_beli
	// 			console.log(data.hasil.jumlah_beli)
	// 		}else {
	// 			window.location.replace("/")
	// 		}
	// 	})
	}
}