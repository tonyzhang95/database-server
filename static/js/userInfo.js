$(function() {
    $('#btnSave').click(function() {
        console.log($('#user_info_form').serialize());


        $.ajax({
            url: '/processUserInfo?' + $('#user_info_form').serialize(),
            data: $('#user_info_form').serialize(),
            type: 'POST',
            dataType: 'json',
            success: function (result, status, xhr) {
                console.log(result);
                $("#result").html(result.response);
                },
            error: function (xhr, status, error) {
                $("#result").html(xhr.responseText)
                }
        })
    });
});
