$('.delete_item').on('click',function(e){
  e.preventDefault();
  Swal.fire({
    title: 'Are you sure?',
    text: "You won't be able to revert this!",
    type: 'warning',
    showCancelButton: true,
    customClass: {
      confirmButton: 'btn btn-success',
      cancelButton: 'btn btn-danger'
    },
    buttonsStyling: false,
    confirmButtonText: 'Yes, delete it!'
  }).then((result) => {
    if (result.value) {
      Swal.fire({
        title : 'Deleted!',
        text : 'This item has been deleted.',
        type :'success',
        onClose: () => {
          document.location.href = $(this).attr("href")
        }
      })
    }
  })
})

$('.confirm_item').on('click',function(e){
  e.preventDefault();
  Swal.fire({
    title: 'Are you sure?',
    text: "You won't be able to revert this!",
    type: 'warning',
    showCancelButton: true,
    customClass: {
      confirmButton: 'btn btn-success',
      cancelButton: 'btn btn-danger'
    },
    buttonsStyling: false,
    confirmButtonText: 'Yes!'
  }).then((result) => {
    if (result.value) {
      Swal.fire({
        title : 'Success!',
        text : 'This item has been executed.',
        type :'success',
        onClose: () => {
          document.location.href = $(this).attr("href")
        }
      })
    }
  })
})