from flask import Flask, request, session, render_template, flash, redirect, url_for
import datetime
from bs4 import BeautifulSoup
import re
from common import dbHandle

app = Flask(__name__, template_folder='template/')
app.secret_key = 'the random string'
app.permanent_session_lifetime = datetime.timedelta(days=1)
app.add_url_rule('/static/face_detection/models/<path:filename>', endpoint='models',
                 view_func=app.send_static_file)

@app.route('/')
@app.route('/home')
def home():
    if session.get('teacher_logged_in'):
        return redirect(url_for('teacher_dashboard'))
    elif session.get('student_logged_in'):
        return redirect(url_for('student_dashboard'))

    return render_template('home.html')


@app.route('/signin_teacher', methods=["POST", "GET"])
def teacher_signin():
    if session.get('teacher_logged_in'):
        return redirect(url_for('teacher_dashboard'))
    elif session.get('student_logged_in'):
        return "You are a student go back to student's Portal"
    if request.method == "POST":
        form_data = request.form.to_dict()
        print(form_data)
        email = form_data['email']
        passwd = form_data['pass']
        if passwd == '' and email == '':
            flash("Enter your Email and Password")
            return render_template('signin_teacher.html')
        elif email == '':
            flash("Enter your Email")
            return render_template('signin_teacher.html')
        elif passwd == '':
            flash("Enter your password")
            return render_template('signin_teacher.html')
        success = dbHandle.teacher_login(email, passwd)
        if success == -1:
            flash("email-id not found please register!")
        elif success == 1:
            session['teacher_id'], session['teacher_name'] = dbHandle.get_tid(email)
            session['teacher_logged_in'] = email
            return redirect(url_for('teacher_dashboard'))
        elif success == 0:
            flash("Password incorrect, Retry!")

    return render_template('signin_teacher.html')


@app.route('/dashboard_teacher', methods=["POST", "GET"])
def teacher_dashboard():
    if session.get('teacher_logged_in'):
        if request.method == "POST":
            form_data = request.form.to_dict()
            print(form_data)
            test_name = form_data['test_name']
            test_pass = form_data['test_pass']
            invig_pass = form_data['invig_pass']
            teacherid = session.get('teacher_id')
            if test_name == '':
                flash("Please enter your test name.")
                return render_template('dashboard_teacher.html')
            elif test_pass == '':
                flash("Please enter password for test.")
                return render_template('dashboard_teacher.html')
            elif invig_pass == '':
                flash("Please enter invigilator password")
                return render_template('dashboard_teacher.html')
            testid = "exproc"
            testid += str(dbHandle.test_creation(test_name, test_pass, invig_pass, teacherid))
            flash("Your generated testid is " + testid)
        test_details = dbHandle.fetch_test(session.get('teacher_id'))
        print(session.get('teacher_id'))
        return render_template('dashboard_teacher.html', len=len(test_details), test_details=test_details, email=session.get('teacher_logged_in'), name=session.get('teacher_name'))
    else:
        return redirect(url_for('teacher_signin'))
    # if request.method == "POST":
    #     form_data = request.form.to_dict()


@app.route('/signin_student', methods=["POST", "GET"])
def student_signin():
    if session.get('student_logged_in'):
        return redirect(url_for('student_dashboard'))
    elif session.get('teacher_logged_in'):
        return "You are a teacher go back to teacher's Portal"
    if request.method == "POST":
        form_data = request.form.to_dict()
        print(form_data)
        email = form_data['email']
        passwd = form_data['pass']
        if passwd == '' and email == '':
            flash("Enter your Email and Password")
            return render_template('signin_student.html')
        elif email == '':
            flash("Enter your Email")
            return render_template('signin_student.html')
        elif passwd == '':
            flash("Enter your password")
            return render_template('signin_student.html')
        success = dbHandle.student_login(email, passwd)
        if success == -1:
            flash("email-id not found please register!")
        elif success == 1:
            session['student_logged_in'] = email
            ids = dbHandle.get_sid(email)
            session['student_id'] = ids[0]
            session['username'] = ids[1]
            ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            print(ip, type(ip))
            session['this_ip'] = ip
            dbHandle.student_active_ip_update(email, ip)
            return redirect(url_for('student_dashboard'))
        elif success == 0:
            flash("Password incorrect, Retry!")
    return render_template('signin_student.html')


