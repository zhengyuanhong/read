layui.use(['layedit', 'form', 'jquery', 'element'], function () {
    var layedit = layui.layedit
    var form = layui.form
    var $ = layui.jquery
    var element = layui.element

    var index = layedit.build('content', {
      tool: [
        'strong' //加粗
        , 'italic' //斜体
        , 'underline' //下划线
        , 'del' //删除线
        , '|' //分割线
        , 'left' //左对齐
        , 'center' //居中对齐
        , 'right' //右对齐
        , 'link' //超链接
        // , 'face' //表情
      ]
    })

    form.verify({
      required: function (value) {
        return layedit.sync(index)
      }
    })

    form.on('submit(add)', function (data) {
      $.ajax({
        url: 'add',
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
  });