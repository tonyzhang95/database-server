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
                $("#retrieve_result").html('<p> Insurance details: ' + result.response + '</p>' + '<button id="btnDelete" class="btn btn-sm btn-primary" type="submit">Delete this record</button>')
                },
            error: function (xhr, status, error) {
                $("#retrieve_result").html('error: ' + xhr.responseText)
                }
        })
    });
});


// $(function() {
//     $('#btnDelete').click(function() {
//         $.ajax({
//             url: '/deleteIns?' + $('#user_info_form').serialize(),
//             data: $('#user_info_form').serialize(),
//             type: 'POST',
//             dataType: 'json',
//             success: function (result, status, xhr) {
//                 console.log(result);
//                 $("#result").html(result.response);
//                 if (result.response == "success") window.location.href='/userHome'
//                 },
//             error: function (xhr, status, error) {
//                 $("#result").html(xhr.responseText)
//                 }
//         })
//     });
// });