@app.route('/dashboard_student', methods=["POST", "GET"])
def student_dashboard():
    if session.get('student_logged_in'):
        if session['this_ip'] != dbHandle.fetch_student_active_ip(session['student_logged_in']):
            return redirect(url_for('student_signout'))
        if session.get('test_login_success'):
            return redirect(url_for('test_enter', test_id=session.get('test_login_success')))
        if request.method == "POST":
            form_data = request.form.to_dict()
            test_id = form_data['test_id']
            passwd = form_data['pass']
            uniqueid = str(test_id[5:]) + '.' + str(session.get('student_id'))
            if test_id == '':
                flash("Enter your Test id")
                return render_template('dashboard_student.html')
            elif passwd == '':
                flash("Enter the password given to you")
                return render_template('dashboard_student.html')
            if len(test_id) > 5 and test_id[0:5] == 'exproc':
                success = dbHandle.validate_test_login(test_id[5:], passwd)
            else:
                success = -1
            if success == 1:
                check = dbHandle.get_uniqueid(uniqueid)
                print(check)
                if check == 1:
                    flash("Test already taken!")
                    return redirect(url_for('student_dashboard'))
                session['test_login_success'] = test_id[5:]
                return redirect(url_for('test_enter', test_id=session.get('test_login_success')))
            elif success == -1:
                flash("No such test found")
            elif success == 0:
                flash("Incorrect password")
        return render_template('dashboard_student.html')
    else:
        return redirect(url_for('student_signin'))


@app.route('/signup_teacher', methods=["POST", "GET"])
def teacher_signup():
    if request.method == "POST":
        form_data = request.form.to_dict()
        name = form_data['name']
        passwd = form_data['pass']
        email = form_data['email']
        passwdchk = form_data['passcheck']
        inst_name = form_data['inst_name']
        phno = str(form_data['ph_no'])
        print(name, email, passwd, passwdchk, inst_name, phno)
        if name == '':
            flash("Please enter your name")
            return render_template('signup_teacher.html')
        elif inst_name == '':
            flash("Please enter inst_name")
            return render_template('signup_teacher.html')
        elif phno == '':
            flash("Please enter phno")
            return render_template('signup_teacher.html')
        elif passwd == '':
            flash("Please enter a password")
            return render_template('signup_teacher.html')
        elif passwdchk == '':
            flash("Please enter confirm password")
            return render_template('signup_teacher.html')
        elif passwd != passwdchk:
            flash("Password and confirm password do not match, Please re-enter")
            return render_template('signup_teacher.html')

        success = dbHandle.teacher_registration(name, email, inst_name, passwd, phno)
        if success == 0:
            flash("email or phone no. already exists, please login")
            return render_template('signup_teacher.html')
        elif success == 1:
            flash("Registration Successful, Please Login")
            return redirect(url_for('teacher_signin'))
    return render_template('signup_teacher.html')


@app.route('/signup_student', methods=["POST", "GET"])
def student_signup():
    if request.method == "POST":
        form_data = request.form.to_dict()
        name = form_data['name']
        passwd = form_data['pass']
        email = form_data['email']
        passwdchk = form_data['passcheck']
        inst_name = form_data['inst_name']
        phno = str(form_data['ph_no'])
        print(name, email, passwd, passwdchk, inst_name, phno)
        if name == '':
            flash("Please enter your name")
            return render_template('signup_student.html')
        elif inst_name == '':
            flash("Please enter inst_name")
            return render_template('signup_student.html')
        elif phno == '':
            flash("Please enter phno")
            return render_template('signup_student.html')
        elif passwd == '':
            flash("Please enter a password")
            return render_template('signup_student.html')
        elif passwdchk == '':
            flash("Please enter confirm password")
            return render_template('signup_student.html')
        elif passwd != passwdchk:
            flash("Password and confirm password do not match, Please re-enter")
            return render_template('signup_student.html')

        success = dbHandle.student_registration(name, email, inst_name, passwd, phno)
        if success == 0:
            flash("email or phone no. already exists, please login")
            return render_template('signup_student.html')
        elif success == 1:
            flash("Registration Successful, Please Login")
            return redirect(url_for('student_signin'))
    return render_template('signup_student.html')


