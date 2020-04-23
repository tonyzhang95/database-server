$(function() {
    $('#btnSignUp').click(function() {
        $.ajax({
            url: '/signUp',
            data: $('form').serialize(),
            type: 'POST',
            dataType: 'json',
            success: function (result, status, xhr) {
                console.log(result);
                $("#result").html(result.message)
                },
            error: function (xhr, status, error) {
                $("#result").html("Error: please fill all fields. ")
                }
        })
    });
});
