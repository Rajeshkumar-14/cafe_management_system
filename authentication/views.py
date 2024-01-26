from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.http import JsonResponse
from django.utils.http import urlsafe_base64_decode
from .tasks import send_password_reset, send_welcome_email, password_change_alert
from .models import UserProfile

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm

from .decorators import allowed_users, unauthenticated_user
from django.contrib.auth.decorators import login_required

__project_by__ = "RajeshKumar"


@login_required(login_url="login")
def user_registration(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password1 = request.POST.get("password1")
        user_group_name = request.POST.get("user_group")
        address = request.POST.get("address")
        additional_info = request.POST.get("additional_info")
        zip_code = request.POST.get("zip_code")
        phone_number = request.POST.get("phone_number")

        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            return JsonResponse({"success": False, "message": "Username or email already exists"}, status=400)

        if password != password1:
            return JsonResponse({"success": False, "message": "Passwords do not match"}, status=400)

        try:
            group = Group.objects.get(name=user_group_name)
        except Group.DoesNotExist:
            return JsonResponse({"success": False, "message": "Specified user group does not exist"}, status=400)

        if not (address and additional_info and zip_code and phone_number):
            return JsonResponse({"success": False, "message": "All fields are required"}, status=400)

        if not (zip_code.isdigit() and phone_number.isdigit()):
            return JsonResponse({"success": False, "message": "Zip code and Phone Number must be an integer"}, status=400)

        try:
            user_data = User.objects.create_user(username=username, email=email, password=password)
            user_data.groups.add(group)

            profile = UserProfile(
                user=user_data,
                address=address,
                additional_info=additional_info,
                zip_code=zip_code,
                phone_number=phone_number,
            )
            profile.save()

            send_welcome_email(user_data.email)

            return JsonResponse({"success": True, "message": "Registration Successful"})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Registration error: {str(e)}"}, status=500)

    return JsonResponse({"success": False, "message": "Invalid Request Method"}, status=405)


@unauthenticated_user
def user_login(request):
    show_error_message = False

    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user1 = User.objects.filter(email=email).first()

        if user1 is None:
            show_error_message = True
            messages.error(request, "User with this email does not exist.")
        else:
            user = authenticate(request, username=user1.username, password=password)
            if user is not None:
                login(request, user)

                if user.groups.filter(name="Manager").exists():
                    return redirect("manager-index")
                elif user.groups.filter(name="Administrator").exists():
                    return redirect(reverse("admin:index"))
                elif user.groups.filter(name="Staff").exists():
                    return redirect("index")
                else:
                    return redirect(reverse("admin:index"))
            else:
                show_error_message = True
                messages.error(request, "Invalid Password. Please try again.")

    context = {"show_error_message": show_error_message}
    return render(request, "authentication/login.html", context)


def user_logout(request):
    logout(request)
    return redirect("login")


@unauthenticated_user
def reset_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            send_password_reset(user.pk)
            messages.success(request, "Password reset email sent successfully.")
            return redirect("login")
        except User.DoesNotExist:
            messages.error(request, "User with this email does not exist.")

    return render(request, "authentication/reset-email.html")


@unauthenticated_user
def reset_confirm(request, uidb64, token):
    User = get_user_model()

    uid = urlsafe_base64_decode(uidb64).decode()

    try:
        user = User.objects.get(pk=uid)
    except User.DoesNotExist:
        messages.error(request, "Invalid user. Please try the password reset again.")
        return redirect("login")

    form = SetPasswordForm(user)

    if request.method == "POST":
        password = request.POST.get("password")
        password1 = request.POST.get("password1")

        if password == password1:
            form = SetPasswordForm(
                user, {"new_password1": password, "new_password2": password1}
            )

            if form.is_valid():
                form.save()
                messages.success(
                    request,
                    "Password reset successful. You can now log in with your new password.",
                )
                password_change_alert(user.email)
                return redirect("login")
            else:
                messages.error(
                    request,
                    "Invalid form data. Please correct the errors and try again.",
                )
    else:
        messages.error(
            request, "Passwords do not match. Please enter matching passwords."
        )

    context = {"form": form}
    return render(request, "authentication/reset-password.html", context)


def staff_details(request):
    staff_id = request.GET.get("staff_id")
    staff = get_object_or_404(User, pk=staff_id)
    staff_details = get_object_or_404(UserProfile, user=staff)

    user_group = staff.groups.first().name if staff.groups.exists() else None

    staff_data = {
        "id": staff.id,
        "username": staff.username,
        "email": staff.email,
        "address": staff_details.address,
        "additional_info": staff_details.additional_info,
        "zip_code": staff_details.zip_code,
        "user_group": user_group,
        "phone_number": staff_details.phone_number,
    }
    return JsonResponse(staff_data)


@login_required(login_url="login")
def edit_staff_detail(request, staff_id):
    if request.method == "POST":
        try:
            staff = User.objects.get(id=staff_id)
            staff_details = UserProfile.objects.get(user=staff)

            staff.username = request.POST.get("username")
            staff.email = request.POST.get("email")

            staff_details.address = request.POST.get("address")
            staff_details.additional_info = request.POST.get("additional_info")
            staff_details.zip_code = request.POST.get("zip_code")
            staff_details.phone_number = request.POST.get("phone_number")
            staff_details.save()
            staff.save()
            return JsonResponse({"success": True, "message": "Success"}, status=200)
        except User.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "User or UserProfile Not Found"},
                status=404,
            )
    else:
        return JsonResponse({"success": False, "message": "Bad Request"}, status=403)
