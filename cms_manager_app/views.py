from django.shortcuts import render, get_object_or_404
from cms_app.models import OrderList, Tables, Dishes, TempOrderList
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from datetime import date, timedelta
from django.contrib.auth.models import User, Group
from django.contrib.humanize.templatetags.humanize import intcomma
from .decorators import allowed_users
from django.views.generic import View


@login_required(login_url="login")
@allowed_users(allowed_roles=["Manager"])
def manager_index(request):
    user = request.user
    # Staff
    staff_group = Group.objects.get(name="Staff")
    staff_users = User.objects.filter(groups=staff_group)
    total_staff_count = staff_users.count()
    staff_present_today_count = staff_users.filter(
        last_login__date=timezone.now().date()
    ).count()
    staff_absent_today_count = total_staff_count - staff_present_today_count

    # Manager
    manager_group = Group.objects.get(name="Manager")
    manager_users = User.objects.filter(groups=manager_group)
    total_manager_count = manager_users.count()
    manager_present_today_count = manager_users.filter(
        last_login__date=timezone.now().date()
    ).count()
    manager_absent_today_count = total_manager_count - manager_present_today_count

    tables = Tables.objects.all()
    dishes = Dishes.objects.all()

    total_tables_count = tables.count()
    total_dishes_count = dishes.count()

    temp_clean_up = TempOrderList.objects.filter(user=user)
    temp_clean_up.delete()

    # Profit
    today = date.today()
    this_month_start = today.replace(day=1)
    this_year_start = today.replace(month=1, day=1)
    previous_year_start = this_year_start - timedelta(days=365)

    today_profit = (
        OrderList.objects.filter(created_at__date=today).aggregate(
            today_profit=Sum("total_amount")
        )["today_profit"]
        or 0
    )

    this_month_profit = (
        OrderList.objects.filter(created_at__date__gte=this_month_start).aggregate(
            this_month_profit=Sum("total_amount")
        )["this_month_profit"]
        or 0
    )

    this_year_profit = (
        OrderList.objects.filter(created_at__date__gte=this_year_start).aggregate(
            this_year_profit=Sum("total_amount")
        )["this_year_profit"]
        or 0
    )

    previous_year_profit = (
        OrderList.objects.filter(
            created_at__date__gte=previous_year_start,
            created_at__date__lt=this_year_start,
        ).aggregate(previous_year_profit=Sum("total_amount"))["previous_year_profit"]
        or 0
    )

    formatted_today_profit = intcomma(today_profit)
    formatted_this_month_profit = intcomma(this_month_profit)
    formatted_this_year_profit = intcomma(this_year_profit)
    formatted_previous_year_profit = intcomma(previous_year_profit)

    context = {
        "tables": tables,
        "dishes": dishes,
        "staffs": staff_users,
        "total_staff_count": total_staff_count,
        "total_manager_count": total_manager_count,
        "staff_present_today_count": staff_present_today_count,
        "staff_absent_today_count": staff_absent_today_count,
        "manager_present_today_count": manager_present_today_count,
        "manager_absent_today_count": manager_absent_today_count,
        "total_tables_count": total_tables_count,
        "total_dishes_count": total_dishes_count,
        "today_profit": formatted_today_profit,
        "this_month_profit": formatted_this_month_profit,
        "this_year_profit": formatted_this_year_profit,
        "previous_year_profit": formatted_previous_year_profit,
    }
    return render(request, "cms_manager_app/manager-index.html", context)


