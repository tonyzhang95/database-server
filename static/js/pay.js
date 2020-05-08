$(function() {
    $('#btnPay').click(function() {
        $.ajax({
            url: '/processPay',
            data: $('#ins_pay_form').serialize(),
            type: 'POST',
            dataType: 'json',
            success: function (result, status, xhr) {
                console.log(result);
                $("#result").html(result.response);
                },
            error: function (xhr, status, error) {
                $("#result").html("Error: " + xhr.responseText)
                }
        })
    });
});
