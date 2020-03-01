from qiniu import Auth, put_file, etag,config

def uploadQiniu(pathname,savename):
    #需要填写你的 Access Key 和 Secret Key
    access_key = 'jmiM2zVKT9DmRh2hCI4MYseYGYziHwRPab3OordF'
    secret_key = 'KFk_xsW02aBZTC_c-kNfhCi2pRTo3dNG-jne3KDX'
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