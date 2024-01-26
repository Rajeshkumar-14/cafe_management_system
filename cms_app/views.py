from django.shortcuts import render, get_object_or_404
from .models import OrderList, Tables, Dishes, TempOrderList
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import datetime
from .decorators import allowed_users

__project_by__ = "RajeshKumar"


@login_required(login_url="login")
@allowed_users(allowed_roles=["Staff"])
def index(request):
    user = request.user
    tables = Tables.objects.all()
    dishes = Dishes.objects.all()
    temp_clean_up = TempOrderList.objects.filter(user=user)
    temp_clean_up.delete()

    last_three_orders = OrderList.objects.filter(attended_by=user).order_by("-id")[:3]

    today = timezone.now().date()
    this_month = timezone.now().replace(day=1).date()
    this_year = datetime.now().year

    today_orders = OrderList.objects.filter(attended_by=user, created_at__date=today)
    this_month_orders = OrderList.objects.filter(
        attended_by=user, created_at__date__gte=this_month
    )
    this_year_orders = OrderList.objects.filter(
        attended_by=user, created_at__year=this_year
    )

    today_order_count = today_orders.count()
    today_total_price = (
        today_orders.aggregate(total_price=Sum("total_amount"))["total_price"] or 0
    )

    this_month_order_count = this_month_orders.count()
    this_month_total_price = (
        this_month_orders.aggregate(total_price=Sum("total_amount"))["total_price"] or 0
    )

    this_year_order_count = this_year_orders.count()
    this_year_total_price = (
        this_year_orders.aggregate(total_price=Sum("total_amount"))["total_price"] or 0
    )

    context = {
        "tables": tables,
        "dishes": dishes,
        "last_three_orders": last_three_orders,
        "today_order_count": today_order_count,
        "today_total_price": today_total_price,
        "this_month_order_count": this_month_order_count,
        "this_month_total_price": this_month_total_price,
        "this_year_order_count": this_year_order_count,
        "this_year_total_price": this_year_total_price,
    }
    return render(request, "cms_app/index.html", context)


@allowed_users(allowed_roles=["Staff", "Manager"])
def temp_order(request):
    if request.method == "POST":
        user = request.user
        table_id = request.POST.get("table")
        dish_id = request.POST.get("dish")
        quantity = int(request.POST.get("quantity", 1))

        table = get_object_or_404(Tables, pk=table_id)
        dish = get_object_or_404(Dishes, pk=dish_id)

        total_amount = quantity * dish.price

        temp_order = TempOrderList.objects.filter(user=user, dish=dish).first()

        if temp_order:
            temp_order.quantity += quantity
            temp_order.total_amount += total_amount
            temp_order.save()
        else:
            temp_order = TempOrderList.objects.create(
                user=user,
                table=table,
                dish=dish,
                total_amount=total_amount,
                quantity=quantity,
            )

        temp_orders_for_user = TempOrderList.objects.filter(user=user)
        total_amount_for_user = sum(
            order.total_amount for order in temp_orders_for_user
        )

        data = {"order_total_amount": total_amount_for_user}
        return JsonResponse(data, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)


@allowed_users(allowed_roles=["Staff", "Manager"])
def temp_order_list(request):
    if request.method == "GET":
        temp_orders = TempOrderList.objects.all()

        data = []
        for order in temp_orders:
            data.append(
                {
                    "dish_name": order.dish.name,
                    "price": order.dish.price,
                    "quantity": order.quantity,
                    "total_amount": order.total_amount,
                    "action": f"<div class='btn-group w-100' role='group'>"
                    + f"<button class='btn btn-primary me-1  editBtn' data-dish-id='{order.id}'><i class='fa-solid fa-pen-to-square'></i></button>"
                    + f"<button class='btn btn-danger deleteBtn' data-dish-id='{order.id}'><i class='fa-solid fa-trash'></i></button>"
                    + f"</div>",
                }
            )

        return JsonResponse({"data": data})

    return JsonResponse({"error": "Invalid request method."}, status=405)


@csrf_exempt
@allowed_users(allowed_roles=["Staff", "Manager"])
def delete_temp_order(request, order_id):
    user = request.user
    if request.method == "DELETE":
        try:
            fetch_order = get_object_or_404(TempOrderList, id=order_id)
            print(order_id)
            print(fetch_order)
            fetch_order.delete()
            # Calculate total amount for the user
            temp_orders_for_user = TempOrderList.objects.filter(user=user)
            total_amount_for_user = sum(
                order.total_amount for order in temp_orders_for_user
            )

            data = {"order_total_amount": total_amount_for_user}
            return JsonResponse(data, status=200)
        except TempOrderList.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@allowed_users(allowed_roles=["Staff", "Manager"])
def edit_temp_order(request, order_id):
    if request.method == "GET":
        try:
            fetch_order = get_object_or_404(TempOrderList, id=order_id)

            table_data = {
                "id": fetch_order.table.id,
                "name": fetch_order.table.name,
            }

            data = {
                "order_id": order_id,
                "table": table_data,
                "dish": fetch_order.dish.name,
                "quantity": fetch_order.quantity,
            }
            return JsonResponse(data)
        except TempOrderList.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@allowed_users(allowed_roles=["Staff", "Manager"])
def update_temp_order(request, order_id):
    user = request.user
    if request.method == "POST":
        update_quantity = int(request.POST.get("update_quantity"))

        try:
            fetch_order = TempOrderList.objects.get(id=order_id)
            update_total = fetch_order.dish.price * update_quantity

            fetch_order.quantity = update_quantity
            fetch_order.total_amount = update_total
            fetch_order.save()
            temp_orders_for_user = TempOrderList.objects.filter(user=user)
            total_amount_for_user = sum(
                order.total_amount for order in temp_orders_for_user
            )

            data = {"order_total_amount": total_amount_for_user}
            return JsonResponse(data, status=200)
        except TempOrderList.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


@allowed_users(allowed_roles=["Staff", "Manager"])
def display_order(request, order_id):
    if request.method == "GET":
        order_details = get_object_or_404(OrderList, id=order_id)

        dish_ids = [int(dish_id) for dish_id in order_details.dishes.split(",")]

        dishes = Dishes.objects.filter(id__in=dish_ids)

        data = {
            "id": order_details.id,
            "table_name": order_details.table.name,
            "dishes": [{"name": dish.name, "price": dish.price} for dish in dishes],
            "total_amount": order_details.total_amount,
        }

        return JsonResponse(data)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


@allowed_users(allowed_roles=["Staff", "Manager"])
def order_list(request):
    if request.method == "POST":
        user = request.user

        temp_orders = TempOrderList.objects.filter(user=user)

        if temp_orders.exists():
            total_amount_for_user = temp_orders.aggregate(
                total_amount=Sum("total_amount")
            )["total_amount"]

            if total_amount_for_user is not None:
                table = temp_orders.first().table
                dishes = ",".join(str(order.dish_id) for order in temp_orders)

                order = OrderList.objects.create(
                    attended_by=user,
                    table=table,
                    dishes=dishes,
                    total_amount=total_amount_for_user,
                )

                temp_orders.delete()

                return JsonResponse(
                    {"success": True, "message": "Order submitted successfully."},
                    status=200,
                )
            else:
                return JsonResponse(
                    {"error": "Total amount is None."},
                    status=400,
                )
        else:
            return JsonResponse(
                {"error": "No items in the temporary order list."},
                status=400,
            )

    return JsonResponse({"error": "Invalid request method."}, status=405)
