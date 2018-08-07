$('#login').click(function () {
    $("#login_modal").modal('show');
})
$('#register').click(function () {
    $("#reg_modal").modal('show');
})
$('#new_login').click(function () {
   $('#login_modal').modal('show');
})
$('#new_register').click(function () {
    $('#reg_modal').modal('show');
})
$("#login_medal_form").submit(function () {
    $.ajax({
       url: "/login",
       type: "POST",
       data: $(this).serialize(),
       cache: false,
       success: function (data) {
            window.location.reload();
       } ,
       error: function (xhr) {
            $('#login_medal_form').text('用户名或密码错误')
       },
    });
    return false;
})