from qiniu import Auth, put_file, etag,config
from django.conf import settings

def uploadQiniu(pathname,savename):
    #需要填写你的 Access Key 和 Secret Key
    access_key = settings.ACCESS_KEY 
    secret_key = settings.SECRET_KEY
    #构建鉴权对象
    q = Auth(access_key, secret_key)
    #要上传的空间
    bucket_name = 'web'
    #上传后保存的文件名
    key = savename 
    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)
    #要上传文件的本地路径
    localfile = pathname 
    ret, info = put_file(token, key, localfile)
    print(info)
    assert ret['key'] == key
    assert ret['hash'] == etag(localfile)
    return ret