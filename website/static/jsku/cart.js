function changeqty (idcrt) {
	let item = document.getElementById(idcrt)
	// console.log(item.id)
	Swal.fire({
		title: 'Are you sure?',
		text: "You won't be able to revert this!",
		icon: 'warning',
		showCancelButton: true,
		cancelButtonColor: '#d33',
		confirmButtonColor: '#34eb40',
		confirmButtonText: 'Yes, edit it!'
	}).then((result) => {
	    if (result.value) {
			Swal.fire({
		        title : 'Edited!',
		        text : 'Your item has been edited.',
		        type :'success',
		        onClose: () => {
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
								location.reload()
							}else {
								window.location.replace("/")
							}

						})
					}
		        }
		    })
		}else{
			location.reload()
		}
	})
}