from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage  # To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json
from datetime import *  

from student_management_app.models import CustomUser, RoomArea, Staffs, Courses, Subjects, Students, SessionYearModel, FeedBackStudent, FeedBackStaffs
from .forms import AddStudentForm, EditStudentForm


def admin_home(request):
    all_student_count = Students.objects.all().count()
    subject_count = Subjects.objects.all().count()
    course_count = Courses.objects.all().count()
    staff_count = Staffs.objects.all().count()

    # Total Subjects and students in Each Course
    course_all = Courses.objects.all()
    course_name_list = []
    subject_count_list = []
    student_count_list_in_course = []

    for course in course_all:
        subjects = Subjects.objects.filter(course_id=course.id).count()
        students = Students.objects.filter(course_id=course.id).count()
        course_name_list.append(course.course_name)
        subject_count_list.append(subjects)
        student_count_list_in_course.append(students)

    subject_all = Subjects.objects.all()
    subject_list = []
    student_count_list_in_subject = []
    for subject in subject_all:
        course = Courses.objects.get(id=subject.course_id.id)
        student_count = Students.objects.filter(course_id=course.id).count()
        subject_list.append(subject.subject_name)
        student_count_list_in_subject.append(student_count)

    # For Saffs
    staff_attendance_present_list = []
    staff_attendance_leave_list = []
    staff_name_list = []

    staffs = Staffs.objects.all()
    for staff in staffs:
        subject_ids = Subjects.objects.filter(staff_id=staff.admin.id)
        staff_name_list.append(staff.admin.first_name)

    # For Students
    student_attendance_present_list = []
    student_attendance_leave_list = []
    student_name_list = []

    students = Students.objects.all()
    for student in students:
        student_name_list.append(student.admin.first_name)

    context = {
        "all_student_count": all_student_count,
        "subject_count": subject_count,
        "course_count": course_count,
        "staff_count": staff_count,
        "course_name_list": course_name_list,
        "subject_count_list": subject_count_list,
        "student_count_list_in_course": student_count_list_in_course,
        "subject_list": subject_list,
        "student_count_list_in_subject": student_count_list_in_subject,
        "staff_attendance_present_list": staff_attendance_present_list,
        "staff_attendance_leave_list": staff_attendance_leave_list,
        "staff_name_list": staff_name_list,
        "student_attendance_present_list": student_attendance_present_list,
        "student_attendance_leave_list": student_attendance_leave_list,
        "student_name_list": student_name_list,
    }
    return render(request, "hod_template/home_content.html", context)


def add_staff(request):
    return render(request, "hod_template/add_staff_template.html")


def add_staff_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('add_staff')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            user = CustomUser.objects.create_user(
                username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=2)
            user.staffs.address = address
            user.save()
            messages.success(request, "Staff Added Successfully!")
            return redirect('manage_staff')
        except:
            messages.error(request, "Failed to Add Staff!")
            return redirect('add_staff')


def manage_staff(request):
    staffs = Staffs.objects.all()
    # staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "staffs": staffs
    }
    return render(request, "hod_template/manage_staff_template.html", context)


def edit_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)

    context = {
        "staff": staff,
        "id": staff_id
    }
    return render(request, "hod_template/edit_staff_template.html", context)


def edit_staff_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        staff_id = request.POST.get('staff_id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')

        try:

            # INSERTING into Customuser Model
            user = CustomUser.objects.get(id=staff_id)
            user_email = CustomUser.objects.filter(
                email=email).values_list('id', flat=True)

            for u in user_email:
                if str(u) != staff_id:
                    raise Exception("Email invalid!")
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            # user.staff.address = address
            user.save()

            # INSERTING into Staff Model
            staff_model = Staffs.objects.get(admin=staff_id)
            staff_model.address = address
            staff_model.save()

            messages.success(request, "Staff Updated Successfully.")
            return redirect('/manage_staff/')

        except:
            messages.error(request, "Failed to Update Staff.")
            return redirect('/edit_staff/'+staff_id)


def delete_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    staff_account = CustomUser.objects.get(id=staff_id)
    try:
        staff.delete()
        staff_account.delete()
        messages.success(request, "Staff Deleted Successfully.")
        return redirect('manage_staff')
    except:
        messages.error(request, "Failed to Delete Staff.")
        return redirect('manage_staff')


def add_course(request):
    return render(request, "hod_template/add_course_template.html")


