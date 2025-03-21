from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.models import User,Group
from django.contrib.auth import login,authenticate,logout
from users.forms import CustomRegistrationForm,AssignRoleForm,CreateGroupForm
from django.contrib import messages
from users.forms import LoginForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth import get_user_model
from django.db.models import Prefetch



def is_admin(user):
    user = get_user_model().objects.get(id=user.id)  # Reload
    return user.groups.filter(name__iexact='admin').exists()


# Create your views here.
def sign_up(request):
      if request.method == 'GET':
         form=CustomRegistrationForm()
      if request.method == 'POST':
          form=CustomRegistrationForm(request.POST)
          if form.is_valid():
              user=form.save(commit=False)
              user.set_password(form.cleaned_data.get('password1'))
              user.is_active=False
              user.save()
              messages.success(request, "A Confirmation mail was Sent check your Email")
              return redirect('sign-in')
          else:
              messages.error(request, "Invalid,please Try Again !")
              print("password do not match")
      return render(request, 'registration/register.html',{'form':form})
 
def  sign_in(request):
    form=LoginForm()
    if request.method == 'POST':
      form=LoginForm(data=request.POST)
      if form.is_valid():
         user=form.get_user()
         login(request,user)
         return redirect('dashboard')  
    return render(request, 'registration/login.html',{'form':form})
@login_required
def sign_out(request):
  if request.method == 'POST':
    logout(request)
  return redirect('sign-in')

def activate_user(request,user_id,token):
  try: 
      user= User.objects.get(id=user_id)
      if default_token_generator.check_token(user,token):
         user.is_active=True
         user.save()
         return redirect('sign-in')
      else:
        user.is_active=False
        return HttpResponse('Invalid ID or token')
  except User.DoesNotExist:
    return HttpResponse('User not found')
@user_passes_test(is_admin,login_url='no-permission')
def admin_dashboard(request):
    users=User.objects.prefetch_related(
      Prefetch('groups',queryset= Group.objects.all(),to_attr='all_groups')
      ).all()
    for user in users:
      if  user.all_groups:
          user.group_name=user.all_groups[0].name
      else:
        user.group_name='No Group Assigned' 
    return render(request, 'admin/admin_dashboard.html',{'users':users})

@user_passes_test(is_admin,login_url='no-permission')
def assign_role(request,user_id):
  user=User.objects.get(id=user_id)
  form=AssignRoleForm()
  if request.method == 'POST':
    form=AssignRoleForm(request.POST)
    if form.is_valid():
       role=form.cleaned_data.get('role')
       user.groups.clear() #remove the old roles
       user.groups.add(role)#add the new roles
       messages.success(request,f"User {user.username} has been assigned to {role.name} Role")
       return redirect('admin-dashboard')
  return render(request,'admin/assign_role.html',{'form':form})   

@user_passes_test(is_admin,login_url='no-permission')
def create_group(request):
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            group = form.save()  # Save the group
            group.permissions.set(form.cleaned_data['permissions'])  # Set the permissions
            messages.success(request, f'Group {group.name} has been created successfully!')
            return redirect('create-group')
    else:
        form = CreateGroupForm()
    
    return render(request, 'admin/create_group.html', {'form': form})
@user_passes_test(is_admin,login_url='no-permission')
def group_list(request):
  groups=Group.objects.prefetch_related('permissions').all()
  return render(request,'admin/group_list.html',{'groups':groups})

