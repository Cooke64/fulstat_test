import json

from django.db import models
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from users.models import User



TRACK_CHOICES = [
    (1, '1'),
    (12, '12'),
    (24, '24'),
]


class Product(models.Model):
    code = models.IntegerField('Артикул', unique=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='product', null=True)

    class Meta:
        ordering = ['code']
        verbose_name = 'Карточка товара'
        verbose_name_plural = 'Карточки товаров'

    def __str__(self):
        return f'{self.code}'


class ProductState(models.Model):
    """Модель состояния товара."""
    code = models.ForeignKey(Product, verbose_name='Артикул',
                             on_delete=models.PROTECT)
    product_name = models.CharField('Название продукта', max_length=255)
    current_price = models.PositiveIntegerField('Новая цена')
    old_price = models.PositiveIntegerField('Старая цена', null=True,
                                            blank=True)
    brand = models.CharField('Бренд', max_length=99)
    supplier = models.CharField('Поставщик', max_length=99)

    class Meta:
        ordering = ['code']
        verbose_name = 'Состояние товара'
        verbose_name_plural = 'Состояния товаров'

    def __str__(self):
        return self.product_name


class ProductTracking(models.Model):
    """Модель отслеживания состояния товара."""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    product = models.ForeignKey(
        Product, unique=True, on_delete=models.CASCADE,
        related_name='tracking_card', verbose_name='Товар')
    start_tracking = models.DateTimeField('Время начала отслеживания',
                                          null=False, blank=False)
    end_tracking = models.DateTimeField('Время завершения отслеживания',
                                        null=False, blank=False)
    interval = models.PositiveIntegerField('Интервал отслеживания', null=False,
                                           blank=False, choices=TRACK_CHOICES)
    is_active = models.BooleanField('Статус', default=True)

    class Meta:
        verbose_name = 'Отслеживание товара'
        verbose_name_plural = 'Отслеживания товаров'

    def __str__(self):
        return f'{self.product}'

    def save(self, *args, **kwargs):
        task = PeriodicTask.objects.get(name=self.product.name)
        if not task.exists():
            create_task(self)
        elif task.exists():
            task.update()
            task.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        task = PeriodicTask.objects.get(name=self.product.name)
        task.delete()
        super().delete(*args, **kwargs)


def create_task(data):
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=data.interval, period=IntervalSchedule.SECONDS)
    product = Product.objects.get(pk=data.card.pk)
    PeriodicTask.objects.create(
        name=f'{product.product_name}',
        task='main.tasks.get_state_task',
        interval=schedule,
        start_time=data.start_tracking,
        args=json.dumps([product.code, data.card.pk]),
        expires=data.end_tracking,
    )
