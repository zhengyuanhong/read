from django.apps import AppConfig


class IndexConfig(AppConfig):
    name = 'index'
    verbose_name = "首页管理"

    def ready(self):
        import  index.signals
