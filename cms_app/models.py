from django.db import models
from django.contrib.auth.models import User

__project_by__ = "RajeshKumar"


class Tables(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Table - {self.name}"


class Dishes(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    price = models.IntegerField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Dish - {self.name}"


class OrderList(models.Model):
    attended_by = models.ForeignKey(User, on_delete=models.CASCADE)
    table = models.ForeignKey(Tables, on_delete=models.CASCADE)
    dishes = models.TextField(help_text="Enter dish IDs separated by commas")
    total_amount = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order for {self.table.name} | Total: {self.total_amount}"


class TempOrderList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    table = models.ForeignKey(Tables, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dishes, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    total_amount = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TempOrderList - User: {self.user.username}, Table: {self.table.name}, Dish: {self.dish.name}, Quantity: {self.quantity}"