def add_course_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('add_course')
    else:
        course = request.POST.get('course')
        try:
            if (course == ""):
                raise Exception("Pls fill all information")
            if Courses.objects.filter(course_name=course):
                raise Exception("Course is already existed!")
            course_model = Courses(course_name=course)
            course_model.save()
            messages.success(request, "Course Added Successfully!")
            return redirect('manage_course')
        except:
            messages.error(request, "Failed to Add Course!")
            return redirect('add_course')


def manage_course(request):
    courses = Courses.objects.all()
    context = {
        "courses": courses
    }
    return render(request, 'hod_template/manage_course_template.html', context)


def edit_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    context = {
        "course": course,
        "id": course_id
    }
    return render(request, 'hod_template/edit_course_template.html', context)


def edit_course_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        course_id = request.POST.get('course_id')
        course_name = request.POST.get('course')
        try:
            if (course_name == ""):
                raise Exception("Pls fill all information")
            if Courses.objects.filter(course_name=course_name):
                raise Exception("Course is already existed!")
            course = Courses.objects.get(id=course_id)
            course.course_name = course_name
            course.save()

            messages.success(request, "Course Updated Successfully.")
            return redirect('manage_course')

        except:
            messages.error(request, "Failed to Update Course.")
            return redirect('/edit_course/'+course_id)


def delete_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    try:
        course.delete()
        messages.success(request, "Course Deleted Successfully.")
        return redirect('manage_course')
    except:
        messages.error(request, "Failed to Delete Course.")
        return redirect('manage_course')


def manage_session(request):
    session_years = SessionYearModel.objects.all()
    context = {
        "session_years": session_years
    }
    return render(request, "hod_template/manage_session_template.html", context)


def add_session(request):
    return render(request, "hod_template/add_session_template.html")


def add_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_course')
    else:
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')

        try:
            x = session_start_year.split('-')
            print(x)
            b1 = date(int(x[0]), int(x[1]), int(x[2]))

            y = session_end_year.split('-')
  
            b2 = date(int(y[0]), int(y[1]), int(y[2]))
  
            if b1 < b2:
                sessionyear = SessionYearModel(
                session_start_year=session_start_year, session_end_year=session_end_year)
                sessionyear.save()
                messages.success(request, "Session Year added Successfully!")
                return redirect("manage_session")
    
            else:
                messages.error(request, "Failed to Add Session Year")
                return redirect("add_session")

            
        except:
            messages.error(request, "Failed to Add Session Year")
            return redirect("add_session")


def edit_session(request, session_id):
    session_year = SessionYearModel.objects.get(id=session_id)
    context = {
        "session_year": session_year
    }
    return render(request, "hod_template/edit_session_template.html", context)


def edit_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('manage_session')
    else:
        session_id = request.POST.get('session_id')
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')

        try:
            x = session_start_year.split('-')
            print(x)
            b1 = date(int(x[0]), int(x[1]), int(x[2]))

            y = session_end_year.split('-')
  
            b2 = date(int(y[0]), int(y[1]), int(y[2]))
  
            if b1 < b2:
                session_year = SessionYearModel.objects.get(id=session_id)
                session_year.session_start_year = session_start_year
                session_year.session_end_year = session_end_year
                session_year.save()

                messages.success(request, "Session Year Updated Successfully.")
                return redirect("manage_session")
            else:
                messages.error(request, "Failed to Add Session Year")
                return redirect('/edit_session/'+session_id)

        except:
            messages.error(request, "Failed to Update Session Year.")
            return redirect('/edit_session/'+session_id)


def delete_session(request, session_id):
    session = SessionYearModel.objects.get(id=session_id)
    try:
        session.delete()
        messages.success(request, "Session Deleted Successfully.")
        return redirect('manage_session')
    except:
        messages.error(request, "Failed to Delete Session.")
        return redirect('manage_session')


def add_student(request):
    form = AddStudentForm()
    context = {
        "form": form
    }
    return render(request, 'hod_template/add_student_template.html', context)


def add_student_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_student')
    else:
        form = AddStudentForm(request.POST, request.FILES)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            address = form.cleaned_data['address']
            session_year_id = form.cleaned_data['session_year_id']
            course_id = form.cleaned_data['course_id']
            gender = form.cleaned_data['gender']

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                user_email = CustomUser.objects.filter(email=email).values_list('id', flat=True)
                if user_email:
                    raise Exception("Email invalid!")
                user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=3)
                user.students.address = address
                user.students.course_id = course_id
                user.students.session_year_id = session_year_id
                user.students.gender = gender
                user.students.profile_pic = profile_pic_url
                user.save()
                messages.success(request, "Student Added Successfully!")
                return redirect('manage_student')
            except:
                messages.error(request, "Failed to Add Student!")
                return redirect('add_student')
        else:
            return redirect('add_student')


