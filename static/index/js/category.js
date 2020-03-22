layui.use(['form', 'jquery', 'layer'], function () {
    var form = layui.form
    var $ = layui.jquery
    var layer = layui.layer

    form.on('submit(edit)', function (data) {
        $.ajax({
            url: '/edit-note',
            method: 'post',
            data: data.field,
            dataType: 'JSON',
            success: function (res) {
                if (res.code == 200) {
                    layer.msg((res.msg));
                    setTimeout(function () {
                        window.location.href = "/"
                    }, 500)
                } else {
                    layer.msg(res.msg);
                }
            }
        });
        return false
    })
})