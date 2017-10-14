$(document).on('change', '#uploadedfile', function() {
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