def manage_student(request):
    students = Students.objects.all()
    context = {
        "students": students
    }
    return render(request, 'hod_template/manage_student_template.html', context)


def edit_student(request, student_id):
    # Adding Student ID into Session Variable
    request.session['student_id'] = student_id

    student = Students.objects.get(admin=student_id)
    form = EditStudentForm()
    # Filling the form with Data from Database
    form.fields['email'].initial = student.admin.email
    form.fields['username'].initial = student.admin.username
    form.fields['first_name'].initial = student.admin.first_name
    form.fields['last_name'].initial = student.admin.last_name
    form.fields['address'].initial = student.address
    form.fields['course_id'].initial = student.course_id
    form.fields['gender'].initial = student.gender
    form.fields['session_year_id'].initial = student.session_year_id

    context = {
        "id": student_id,
        "username": student.admin.username,
        "email": student.admin.email,
        "form": form
    }
    return render(request, "hod_template/edit_student_template.html", context)


def edit_student_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid Method!")
    else:
        student_id = request.session.get('student_id')
        if student_id == None:
            return redirect('/manage_student')

        form = EditStudentForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            course_id = form.cleaned_data['course_id']
            gender = form.cleaned_data['gender']
            session_year_id = form.cleaned_data['session_year_id']

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                # First Update into Custom User Model
                user = CustomUser.objects.get(id=student_id)
                user_email = CustomUser.objects.filter(
                    email=email).values_list('id', flat=True)
                for u in user_email:
                    if str(u) != student_id:
                        raise Exception("Email invalid!")
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.username = username
                user.save()

                # Then Update Students Table
                student_model = Students.objects.get(admin=student_id)
                student_model.address = address
                student_model.course_id = course_id
                student_model.session_year_id = session_year_id

                student_model.gender = gender
                if profile_pic_url != None:
                    student_model.profile_pic = profile_pic_url
                student_model.save()
                # Delete student_id SESSION after the data is updated
                del request.session['student_id']

                messages.success(request, "Student Updated Successfully!")
                return redirect('manage_student')
            except:
                messages.success(request, "Failed to Update Student.")
                return redirect('/edit_student/'+student_id)
        else:
            return redirect('/edit_student/'+student_id)


def delete_student(request, student_id):
    student = Students.objects.get(admin=student_id)
    student_account = CustomUser.objects.get(id=student_id)
    try:
        student.delete()
        student_account.delete()
        messages.success(request, "Student Deleted Successfully.")
        return redirect('manage_student')
    except:
        messages.error(request, "Failed to Delete Student.")
        return redirect('manage_student')


def add_subject(request):
    courses = Courses.objects.all()
    room_areas = RoomArea.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "courses": courses,
        "staffs": staffs,
        "room_areas": room_areas
    }
    return render(request, 'hod_template/add_subject_template.html', context)


def add_subject_save(request):
    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('add_subject')
    else:
        subject_name = request.POST.get('subject')

        course_id = request.POST.get('course')
        course = Courses.objects.get(id=course_id)

        date = request.POST.get('date')
        time = request.POST.get('time')
        staff_id = request.POST.get('staff')
        staff = CustomUser.objects.get(id=staff_id)

        room_area_id = request.POST.get('roomarea')
        room_area = RoomArea.objects.get(id=room_area_id)

        try:
            existed_subject = Subjects.objects.filter(date=date, time=time)
            if existed_subject:
                for s in existed_subject:
                    if s.staff_id == staff or s.room_area_name_id == room_area :
                        raise Exception("Subject invalid")
            subject = Subjects(subject_name=subject_name, course_id=course,
                               staff_id=staff, room_area_name_id=room_area, time=time, date=date)
            subject.save()
            messages.success(request, "Subject Added Successfully!")
            return redirect('manage_subject')
        except:
            messages.error(request, "Failed to Add Subject!")
            return redirect('add_subject')


def manage_subject(request):
    subjects = Subjects.objects.all()
    context = {
        "subjects": subjects
    }
    return render(request, 'hod_template/manage_subject_template.html', context)


