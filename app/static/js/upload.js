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