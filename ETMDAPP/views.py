from django.core.exceptions import ValidationError
from .forms import TaskAssignmentForm
from .models import EmployeeSignUp
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.http import HttpResponse
from .utils import (
    generate_task_distribution_plot,
    generate_remaining_tasks_plot,
    generate_task_deadlines_table,
    generate_completed_tasks_over_time_plot,
    generate_employee_performance_plot,
    generate_task_description_wordcloud,
    generate_completion_rate_by_employee_plot,
    generate_task_distribution_by_category_plot,
    generate_task_distribution_by_priority_plot,
    generate_task_duration_distribution_plot,  # Đảm bảo hàm này không bị bỏ qua nếu cần
)
from django.contrib.auth import authenticate, login
from .models import FinishedTask
from django.shortcuts import redirect, render, get_object_or_404
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import redirect, render
from .models import Task
from .models import EmployeeSignUp  # Import the Employee model
from .models import Task, FinishedTask
from .forms import TaskForm
from .models import Employee, Task
from .forms import ContactForm
from django.shortcuts import render, get_object_or_404, redirect
from .forms import TaskAssignmentForm
from .forms import DepartmentForm
from .models import Department
from .models import TaskAssignment
from .forms import EmployeeForm
from .forms import EmployeeForm  # Import the form
from .models import Employee
from django.shortcuts import render, redirect
from .models import Admin
from django.shortcuts import render
from django.db.models import Count

# Create your views here.

def HOME(request):
    return render(request,"HOME.html")


def REGIEMP(request):
    departments = Department.objects.all()

    if request.method == "POST":
        try:
            emp = Employee(
                name=request.POST.get("firstname"),
                department=request.POST.get("department"),
                employee_id=request.POST.get("id"),
                address=request.POST.get("address"),
                contact_number=request.POST.get("number"),
                destination=request.POST.get("dest"),
                date_of_birth=request.POST.get("dob"),
                date_of_joining=request.POST.get("doj"),
                email=request.POST.get("email"),
                designation=request.POST.get("des"),
                description=request.POST.get("desc"),
            )

            # Xử lý hình ảnh nếu có
            if request.FILES.get("pictureInput"):
                emp.picture = request.FILES["pictureInput"]

            emp.save()
            return render(request, "REGIEMP.html", {
                "success_message": "Thêm nhân viên thành công!",
                "departments": departments
            })
        except Exception as e:
            print("Lỗi khi thêm nhân viên:", e)
            return render(request, "REGIEMP.html", {
                "error_message": "Có lỗi xảy ra!",
                "departments": departments
            })

    return render(request, "REGIEMP.html", {"departments": departments})



def employeesignuplogin(request):
    if request.method == "POST":
        email = request.POST.get("LOGINEmail")
        password = request.POST.get("LOGINPassword")

        # Check if email and password are provided for login
        if email and password:
            try:
                user = EmployeeSignUp.objects.get(email=email)
                # Use check_password to compare hashed password
                if check_password(password, user.password):
                    # Authentication successful
                    print("Authentication successful")
                    # Store user info in session
                    request.session['EmployeeEmail'] = email
                    request.session['EmployeeUsername'] = user.name
                    return redirect("EMPDashboard")
                else:
                    # Authentication failed - invalid password
                    print("Authentication failed: Invalid password")
                    return render(request, "LOGIN.html", {'error_message': "Invalid email or password"})
            except EmployeeSignUp.DoesNotExist:
                # Authentication failed - user not found
                print("Authentication failed: User not found")
                return render(request, "LOGIN.html", {'error_message': "Invalid email or password"})

        else:
            # Signup process
            name = request.POST.get("Name")
            email = request.POST.get("Email")
            password = request.POST.get("Password")

            # Check if email and password are provided for signup
            if email and password:
                if EmployeeSignUp.objects.filter(email=email).exists():
                    # Email already exists
                    return render(request, "LOGIN.html", {'error_message': "Email is already registered. Please use a different email."})

                # Hash password before saving
                hashed_password = make_password(password)
                new_user = EmployeeSignUp(name=name, email=email, password=hashed_password)
                new_user.save()

                # Successful signup, prompt user to login
                return render(request, "LOGIN.html", {'success_message': "Sign up successful! Please log in"})

            else:
                # Missing email or password for signup or login
                return render(request, "LOGIN.html", {'error_message': "Please provide email and password"})

    # Render the login page for GET requests
    return render(request, "LOGIN.html")