@app.route('/signout_teacher', methods=["POST", "GET"])
def teacher_signout():
    if session.get('teacher_logged_in'):
        session.clear()
        return redirect(url_for('teacher_signin'))
    else:
        return redirect(url_for('teacher_signin'))


@app.route('/signout_student', methods=["POST", "GET"])
def student_signout():
    if session.get('student_logged_in'):
        session.clear()
        return redirect(url_for('student_signin'))
    else:
        return redirect(url_for('student_signin'))


@app.route('/dashboard_invigilator', methods=["POST", "GET"])
def invigilator_dashbaord():
    if (session.get('teacher_logged_in')):
        return render_template('dashboard_invigilator.html')
    else:
        return redirect(url_for('teacher_signup'))


@app.route('/edit_test/exproc<test_id>_<test_name>', methods=["POST", "GET"])
def test_edit(test_id, test_name):
    tid = dbHandle.get_teacherid(test_id)
    if session.get('teacher_logged_in') and tid == session.get('teacher_id'):
        test_details = dbHandle.get_test_details(test_id)
        if request.method == "POST":
            form_data = request.form.to_dict()
            date_time = form_data['date_time']
            date_time_dict = {'year': date_time[0:4], 'month': date_time[5:7], 'date': date_time[8:10],
                              'hour': date_time[11:13], 'min': date_time[14:16]}
            duration = form_data['duration']

            duration_dict = {'hour': duration[0:2], 'min': duration[3:5]}

            question_paper = form_data['noise']
            print(duration_dict, date_time_dict, question_paper)
            success = dbHandle.update_test_details(test_id, duration_dict, date_time_dict, question_paper)
            if success == 1:
                flash("Test details updated successfully")
                return redirect(url_for('teacher_dashboard'))
            elif success == 0:
                flash("Enter details properly")
                return render_template('edit_test.html', test_id=test_id, test_name=test_name, test_details=test_details, email=session.get('teacher_logged_in'), name=session.get('teacher_name'))
        return render_template('edit_test.html', test_id=test_id, test_name=test_name, test_details=test_details, email=session.get('teacher_logged_in'), name=session.get('teacher_name'))
    else:
        return redirect(url_for('teacher_signin'))


@app.route('/pre_test/exproc<test_id>_<date_time>_<test_dur>', methods=["POST", "GET"])
def test_pre(test_id,date_time,test_dur):
    if session.get('student_logged_in') and session.get('test_login_success') == test_id:

        if request.method == "POST":
            user_id = session.get('student_id')
            user_name = session.get('username')
            success = dbHandle.submit_test(user_id, user_name, test_id)
            if success == 1:
                return redirect(url_for('test_appear', test_id=session.get('test_login_success'),date_time=date_time,test_dur=test_dur))
            else:
                flash("Not allowed anymore!")
                session.pop('test_login_success', None)
                return redirect(url_for('student_dashboard'))
        return render_template('pre_test.html', test_id=session.get('test_login_success'),date_time=date_time,test_dur=test_dur)
    else:
        flash("Illegal access to test. Don't ever do that again otherwise we'll terminate your account!")
        session.pop('test_login_success', None)
        return redirect(url_for('student_dashboard'))


@app.route('/enter_test/exproc<test_id>', methods=["POST", "GET"])
def test_enter(test_id):
    if session.get('student_logged_in') and session.get('test_login_success') == test_id:
        time_details = dbHandle.get_time(test_id)
        if time_details[0] == 0 or time_details == -1:
            flash("You are too early or too late!")
            session.pop('test_login_success', None)
            return redirect(url_for('student_dashboard'))
        date_time = time_details[0]
        test_dur = time_details[1]
        if request.method == "POST":
            return redirect(url_for('test_pre', test_id=session.get('test_login_success'), date_time=date_time, test_dur=test_dur))
        return render_template('enter_test.html', test_id=session.get('test_login_success'), date_time=date_time, test_dur=test_dur)
    else:
        flash("Illegal access to test. Don't ever do that again otherwise we'll terminate your account!")
        session.pop('test_login_success', None)
        return redirect(url_for('student_dashboard'))


