# Django Cafe Management System (CMS)

The Django Cafe Management System (CMS) is a web application designed to manage cafe operations, including taking orders from customers, saving them to the database in the billing area, and allowing manager to view and print the orders created on that day. The system includes group role permissions and has a responsive layout for mobile, tablet, and desktop devices. It is built using HTML5, CSS3, jQuery, AJAX, Bootstrap 5, Font Awesome, SweetAlert (Swal), DataTables, and uses Poetry for package management.

## Features

- Take orders from customer tables
- Save orders to the database in the billing area
- View and print orders made by staff on that day
- Group role permissions
- Responsive layout for mobile, tablet, and desktop devices

## Technologies Used

- HTML5
- CSS3
- jQuery
- AJAX
- Bootstrap 5
- Font Awesome
- SweetAlert (Swal)
- DataTables
- Poetry (for package management)

## Project Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Rajeshkumar-14/cafe_management_system.git
   ```
2. **Create and Activate Conda Environment:**

   - Create a new Conda environment or use your existing environment:

     ```bash
     conda create --name cms-env python=3.12
     ```

   - Activate the Conda environment:

     ```bash
     conda activate cms-env
     ```
3. **Create .env file:**

   - Create a `.env` file in the main directory for mail sending purpose using [mailtrap.io](https://mailtrap.io/).

     ```env
     EMAIL_HOST=sandbox.smtp.mailtrap.io,
     EMAIL_PORT=2525,
     EMAIL_HOST_USER=your_username,
     EMAIL_HOST_PASSWORD=your_password,
     ```

   - Remove spaces between the variable and equals and the value to avoid errors while copying from the website.

4. **Install Dependencies:**

   - Install Poetry:

     ```bash
     pip install poetry
     ```

   - Run this command after installing Poetry:

     ```bash
     poetry install
     ```

5. **Database Setup:**

   - Run these commands to migrate models:

     ```bash
     python manage.py makemigrations
     python manage.py migrate
     ```

   - If the above commands don't work, try:

     ```bash
     python manage.py makemigrations authentication
     python manage.py makemigrations cms_app
     python manage.py migrate
     ```

6. **Create Superuser:**

   ```bash
   python manage.py createsuperuser
    ```
7. **Run Server**
  ```bash
    python manage.py runserver
  ```

## Usage

### Admin Panel

- Visit the admin panel at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) and log in with your superuser credentials.
- Create groups with the exact names **Administrator**, **Manager**, and **Staff** and assign appropriate **Permissions**.
- The **Superuser** will be the **Administrator**, and others cannot access the admin panel.
⚠️ **Note:** Before registering users, ensure that you have created the necessary groups, as the system redirects you to the respective Landing Page.

### Admin Permissions

- Admin has all the access to the CRUD operations.

### Manager Page

- Manager can add or edit content but can't delete content.
- Manager has access to print bills.

### Staff Page

- Staff can only access the contents created by the Administrator or Manager.
- They can take orders from Customers and save them in the database.
⚠️ **Note:** Staff page can also be accessed on mobile phones; it's responsive.

## Contributing

Contributions are welcome! If you'd like to contribute to the Django Cafe Management System, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature-name`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Create a new Pull Request.

