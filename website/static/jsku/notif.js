function showNotificationError(from, align, pesan) {
  type = ['primary', 'info', 'success', 'warning', 'danger'];
  color = Math.floor((Math.random() * 4) + 1);

  $.notify({
    message: pesan

  }, {
    type: 'danger',
    timer: 8000,
    placement: {
      from: from,
      align: align
    }
  });
}
function showNotificationSuccess(from, align, pesan) {
  type = ['primary', 'info', 'success', 'warning', 'danger'];
  color = Math.floor((Math.random() * 4) + 1);

  $.notify({
    message: pesan

  }, {
    type: 'success',
    timer: 8000,
    placement: {
      from: from,
      align: align
    }
  });
}
$(document).ready(function(){
  let notif = $('meta[name=notif]');
  if($('meta[name=notif]').length){
    if (notif.attr("category") === 'error') {
      showNotificationError('top','right',notif.attr("content"))
    }
    else if (notif.attr("category") === 'success') {
      showNotificationSuccess('top','right',notif.attr("content"))
    }
  }
})