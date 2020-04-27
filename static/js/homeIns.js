$(function() {
    $('#btnHomeInsSubmit').click(function() {
        $.ajax({
            url: '/processHomeIns?' + $('#home_ins_form').serialize(),
            data: $('#home_ins_form').serialize(),
            type: 'POST',
            dataType: 'json',
            success: function (result, status, xhr) {
                console.log(result);
                $("#result").html(result.response);
                // if (result.response == "success") window.location.href='/userHome'
                },
            error: function (xhr, status, error) {
                $("#result").html(xhr.responseText)
                }
        })
    });
});