def handle_login(request, data):
    email = data["Email"]
    password = data["Password"]

    # Authenticate the user
    user = authenticate(request, email=email, password=password)

    if user is not None:
        # Login the user
        login(request, user)
        # Redirect to a success page or homepage
        return redirect("home")
    else:
        # If authentication fails, display an error message for login
        error_message = "Invalid email or password. Please try again."
        return render(request, "login.html", {"error_message": error_message})


def employee_list(request):
    try:
        query = request.GET.get('q')
        if query:
            employees = Employee.objects.filter(email__icontains=query)
        else:
            employees = Employee.objects.all()
        return render(request, 'emplist.html', {'employees': employees, 'query': query})
    except ValidationError as ve:
        # Handle validation errors
        error_message = "Validation Error: {}".format(ve)
        return render(request, "error.html", {'error_message': error_message})
    except Exception as e:
        # Handle other exceptions
        error_message = "An error occurred while processing your request."
        return render(request, "error.html", {'error_message': error_message})



def search_employee(request):
    query_email = request.GET.get('email')
    query_emp_id = request.GET.get('emp_id')

    employees = Employee.objects.all()  # Default queryset

    if query_email:
        employees = employees.filter(email__icontains=query_email)
    if query_emp_id:
        employees = employees.filter(employee_id__icontains=query_emp_id)

    return render(request, 'emplist.html', {'employees': employees, 'query_email': query_email, 'query_emp_id': query_emp_id})


def delete_employee(request, pk):
    employee = Employee.objects.get(pk=pk)
    employee.delete()
    return redirect('employee_list')


def edit_employee(request, pk):
    employee = Employee.objects.get(pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('AdminDashboard')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'editemp.html', {'form': form})

def ABOUT(request):
    return render(request, "ABOUT.html")


def EMPDASHBOARD(request):
    try:
        email = request.session.get("EmployeeEmail")

        if not email:
            return render(request, "error.html", {
                'error_message': "Session data missing. Please log in again."
            })

        employee = Employee.objects.get(email=email)

        # Tổng số công việc (trong bảng Task, chưa hoàn thành)
        total_tasks = Task.objects.filter(assigned_to=employee).count()

        # Công việc vừa bắt đầu (tiến độ từ 1 đến 10%)
        just_started_tasks = TaskAssignment.objects.filter(
            employee=employee,
            progress__gte=1,
            progress__lte=10
        ).count()

        # Công việc đang làm (tiến độ từ 11 đến 99%)
        in_progress_tasks = TaskAssignment.objects.filter(
            employee=employee,
            progress__gt=10,
            progress__lt=100
        ).count()

        # Công việc đã hoàn thành
        completed_tasks = FinishedTask.objects.filter(
            assigned_to=employee,
            finished=True
        ).count()

        return render(request, "EMPDashboard.html", {
            'total_tasks': total_tasks,
            'just_started_tasks': just_started_tasks,
            'in_progress_tasks': in_progress_tasks,
            'completed_tasks': completed_tasks,
        })

    except Employee.DoesNotExist:
        return render(request, "error.html", {
            'error_message': "Employee not found."
        })
    except Exception as e:
        return render(request, "error.html", {
            'error_message': f"An unexpected error occurred: {str(e)}"
        })



    
def REGIDMENT(request):
    return render(request, "REGIDMENT.html")

from django.shortcuts import redirect


def logout(request):
    try:
        # Check if the 'admin_email' session variable exists
        if 'admin_email' in request.session:
            # Delete the 'admin_email' session variable
            del request.session['admin_email']

        # Check if other session variables exist and delete them based on conditions
        if 'EmployeeEmail' in request.session:
            del request.session['EmployeeEmail']
        if 'EmployeeUsername' in request.session:
            del request.session['EmployeeUsername']

        # Redirect to the home page after logout
        # Replace 'HOME' with the name of your home page URL pattern
        return redirect('HOME')
    except Exception as e:
        # Handle any exceptions
        error_message = "An error occurred while logging out."
        return render(request, "error.html", {'error_message': error_message})

 