class TodaysOrdersView(View):
    def get(self, request, *args, **kwargs):
        # Get today's date
        today = date.today()
        # Filter orders for today
        orders = OrderList.objects.filter(created_at__date=today)
        # Serialize orders data
        data = [
            {
                "id": order.id,
                "attended_by": order.attended_by.username,
                "table_name": order.table.name,
                "total_amount": order.total_amount,
                "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for order in orders
        ]
        return JsonResponse(data, safe=False)


@login_required(login_url="login")
@allowed_users(allowed_roles=["Manager"])
def add_table(request):
    user = request.user
    if request.method == "POST":
        table_name = request.POST.get("table_name")
        table = Tables.objects.create(name=table_name, created_by=user)
        table.save()
        return JsonResponse(
            {"success": True, "message": "Table Created Successful"}, status=201
        )
    else:
        return JsonResponse(
            {"success": False, "message": "Error Creating the Table"}, status=500
        )


@allowed_users(allowed_roles=["Manager"])
def edit_table(request):
    if request.method == "POST":
        table_id = request.POST.get("table_id")
        try:
            table = Tables.objects.get(id=table_id)

            data = {
                "id": table.id,
                "table_name": table.name,
            }
            return JsonResponse(data, status=200)
        except Tables.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Table Does not exists."}, status=404
            )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid Request Method"}, status=403
        )


@allowed_users(allowed_roles=["Manager"])
def update_table(request, table_id):
    if request.method == "POST":
        try:
            table = Tables.objects.get(id=table_id)
            name = request.POST.get("table_name")

            table.name = name
            table.save()
            return JsonResponse(
                {"success": True, "message": "Table Updated Successfully."}, status=200
            )
        except Tables.DoesNotExist():
            return JsonResponse(
                {"success": False, "message": "Table Does not exists."}, status=404
            )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid Request Method."}, status=403
        )


@login_required(login_url="login")
@allowed_users(allowed_roles=["Manager"])
def add_dish(request):
    user = request.user
    if request.method == "POST":
        dish_name = request.POST.get("dish_name")
        dish_price = request.POST.get("dish_price")

        # Basic validation
        if not dish_name or not dish_price:
            return JsonResponse(
                {"success": False, "message": "Dish name and price are required."},
                status=400,
            )

        try:
            dish_price = float(dish_price)
        except ValueError:
            return JsonResponse(
                {"success": False, "message": "Invalid price format."}, status=400
            )

        # Create the Dish object
        try:
            dish = Dishes.objects.create(
                name=dish_name, price=dish_price, created_by=user
            )
            return JsonResponse(
                {
                    "success": True,
                    "message": "Dish created successfully",
                    "dish_id": dish.id,
                },
                status=201,
            )
        except Exception as e:
            return JsonResponse(
                {"success": False, "message": f"Error creating the dish: {str(e)}"},
                status=500,
            )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


@allowed_users(allowed_roles=["Manager"])
def edit_dish(request):
    if request.method == "POST":
        dish_id = request.POST.get("dish_id")
        try:
            dish = Dishes.objects.get(id=dish_id)

            data = {
                "id": dish.id,
                "dish_name": dish.name,
                "dish_price": dish.price,
            }
            return JsonResponse(data, status=200)
        except Tables.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Dish Does not exists."}, status=404
            )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid Request Method"}, status=403
        )


@allowed_users(allowed_roles=["Manager"])
def update_dish(request, dish_id):
    if request.method == "POST":
        try:
            dish = Dishes.objects.get(id=dish_id)
            name = request.POST.get("dish_name")
            price = request.POST.get("dish_price")

            dish.name = name
            dish.price = price
            dish.save()
            return JsonResponse(
                {"success": True, "message": "Dish Updated Successfully."}, status=200
            )
        except Dishes.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Dish Does not exists."}, status=404
            )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid Request Method."}, status=403
        )


def print_preview(request):
    if request.method == "POST":
        try:
            order_id = request.POST.get("order_id")
            order_details = OrderList.objects.get(id=order_id)

            # Fetch the dish IDs and split them into a list
            dish_ids = order_details.dishes.split(",")

            # Fetch the corresponding Dishes objects
            dishes = Dishes.objects.filter(id__in=dish_ids)

            # Prepare data to send to the template
            data = {
                "table": order_details.table.name,
                "attended_by": order_details.attended_by.username,
                "dishes": list(
                    dishes.values()
                ),  # Convert QuerySet to list of dictionaries
                "total_amount": order_details.total_amount,
            }
            return JsonResponse(data)
        except OrderList.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Order does not exist."}, status=404
            )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method."}, status=403
        )

