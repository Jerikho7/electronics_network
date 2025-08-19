from __future__ import annotations

from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models

from users.models import User


class NetworkNode(models.Model):
    """
    Узел сети: завод / розничная сеть / ИП.
    Уровень НЕ хранится, вычисляется из цепочки поставщиков:
      0 — нет supplier (завод),
      1 — supplier уровня 0,
      2 — supplier уровня 1.
    """
    LEVEL_NAMES = {
        0: "Завод",
        1: "Розничная сеть",
        2: "Индивидуальный предприниматель",
    }

    name = models.CharField(
        "Название",
        max_length=255,
        validators=[MinLengthValidator(2)],
    )

    email = models.EmailField("Email")
    country = models.CharField("Страна", max_length=100)
    city = models.CharField("Город", max_length=100)
    street = models.CharField("Улица", max_length=120)
    house_number = models.CharField("Номер дома", max_length=30)

    supplier = models.ForeignKey(
        "self",
        verbose_name="Поставщик",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="clients",
        help_text="Единственный поставщик данного звена",
    )

    employees = models.ManyToManyField(User, related_name="network_nodes", verbose_name="Сотрудники")

    debt = models.DecimalField(
        "Задолженность перед поставщиком",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
    )

    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Элемент сети"
        verbose_name_plural = "Элементы сети"
        ordering = ("country", "city", "name")

    def __str__(self) -> str:
        return f"{self.name} ({self.city})"

    @property
    def level_name(self) -> str:
        """Читаемое название уровня (завод, розница, ИП)."""
        return self.LEVEL_NAMES.get(self.level, f"Уровень {self.level}")

    @property
    def level(self) -> int:
        """
        Вычисление уровня по цепочке поставщиков.
        """
        depth = 0
        node = self
        while node.supplier is not None and depth <= 10:
            depth += 1
            node = node.supplier
        return depth

    def clean(self):
        if self.pk:
            node = self.supplier
            while node is not None:
                if node.pk == self.pk:
                    raise ValidationError({"supplier": "Цикл в цепочке поставщиков запрещён."})
                node = node.supplier

        depth = 0
        node = self.supplier
        while node is not None:
            depth += 1
            if depth > 2:
                raise ValidationError({"supplier": "Глубина иерархии не может превышать 3 уровня (0..2)."})
            node = node.supplier

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Product(models.Model):
    """
    Продукт принадлежит конкретному узлу сети.
    """

    owner = models.ForeignKey(
        NetworkNode,
        verbose_name="Владелец",
        on_delete=models.CASCADE,
        related_name="products",
    )
    title = models.CharField("Название", max_length=255)
    model = models.CharField("Модель", max_length=120)
    release_date = models.DateField("Дата выхода на рынок")

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ("-release_date", "title")

    def __str__(self) -> str:
        return f"{self.title} {self.model}"
