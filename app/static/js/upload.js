$(document).on('change', '#upload-button :file', function() {
    var input = $(this),
        numFiles = input.get(0).files ? input.get(0).files.length : 1,
        label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
	if (label.length <45) {
	    if (this.files[0].size < 1e+7) {
		    input.trigger('fileselect', [numFiles, label]);
	    } else {
	    	alert("The size of the file should be less than 10MB");
	    	$("#uploadForm")[0].reset();
	    }    	
    } else {
    	alert("The length of the file's name should be less than 45 characters");
	   	$("#uploadForm")[0].reset();
    }

});

$(document).ready( function() {
    $('#upload-button :file').on('fileselect', function(event, numFiles, label) {
        var input = $(this).parents('#input-group').find(':text');
        input.val('Files selected: ' + label);
    });
});



var thumbnails = document.getElementsByClassName('thumbnail');
var user_id = document.getElementById('user_id');
var bucket_url = document.getElementById('bucket_url');

for(var i=0; i<thumbnails.length; i++) {

	img = thumbnails[i].getElementsByTagName('img')[0];
	modal = thumbnails[i].getElementsByClassName('modal')[0];
	modalImg = modal.getElementsByClassName('modal-content')[0];
	modalImg_resize = modal.getElementsByClassName('modal-content')[1];
	modalImg_enhancement = modal.getElementsByClassName('modal-content')[2];
	modalImg_rotate = modal.getElementsByClassName('modal-content')[3];

	captionText1 = modal.getElementsByClassName("caption")[0];
	captionText2 = modal.getElementsByClassName("caption")[1];
	captionText3 = modal.getElementsByClassName("caption")[2];
	captionText4 = modal.getElementsByClassName("caption")[3];

	img.onclick = function(){
	    modal.style.display = "block";
	 	modalImg.src = bucket_url.value + "/original/" + this.alt;
	 	modalImg_resize.src =  bucket_url.value + "/resize/" + this.alt;
	    modalImg_enhancement.src = bucket_url.value + "/enhancement/" + this.alt;
	    modalImg_rotate.src = bucket_url.value + "/rotate/" + this.alt;
	    

	 	// modalImg_resize.src =  "static/img/upload/"+ user_id.value +"/resize/" + this.alt;
	  //   modalImg_enhancement.src = "static/img/upload/"+ user_id.value +"/enhancement/" + this.alt;
	  //   modalImg_rotate.src = "static/img/upload/"+ user_id.value +"/rotate/" + this.alt;
	    
	    captionText1.innerHTML = "Original Picture";
	   	captionText2.innerHTML = "Resized Picture";
	    captionText3.innerHTML = "Rightshift Picture";
	    captionText4.innerHTML = "Rotated Picture";

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
