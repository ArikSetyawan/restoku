function error_notif(Pesan) {
	let timerInterval
	Swal.fire({
		icon: 'error',
		title: 'Oops..',
		text: Pesan,
		timer: 2000,
		showConfirmButton: false,
		onClose: () => {
			clearInterval(timerInterval)
		}
	})
}
function success_notif(Pesan) {
	let timerInterval
	Swal.fire({
		icon: 'success',
		title: 'success',
		text: Pesan,
		timer: 2000,
		showConfirmButton: false,
		onClose: () => {
			clearInterval(timerInterval)
		}
	})
}
$(document).ready(function(){
  let notif = $('meta[name=notif]');
  if($('meta[name=notif]').length){
    if (notif.attr("category") === 'error') {
      error_notif(notif.attr("content"))
    }
    else if (notif.attr("category") === 'success') {
      success_notif(notif.attr("content"))
    }
  }
})