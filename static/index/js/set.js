layui.use(['form', 'jquery', 'upload'], function () {
    var form = layui.form,
      $ = layui.jquery,
      upload = layui.upload

    form.on('submit(setinfo)', function (data) {
      $.ajax({
        url: 'set_info',
        method: 'post',
        data: data.field,
        dataType: 'JSON',
        success: function (res) {
          if (res.code = '200') {
            layer.msg((res.msg));
          } else {
            layer.msg(res.msg);
          }
        }
      });
      return false
    });

    form.on('submit(setpass)', function (data) {
      $.ajax({
        url: 'set_pwd',
        method: 'post',
        data: data.field,
        dataType: 'JSON',
        success: function (res) {
          if (res.code == 200) {
            layer.msg((res.msg));
          } else {
            layer.msg(res.msg);
          }
        }
      });
      return false
    });

    //普通图片上传
    var uploadInst = upload.render({
      elem: '#upload',
      url: 'upload',
      size: 200,
      before: function (obj) {
        //预读本地文件示例，不支持ie8
        obj.preview(function (index, file, result) {
          $('#preview').attr('src', result); //图片链接（base64）
        });
      },
      done: function (res) {
        if (res.code == 200) {
          return layer.msg(res.msg);
        }

        if (res.code == 201) {
          return layer.msg(res.msg);
        }
      },
    });

  });