from rest_framework import serializers
from .models import Admin, Employee, Department, Contact, Task, FinishedTask, EmployeeSignUp, TaskAssignment

# Serializer cho model Admin
class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['email', 'password']

# Serializer cho model Employee
class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['name', 'department', 'employee_id', 'address', 'contact_number', 'destination', 
                  'date_of_birth', 'date_of_joining', 'email', 'designation', 
                  'description', 'picture']

# Serializer cho model Department
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['name', 'code', 'head', 'location', 'description']

# Serializer cho model Contact
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'email', 'mobile', 'message', 'created_at']

# Serializer cho model Task
class TaskSerializer(serializers.ModelSerializer):
    assigned_to = EmployeeSerializer()  # Để ánh xạ Employee thông qua Task
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'deadline_date', 'deadline_time', 'email', 
                  'created_at', 'priority', 'category']

# Serializer cho model FinishedTask
class FinishedTaskSerializer(serializers.ModelSerializer):
    assigned_to = EmployeeSerializer()  # Để ánh xạ Employee thông qua FinishedTask
    class Meta:
        model = FinishedTask
        fields = ['title', 'description', 'assigned_to', 'deadline_date', 'deadline_time', 'email', 'finished']

# Serializer cho model EmployeeSignUp
class EmployeeSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSignUp
        fields = ['name', 'email', 'password']

class TaskAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAssignment
        fields = '__all__'