def edit_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    courses = Courses.objects.all()
    room_areas = RoomArea.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "subject": subject,
        "courses": courses,
        "staffs": staffs,
        "id": subject_id,
        "room_areas": room_areas
    }
    return render(request, 'hod_template/edit_subject_template.html', context)


def edit_subject_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method.")
    else:
        subject_id = request.POST.get('subject_id')
        subject_name = request.POST.get('subject')
        course_id = request.POST.get('course')
        room_area_id = request.POST.get('roomarea')
        staff_id = request.POST.get('staff')

        try:
            subject = Subjects.objects.get(id=subject_id)
            subject.subject_name = subject_name
            existed_subject = Subjects.objects.filter(date=subject.date, time=subject.time)
            if existed_subject:
                for s in existed_subject:
                    if str(s.id) != subject_id:
                        if s.staff_id == CustomUser.objects.get(id=staff_id) or s.room_area_name_id == RoomArea.objects.get(id=room_area_id) :
                            raise Exception("Subject invalid")

            course = Courses.objects.get(id=course_id)
            subject.course_id = course

            staff = CustomUser.objects.get(id=staff_id)
            subject.staff_id = staff

            rome_area = RoomArea.objects.get(id=room_area_id)
            subject.room_area_id = rome_area

            subject.save()

            messages.success(request, "Subject Updated Successfully.")
            return redirect('/manage_subject')
            # return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id": subject_id}))

        except:
            messages.error(request, "Failed to Update Subject.")
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id": subject_id}))
            # return redirect('/edit_subject/'+subject_id)


def delete_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    try:
        subject.delete()
        messages.success(request, "Subject Deleted Successfully.")
        return redirect('manage_subject')
    except:
        messages.error(request, "Failed to Delete Subject.")
        return redirect('manage_subject')


@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


def student_feedback_message(request):
    feedbacks = FeedBackStudent.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/student_feedback_template.html', context)


@csrf_exempt
def student_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackStudent.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def staff_feedback_message(request):
    feedbacks = FeedBackStaffs.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/staff_feedback_template.html', context)


@csrf_exempt
def staff_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackStaffs.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)

    context = {
        "user": user
    }
    return render(request, 'hod_template/admin_profile.html', context)


def admin_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('admin_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect('/admin_home')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('admin_profile')


def staff_profile(request):
    pass


def student_profile(requtest):
    pass


def manage_room_area(request):
    room_areas = RoomArea.objects.all()
    context = {
        "room_areas": room_areas
    }
    return render(request, "hod_template/manage_room_area_template.html", context)


def add_room_area(request):
    return render(request, "hod_template/add_room_area_template.html")


def add_room_area_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_room_area')
    else:
        room_area_name = request.POST.get('room_area_name')
        try:
            if RoomArea.objects.filter(room_area_name=room_area_name):
                raise Exception("Room is already existed!")
            roomarea = RoomArea(room_area_name=room_area_name)
            roomarea.save()
            messages.success(request, "Room Area added Successfully!")
            return redirect("manage_room_area")
        except:
            messages.error(request, "Failed to Add Room Area")
            return redirect("add_room_area")


def edit_room_area(request, room_area_id):
    room_area = RoomArea.objects.get(id=room_area_id)
    context = {
        "room_area": room_area
    }
    return render(request, "hod_template/edit_room_area_template.html", context)


def edit_room_area_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('manage_room_area')
    else:
        room_area_id = request.POST.get('room_area_id')
        room_area_name = request.POST.get('room_area_name')

        try:
            rooms = RoomArea.objects.filter(room_area_name=room_area_name)
            for room in rooms:
                if str(room.id) != room_area_id:
                    raise Exception("Room is already existed!")
            room_area = RoomArea.objects.get(id=room_area_id)
            room_area.room_area_name = room_area_name
            room_area.save()

            messages.success(request, "Room Area Updated Successfully.")
            return redirect('manage_room_area')
        except:
            messages.error(request, "Failed to Update Room Area.")
            return redirect('/edit_room_area/'+room_area_id)


def delete_room_area(request, room_area_id):
    room_areas = RoomArea.objects.get(id=room_area_id)
    try:
        room_areas.delete()
        messages.success(request, "Room Area Deleted Successfully.")
        return redirect('manage_room_area')
    except:
        messages.error(request, "Failed to Delete Room Area.")
        return redirect('manage_room_area')