def ADMINLOGIN(request):
    if request.method == "POST":
        # Lấy email và mật khẩu từ form
        admin_email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            # Truy vấn admin dựa trên email
            admin = Admin.objects.get(email=admin_email)
        except Admin.DoesNotExist:
            return render(request, "adminlogin.html", {"error_message": "Admin not found"})

        # Kiểm tra nếu mật khẩu đúng
        if check_password(password, admin.password):
            # Tạo session cho admin
            request.session['admin_email'] = admin.email

            # Redirect đến trang Dashboard của admin
            total_employees = Employee.objects.count()  # Nếu cần, có thể sử dụng biến này ở đâu đó
            return redirect("AdminDashboard")
        else:
            return render(request, "adminlogin.html", {"error_message": "Invalid credentials"})

    # Nếu không phải POST, trả về trang login với admin_email trong session (nếu có)
    admin_email = request.session.get('admin_email', None)
    return render(request, "adminlogin.html", {"admin_email": admin_email})


def AdminDashboard(request):
    try:
        # Check if the 'admin_email' session variable exists
        admin_email = request.session.get('admin_email', None)
        if admin_email is None:
            return redirect('ADMINLOGIN')

        # Total count of employees and departments
        total_employees = Employee.objects.count()
        total_departments = Department.objects.count()

        # Count of finished tasks
        finished_tasks_count = FinishedTask.objects.count()

        # Count of assigned tasks (assuming each employee can have multiple tasks)
        assigned_tasks_count = Task.objects.count()

        return render(request, "AdminDashboard.html", {
            'total_employees': total_employees,
            'total_departments': total_departments,
            'finished_tasks_count': finished_tasks_count,
            'assigned_tasks_count': assigned_tasks_count,
            'admin_email': admin_email,
        })
    except Exception as e:
        # Handle any exceptions
        error_message = f"An error occurred: {str(e)}"
        return render(request, "error.html", {'error_message': error_message})


def REGIDMENT(request):
    try:
        # Check if the 'admin_email' session variable exists
        admin_email = request.session.get('admin_email', None)
        if admin_email is None:
            return redirect('ADMINLOGIN')

        if request.method == 'POST':
            form = DepartmentForm(request.POST)
            if form.is_valid():
                form.save()
                # Redirect to a page showing department list
                return redirect('AdminDashboard')
        else:
            form = DepartmentForm()
        return render(request, 'REGIDMENT.html', {'form': form, 'admin_email': admin_email})
    except Exception as e:
        # Handle any exceptions
        error_message = "An error occurred while processing department registration."
        return render(request, "error.html", {'error_message': error_message})


def department_list(request):
    departments = Department.objects.all()
    total_departments = departments.count()
    context = {
        'departments': departments,
        'total_departments': total_departments
    }
    return render(request, 'Dlist.html', context)


# views.py


def edit_department(request, department_id):
    department = get_object_or_404(Department, pk=department_id)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            # Redirect to department list page after successful edit
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'edit_department.html', {'form': form})


def delete_department(request, department_id):
    department = get_object_or_404(Department, pk=department_id)
    if request.method == 'POST':
        department.delete()
        # Redirect to department list page after successful delete
        return redirect('department_list')
    return render(request, 'AdminDashboard', {'department': department})



