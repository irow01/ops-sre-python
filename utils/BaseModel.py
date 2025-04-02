from django.db import models


class BaseModel(models.Model):
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    is_delete = models.BooleanField(default=False, verbose_name='是否删除')

    class Meta:
        abstract = True
