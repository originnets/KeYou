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
$('#forgotpassword').click(function () {
    $("#login_modal").modal('hide');
    $('#forgotpassword_modal').modal('show');
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

$("#send_code").click(function () {
    var email = $("#id_email").val();
    if(email==""){
        $("#error-tip").text('* 邮箱不能为空');
        return false;
    }
    //发送验证码
    $.ajax({
        url: "{% url 'send_verification_code' %}",
        type: "GET",
        data: {
            'email': email,
            'send_for': 'forgot_password_code',
        },
        cache: false,
        success: function (data) {
            if (data['status']=='ERROR'){
                alert(data['status']);
            }
        }
    });
    //把按钮变灰
    $(this).addClass('disabled');
    $(this).attr('disabled', true);
    $(this).text(time + 's');
    var time = 30;
    var interval = setInterval(() => {
        if (time <= 0){
            clearInterval(interval);
            $(this).removeClass('disabled');
            $(this).attr('disabled', false);
            $(this).text('发送验证码');
            return false;
        }
        time --;
        $(this).text(time + 's');
    }, 1000);
})

$("#send_reg_code").click(function () {
    var email = $("#id_email").val();
    if(email==""){
        $("#error-tip").text('* 邮箱不能为空');
        return false;
    }
    //发送验证码
    $.ajax({
        url: "{% url 'send_verification_code' %}",
        type: "GET",
        data: {
            'email': email,
            'send_for': 'register_code',
        },
        cache: false,
        success: function (data) {
            if (data['status']=='ERROR'){
                alert(data['status']);
            }
        }
    });
    //把按钮变灰
    $(this).addClass('disabled');
    $(this).attr('disabled', true);
    $(this).text(time + 's');
    var time = 30;
    var interval = setInterval(() => {
        if (time <= 0){
            clearInterval(interval);
            $(this).removeClass('disabled');
            $(this).attr('disabled', false);
            $(this).text('发送验证码');
            return false;
        }
        time --;
        $(this).text(time + 's');
    }, 1000);
    })