def search_department(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        departments = Department.objects.filter(name__icontains=name)
        return render(request, 'Dlist.html', {'departments': departments})
    else:
        # Trả về một trang tìm kiếm trống hoặc thông báo
        return render(request, 'department_search_results.html')  # giả sử bạn có một form tìm kiếm


def CONTACT(request):
    try:
        if request.method == 'POST':
            form = ContactForm(request.POST)
            if form.is_valid():
                # Save form data
                form.save()
                # Redirect to the home page after successful form submission
                return redirect('HOME')
        else:
            form = ContactForm()
        return render(request, 'CONTACT.html', {'form': form})
    except Exception as e:
        # Handle any exceptions
        error_message = "An error occurred while processing the contact form."
        return render(request, "error.html", {'error_message': error_message})

def assign_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            assigned_employees = form.cleaned_data['assigned_to']
            task.assigned_to.set(assigned_employees)
            task.save()

            # ✅ Tạo bản ghi TaskAssignment cho mỗi nhân viên
            for employee in assigned_employees:
                TaskAssignment.objects.create(
                    task=task,
                    employee=employee,
                    progress=0  # Ban đầu 0%
                )

            return redirect('taskemployeelist')  # Hoặc bất kỳ tên URL nào
    else:
        form = TaskForm()

    return render(request, 'assigntask.html', {'form': form})


def task_des(request):
    # Get employees who have been assigned tasks
    employees_with_tasks = Employee.objects.filter(
        task__isnull=False).distinct().annotate(task_count=Count('task'))
    return render(request, 'TaskDes.html', {'employees': employees_with_tasks})

def assigned_tasks(request):
    employee_data = []

    # Lặp qua từng nhân viên
    for emp in Employee.objects.all():
        # Lấy danh sách các task đã giao cho nhân viên này
        assignments = TaskAssignment.objects.filter(employee=emp).select_related('task')

        task_list = []
        for assign in assignments:
            task_list.append({
                'task': assign.task,
                'progress': assign.progress,
                'notes': assign.notes,
                'updated_at': assign.updated_at,
                'start_date': assign.start_date
            })

        employee_data.append({
            'employee': emp,
            'tasks': task_list
        })

    return render(request, 'AssignTasks.html', {'employee_data': employee_data})


def TaskReport(request):
    # Generate plots
    generate_task_distribution_plot()
    generate_remaining_tasks_plot()
    generate_task_deadlines_table()  # Nếu muốn dùng kết quả này trong template, cần trả về
    generate_completed_tasks_over_time_plot()
    generate_employee_performance_plot()
    generate_task_description_wordcloud()
    generate_completion_rate_by_employee_plot()
    generate_task_distribution_by_category_plot()
    generate_task_distribution_by_priority_plot()
    generate_task_duration_distribution_plot()  # Đảm bảo không bị comment lại nếu cần thiết

    # Nếu muốn trả về kết quả bảng deadline trong context (nếu dùng trong template)
    deadlines_data = generate_task_deadlines_table()

    context = {
        'deadlines_data': deadlines_data  # Đưa data vào context nếu cần
    }

    # Render the template
    return render(request, 'TaskReport.html', context)



def mark_task_finished(request, task_id, email):
    if request.method == 'POST':
        # Retrieve the task associated with the provided ID
        task = get_object_or_404(Task, pk=task_id, assigned_to__email=email)

        # Create a FinishedTask object with the details of the original task
        finished_task = FinishedTask.objects.create(
            title=task.title,
            description=task.description,
            deadline_date=task.deadline_date,
            deadline_time=task.deadline_time,
            email=task.email,
            finished=True  # Mark the task as finished
        )

        # Gán nhân viên đã được giao cho công việc gốc vào finished_task
        finished_task.assigned_to.set(task.assigned_to.all())  # Sử dụng .all() để lấy tất cả nhân viên trong trường Many-to-Many

        # Save the finished task
        finished_task.save()

        # Delete the original task
        task.delete()

        # Redirect the user to a success page or another appropriate URL
        return redirect('AdminDashboard')
    else:
        # Handle GET requests appropriately, if needed
        pass



def DEV(request):
    return render(request, "Developers.html")


def task_end_dates(request):
    tasks = Task.objects.all()
    return render(request, 'taskenddate.html', {'tasks': tasks})

def EMPAccount(request):
    return render(request,"EMPAccount.html")


def TaskDashboard(request):
    # Assuming you get email from session
    email = request.session.get("EmployeeEmail")

    # Filter tasks assigned to the employee (using assigned_to relationship)
    assigned_tasks = Task.objects.filter(email=email)

    total_tasks = assigned_tasks.count()
    completed_tasks = FinishedTask.objects.filter(
        email=email, finished=True).count()

    # Calculate completion rate with potential zero division handling and 50% for equal values
    completion_rate = 0
    if total_tasks > 0:
        if total_tasks == completed_tasks:
            completion_rate = 50  # Set 50% for equal completed and total tasks
        else:
            completion_rate = round((completed_tasks / total_tasks) * 100,2)
    performance_rate = completion_rate
    NoOfTasks=total_tasks + completed_tasks

    context = {
        'completion_rate': completion_rate,
        'total_tasks': NoOfTasks,
        'performance_rate': performance_rate,
    }

    return render(request, "EMPTaskDashboard.html", context)


def EMPTaskEndDate(request):
    try:
        # Check if the 'EmployeeEmail' session variable exists
        email = request.session.get("EmployeeEmail", None)
        if email:
            tasks = Task.objects.filter(email=email)
        else:
            tasks = []

        return render(request, 'EMPTaskEndDate.html', {'tasks': tasks})
    except Exception as e:
        # Handle any exceptions
        error_message = "An error occurred while loading the employee tasks."
        return render(request, "error.html", {'error_message': error_message})



def EmployeeTask(request):
    try:
        # Check if the 'EmployeeEmail' session variable exists
        email = request.session.get("EmployeeEmail", None)
        username = request.session.get("EmployeeUsername", None)

        if email:
            # Lọc tất cả các task mà email của nhân viên có trong danh sách emails
            tasks = Task.objects.filter(emails__contains=email)
        else:
            tasks = []

        return render(request, 'EmployeeTask.html', {'email': email, 'tasks': tasks, 'username': username})
    except Exception as e:
        print("=== LỖI DASHBOARD ===")  
        print(e)  # 👈 In ra lỗi cụ thể để bạn biết
        error_message = f"Lỗi khi load trang dashboard: {str(e)}"
        return render(request, "error.html", {'error_message': error_message})
    
def finished_tasks_view(request):
    try:
        finished_tasks = FinishedTask.objects.filter(finished=True)  # chỉ lấy các task đã đánh dấu hoàn thành
        return render(request, 'finished_tasks.html', {'finished_tasks': finished_tasks})
    except Exception as e:
        print("=== LỖI HIỂN THỊ TASK HOÀN THÀNH ===")
        print(e)
        return render(request, 'error.html', {'error_message': str(e)})


def employee_dashboard(request):
    email = request.session.get("EmployeeEmail")

    if email:
        try:
            employee = Employee.objects.get(email=email)
            assigned_tasks = Task.objects.filter(assigned_to=employee)
            total_tasks = assigned_tasks.count()
            completed_tasks_qs = FinishedTask.objects.filter(assigned_to=employee, finished=True)
            completed_tasks = completed_tasks_qs.count()
            in_progress_tasks = total_tasks - completed_tasks

            return render(request, 'employee_dashboard.html', {
                'tasks': assigned_tasks,
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'in_progress_tasks': in_progress_tasks
            })

        except Employee.DoesNotExist:
            return HttpResponse("Không tìm thấy nhân viên.")

    return redirect('login')

def update_Assignment(request, task_id):
    email = request.session.get("EmployeeEmail")
    task = get_object_or_404(Task, id=task_id)
    employee = get_object_or_404(Employee, email=email)

    assignment, created = TaskAssignment.objects.get_or_create(task=task, employee=employee)

    if request.method == 'POST':
        form = TaskAssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            assignment = form.save()

            if assignment.progress == 100:
                # Tạo công việc đã hoàn thành (KHÔNG truyền task)
                finished_task = FinishedTask.objects.create(
                    title=task.title,
                    description=task.description,
                    deadline_date=task.deadline_date,
                    deadline_time=task.deadline_time,
                    email=task.email,
                    finished=True
                )

                # Gán nhân viên
                finished_task.assigned_to.set(task.assigned_to.all())

                # Sau khi lưu FinishedTask mới xóa task
                task.delete()

                return redirect('employee_dashboard')

            return redirect('update_assignment', task_id=task.id)
    else:
        form = TaskAssignmentForm(instance=assignment)

    return render(request, 'update_assignment.html', {
        'task': task,
        'form': form,
        'assignment': assignment,
    })


import pandas as pd
from django.shortcuts import render
import requests
from io import BytesIO

def timesheet_view(request):
    import requests
    import pandas as pd
    from io import BytesIO
    import datetime

    url = 'https://docs.google.com/spreadsheets/d/1hRBixIYOX5_oaXOawR16OFmsI1UBIYNqgs30GoPJja0/export?format=xlsx'
    response = requests.get(url)
    if response.status_code != 200:
        return render(request, 'Chamcong.html', {'error': 'Không tải được file Excel từ Google Sheets'})

    file_bytes = BytesIO(response.content)
    try:
        xls = pd.ExcelFile(file_bytes)
        sheet_names = xls.sheet_names

        selected_sheet = request.GET.get('sheet', sheet_names[0])
        selected_sheet = selected_sheet.strip()
        match_sheets = [s for s in sheet_names if s.strip().lower() == selected_sheet.lower()]
        if match_sheets:
            selected_sheet = match_sheets[0]
        else:
            selected_sheet = sheet_names[0]

        df = pd.read_excel(xls, sheet_name=selected_sheet, header=2)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df.dropna(axis=1, how='all', inplace=True)
        if df.columns[0] != 'STT':
            df.rename(columns={df.columns[0]: 'STT'}, inplace=True)
        df = df.fillna('')

        table_html = df.to_html(classes='table table-bordered table-striped', index=False)

        report_date = datetime.datetime.now().strftime('%d/%m/%Y')

        context = {
            'sheet_names': sheet_names,
            'selected_sheet': selected_sheet,
            'table': table_html,
            'report_date': report_date,
        }
        return render(request, 'Chamcong.html', context)
    except Exception as e:
        return render(request, 'Chamcong.html', {'error': f'Lỗi khi đọc file Excel: {str(e)}'})
