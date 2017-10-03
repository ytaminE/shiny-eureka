$(document).on('change', '#upload-button :file', function() {
    var input = $(this),
        numFiles = input.get(0).files ? input.get(0).files.length : 1,
        label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
    input.trigger('fileselect', [numFiles, label]);
});

$(document).ready( function() {
    $('#upload-button :file').on('fileselect', function(event, numFiles, label) {
        var input = $(this).parents('#input-group').find(':text');
        input.val('Files selected: ' + label);
    });
});


var thumbnails = document.getElementsByClassName('thumbnail');
var user_id = document.getElementById('user_id');

for(var i=0; i<thumbnails.length; i++) {

	img = thumbnails[i].getElementsByTagName('img')[0];
	modal = thumbnails[i].getElementsByClassName('modal')[0];
	modalImg = modal.getElementsByClassName('modal-content')[0];
	modalImg_resize = modal.getElementsByClassName('modal-content')[1];
	modalImg_enhancement = modal.getElementsByClassName('modal-content')[2];
	modalImg_rotate = modal.getElementsByClassName('modal-content')[3];

	captionText = modal.getElementsByClassName("caption")[0];
	img.onclick = function(){
	    modal.style.display = "block";
	 	modalImg.src = this.src;
	 	modalImg_resize.src =  "static/img/upload/"+ user_id.value +"/resize/" + this.alt;
	    modalImg_enhancement.src = "static/img/upload/"+ user_id.value +"/enhancement/" + this.alt;
	    modalImg_rotate.src = "static/img/upload/"+ user_id.value +"/rotate/" + this.alt;
	    captionText.innerHTML = this.alt;
	}

	// Get the <span> element that closes the modal
	var span = modal.getElementsByClassName("close")[0];

	// When the user clicks on <span> (x), close the modal
	span.onclick = function() { 
	  modal.style.display = "none";
	}
	
	$(window).keydown(function(e) {
	  switch (e.keyCode) {
	    case 27:
	      span.click();  // esc
	  }
	});

}