@app.route('/appear_test/exproc<test_id>_<date_time>_<test_dur>', methods=["POST", "GET"])
def test_appear(test_id, date_time, test_dur):
    if session.get('student_logged_in') and session.get('test_login_success') == test_id:
        if request.method == "POST":
            form_data = request.form.to_dict()
            if 'noise' in form_data:
                ans_paper = form_data['noise']
                roll_no = form_data['roll_no']
                user_id = session.get('student_id')
                success = dbHandle.update_test_submit(user_id, test_id, ans_paper, roll_no)
                if success == 1:
                    flash("Test is submitted! Thanks for taking test.")
                    session.pop('test_login_success', None)
                    return redirect(url_for('student_dashboard'))
                else:
                    flash("Test is already taken by you!")
                    session.pop('test_login_success', None)
                    return redirect(url_for('student_dashboard'))
            else:
                print("dgh1")
                user_id = session.get('student_id')
                print("dhg2")
                json = request.get_json()
                url = json['image_data_url']

                print(url)
                success=dbHandle.sendImage(url,test_id,user_id)


        test_details = dbHandle.get_test_details(test_id)
        question_paper = test_details[2]

        return render_template('appear_test.html', question_paper=question_paper, test_id=test_id, date_time=date_time, test_dur=test_dur)
    else:
        flash("Illegal access to test. Don't ever do that again otherwise we'll terminate your account!")
        return redirect(url_for('student_dashboard'))


@app.route('/test_remove/remove<test_id> ', methods=["POST", "GET"])
def remove_test(test_id):

    tid = dbHandle.get_teacherid(test_id)
    if session.get('teacher_logged_in') and tid == session.get('teacher_id'):
        dbHandle.delete_test(test_id)
        return redirect(url_for('teacher_dashboard'))
    else:
        return redirect(url_for('teacher_signin'))


@app.route('/test_evaluate', methods=["POST", "GET"])
def evaluate_test():

    if session.get('teacher_logged_in'):
        test_details = dbHandle.fetch_test(session.get('teacher_id'))
        return render_template('test_evaluate.html', len=len(test_details), test_details=test_details, email=session.get('teacher_logged_in'), name=session.get('teacher_name'))
    else:
        return redirect(url_for('teacher_signin'))


@app.route('/view_submissions/exproc<test_id> ', methods=["POST", "GET"])
def submission_view(test_id):

    tid = dbHandle.get_teacherid(test_id)
    if session.get('teacher_logged_in') and tid == session.get('teacher_id'):
        submissions = dbHandle.paper_evaluation(test_id)
        print(submissions)
        return render_template('view_submissions.html', len=len(submissions), submissions=submissions, email=session.get('teacher_logged_in'), name=session.get('teacher_name'))
    else:
        return redirect(url_for('teacher_signin'))


@app.route('/view_ans_script/<unique_id>', methods=["POST", "GET"])
def view_ans_script(unique_id):
    if session.get('teacher_logged_in'):
        if request.method=="POST":
            form_data=request.form.to_dict();
            score=form_data['score']
            success=dbHandle.submit_score(score,unique_id)
            if(success==1):
                flash("score updated successfully")
            return redirect(url_for('teacher_dashboard'))
        else:
            data = dbHandle.get_ans_script(unique_id)
            print(data,unique_id)
            tid = dbHandle.get_teacherid(str(data[1]))
            fetched_images = dbHandle.fetchImages(unique_id)
            print(tid)
            if tid == session.get('teacher_id'):
                return render_template('view_ans_script.html', data=data, email=session.get('teacher_logged_in'), name=session.get('teacher_name'), fetched_images=fetched_images, len=len(fetched_images))
            flash("You can't access that data")
            return redirect(url_for('teacher_dashboard'))
    else:
        return redirect(url_for('teacher_signin'))

@app.route('/view_tests', methods=["POST", "GET"])
def view_attempted_test():
    if session.get('student_logged_in'):
        user_id = session.get('student_id')
        submissions = dbHandle.view_tests(user_id)
        print(submissions)
        return render_template('view_attempted_tests.html', len=len(submissions), submissions=submissions, email=session.get('student_logged_in'))
    else:
        return redirect(url_for('student_signin'))
if __name__ == "__main__":
    app.run(debug="true")