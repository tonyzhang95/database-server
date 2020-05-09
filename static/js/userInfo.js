$(function() {
    $('#btnSave').click(function() {
        $.ajax({
            url: '/processUserInfo?' + $('#user_info_form').serialize(),
            data: $('#user_info_form').serialize(),
            type: 'POST',
            dataType: 'json',
            success: function (result, status, xhr) {
                console.log(result);
                $("#result").html(result.response);
                if (result.response == "success") window.location.href='/userHome'
                },
            error: function (xhr, status, error) {
                $("#result").html(xhr.responseText)
                }
        })
    });
});



$(function() {
    $('#btnRetrieve').click(function() {
        $.ajax({
            url: '/retrieveIns?' + $('#ins_retrieve_form').serialize(),
            data: $('#ins_retrieve_form').serialize(),
            type: 'POST',
            dataType: 'json',
            success: function (result, status, xhr) {
                console.log(result);
                $("#retrieve_result").html('<p> Insurance details: ' + result.response + '</p>')
                },
            error: function (xhr, status, error) {
                $("#retrieve_result").html('error: ' + xhr.responseText)
                }
        })
    });
});


$(function() {
    $('#btnDelete').click(function() {
        $.ajax({
            url: '/deleteIns?' + $('#ins_delete_form').serialize(),
            data: $('#ins_delete_form').serialize(),
            type: 'POST',
            dataType: 'json',
            success: function (result, status, xhr) {
                console.log(result);
                $("#delete_result").html(result.response);
                },
            error: function (xhr, status, error) {
                $("#result").html(xhr.responseText)
                }
        })
    });
});


$(function() {
    $('#btnEditInsSubmit').click(function() {
        $.ajax({
            url: '/processEdit?' + $('#edit_ins_form').serialize(),
            data: $('#edit_ins_form').serialize(),
            type: 'POST',
            dataType: 'json',
            success: function (result, status, xhr) {
                console.log(result);
                $("#result").html(result.response)
                },
            error: function (xhr, status, error) {
                $("#result").html(xhr.responseText)
                }
        })
    });
});
