$(function() {
    $('#btnSave').click(function() {
        $.ajax({
            url: '/processUserInfo',
            data: $('form').serialize(),
            type: 'POST',
            dataType: 'json',
            success: function (result, status, xhr) {
                console.log(result);

                },
            error: function (xhr, status, error) {
                $("#result").html("Error: " + xhr.responseText)
                }
        })
    });
});
