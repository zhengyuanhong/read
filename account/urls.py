from django.urls import path
from account.views import accountUserArticle,getMsg,delMsg, \
    accountUserComment,accountUser,accountLogin,verifEmail, \
    emailTip,accountSet,setPassword,accountLoginOut,accountRegister, \
    setInfo,uploadImage,verif,getMessage,sendResetPassword,resetPassword

urlpatterns = [
    path('u/<int:userId>',accountUser,name='accountUser'),
    path('login',accountLogin,name='accountLogin'),
    path('register',accountRegister,name='accountRegister'),
    path('set',accountSet,name='accountSet'),
    path('set_info',setInfo,name='setInfo'),
    path('set_pwd',setPassword,name='setPassword'),
    path('logout',accountLoginOut,name='accountLoginOut'),
    path('upload',uploadImage,name='uploadImage'),
    path('verif',verif,name='verif'),
    path('message',getMessage,name='getMessage'),
    path('msg',getMsg),
    path('del_msg',delMsg),
    path('email_tip',emailTip,name='emailTip'),
    path('verif_email',verifEmail,name='verifEmail'),
    path('u/article',accountUserArticle,name='accountUserArticle'),
    path('u/comment',accountUserComment,name='accountUserComment'),
    path('forget',sendResetPassword,name='sendResetPassword'),
    path('reset_password',resetPassword,name='resetPassword'),
]