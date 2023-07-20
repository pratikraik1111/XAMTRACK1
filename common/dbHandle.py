import mysql.connector
import bcrypt
from datetime import datetime, timedelta

def connect():
    try:
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Pratik@123',
            database='xamdata',
        )
    except:
        connect()
    return mydb

def student_registration(name: str, email: str, inst_name: str, passwd: str, phno: str):
    mydb = connect()
    mycursor = mydb.cursor()
    hassedPasswd = bcrypt.hashpw(passwd.encode("utf-8"), bcrypt.gensalt())
    try:
        insertFn = "INSERT INTO student_info (name,email,pass,inst_name,phno) VALUES (%s, %s, %s, %s,%s)"
        registration_info = (name, email, hassedPasswd, inst_name, phno)
        mycursor.execute(insertFn, registration_info)
        mydb.commit()
        return 1
    except:
        return 0  # email exists


def teacher_registration(name: str, email: str, inst_name: str, passwd: str, phno: str):
    mydb = connect()
    mycursor = mydb.cursor()
    hassedPasswd = bcrypt.hashpw(passwd.encode("utf-8"), bcrypt.gensalt())
    try:
        insertFn = "INSERT INTO teacher_info (name,email,pass,inst_name,phno) VALUES (%s, %s, %s, %s, %s)"
        registration_info = (name, email, hassedPasswd, inst_name, phno)
        mycursor.execute(insertFn, registration_info)
        mydb.commit()
        return 1
    except:
        return 0


def student_active_ip_update(email: str, ip):
    mydb = connect()
    mycursor = mydb.cursor()
    try:
        mycursor.execute("UPDATE student_info SET active_ip = \"" + ip + "\"  where email = \"" + email + "\"")
        mydb.commit()
        return 1
    except:
        return 0


def fetch_student_active_ip(email: str):
    mydb = connect()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT active_ip from student_info where email = \"" + email + "\"")
    fetched_list = mycursor.fetchall()
    if (len(fetched_list) == 0):
        return 1
    else:
        return fetched_list[0][0]


def student_login(emailid: str, passwd: str):
    mydb = connect()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT pass from student_info where email = \"" + emailid + "\"")
    fetched_list = mycursor.fetchall()
    if (len(fetched_list) == 0):
        return -1  # email id not found

    else:
        hassedPasswd = fetched_list[0][0]
        if bcrypt.checkpw(passwd.encode("utf-8"), hassedPasswd.encode("utf-8")):
            return 1  # login success
        else:
            return 0  # incorrect password


def teacher_login(emailid: str, passwd: str):
    mydb = connect()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT pass from teacher_info where email = \"" + emailid + "\"")
    fetched_list = mycursor.fetchall()
    if len(fetched_list) == 0:
        return -1  # email id not found

    else:
        hassedPasswd = fetched_list[0][0]
        print(str(hassedPasswd))
        if bcrypt.checkpw(passwd.encode("utf-8"), hassedPasswd.encode("utf-8")):
            return 1  # login success
        else:
            return 0  # incorrect password


def validate_test_login(test_id: str, passwd: str):
    mydb = connect()
    mycursor = mydb.cursor()
    try:
        mycursor.execute("SELECT testpass from test_create where test_id = " + test_id)
        fetched_list = mycursor.fetchall()
        if len(fetched_list) == 0:
            return -1  # no such test avail
        else:
            hassedPasswd = fetched_list[0][0]
            if bcrypt.checkpw(passwd.encode("utf-8"), hassedPasswd.encode("utf-8")):
                return 1  # login success
            else:
                return 0  # incorrect password
    except:
        return -1


def test_creation(testname: str, testpass: str, invigpass: str, teacherid: int):
    mydb = connect()
    mycursor = mydb.cursor()
    hassedtestpass = bcrypt.hashpw(testpass.encode("utf-8"), bcrypt.gensalt())
    hassedinvigpass = bcrypt.hashpw(invigpass.encode("utf-8"), bcrypt.gensalt())
    try:
        insertFn = "INSERT INTO test_create (testname,testpass,invigpass,teacherid) VALUES (%s, %s, %s, %s)"
        test_creation_info = (testname, hassedtestpass, hassedinvigpass, teacherid)
        mycursor.execute(insertFn, test_creation_info)
        mydb.commit()
        mycursor.execute("SELECT test_id from test_create where teacherid = " + str(teacherid))
        fetched_list = mycursor.fetchall()
        ids = fetched_list[len(fetched_list) - 1][0]
        return ids
    except:
        return 0


def get_tid(email: str):
    mydb = connect()
    mycursor = mydb.cursor()

    try:
        mycursor.execute("SELECT userid,name from teacher_info where email = \"" + email + "\"")
        fetched_list = mycursor.fetchall()
        tid, tname = fetched_list[0][0], fetched_list[0][1]
        return tid, tname
    except:
        return 0


def get_sid(email: str):
    mydb = connect()
    mycursor = mydb.cursor()

    try:
        mycursor.execute("SELECT userid,name from student_info where email=\"" + email + "\"")
        fetched_list = mycursor.fetchall()
        sid = fetched_list[0]
        return sid
    except:
        return 0


def fetch_test(teacher_id: int):
    mydb = connect()
    mycursor = mydb.cursor()

    try:
        mycursor.execute("SELECT test_id, testname from test_create where teacherid = " + str(teacher_id))
        fetched_list = mycursor.fetchall()
        ids = fetched_list
        return ids
    except:
        return 0


# def update_test_details(test_id, duration, date_time, question_paper):
#     mydb = connect()
#     mycursor = mydb.cursor()
#     try:
#         mycursor.execute("UPDATE test_create SET testdur = \'" + duration['hour'] + ":" + duration['min'] + "\', "
#                                  "date_time =  str_to_date(\"" + date_time['year'] + "-" + date_time['month'] + "-" + date_time['date'] + " " + date_time['hour'] + ":" + date_time['min'] +":00\", \"%Y-%m-%d %H:%i:%s\"), testpaper=\""+question_paper+"\" where testid = " + str(test_id))
#         mydb.commit()
#         return 1
#     except:
#         return 0


def update_test_details(test_id, duration, date_time, question_paper):
    mydb = connect()
    mycursor = mydb.cursor()
    count=0
    try:
        mycursor.execute("UPDATE test_create SET testdur = \'" + duration['hour'] + ":" + duration['min'] + "\' where test_id = " + str(test_id))
        mydb.commit()
        count += 1
    except:
        pass
    try:
        mycursor.execute("UPDATE test_create SET date_time =  str_to_date(\"" + date_time['year'] + "-" + date_time['month'] + "-" + date_time['date'] + " " + date_time['hour'] + ":" + date_time['min'] +":00\", \"%Y-%m-%d %H:%i:%s\") where test_id = " + str(test_id))
        mydb.commit()
        count += 1
    except:
        pass
    try:
        mycursor.execute("UPDATE test_create SET testpaper=\""+question_paper+"\" where test_id = " + str(test_id))
        mydb.commit()
        return 1
    except:
        if count >= 1:
            return 1
        else:
            return 0


def get_test_details(test_id):
    mydb = connect()
    mycursor = mydb.cursor()

    try:
        mycursor.execute("SELECT testdur,date_time, testpaper, testname from test_create where test_id = " + str(test_id))
        fetched_list = mycursor.fetchall()
        return fetched_list[0]
    except:
        return 0


def submit_test(userid, username, testid):
    mydb = connect()
    mycursor = mydb.cursor()

    try:
        uniqueid = testid+'.'+str(userid)
        insertFn = "INSERT INTO test_student (uniqueid,username,userid, testid) VALUES (%s,%s,%s, %s)"
        test_submit_info = (uniqueid, username, userid, testid)
        mycursor.execute(insertFn, test_submit_info)
        mydb.commit()
        return 1
    except :
        return 0

def update_test_submit(user_id, test_id, ans_paper, roll_no):
    mydb = connect()
    mycursor = mydb.cursor()
    count = 0
    try:
        uniqueid = test_id + '.' + str(user_id)
        mycursor.execute("UPDATE test_student SET ans_paper = \""+ans_paper+"\" where uniqueid = \""+uniqueid+"\"")
        mydb.commit()
        count += 1
    except:
        pass
    try:
        uniqueid = test_id + '.' + str(user_id)
        mycursor.execute("UPDATE test_student SET rollno = \""+roll_no+"\" where uniqueid = \""+uniqueid+"\"")
        mydb.commit()
        return 1
    except:
        if count >= 1:
            return 1
        return 0


def get_uniqueid(uniqueid:str):
    mydb=connect()
    mycursor= mydb.cursor()

    try:
        mycursor.execute("SELECT userid from test_student where uniqueid = " + uniqueid)

        fetched_list = mycursor.fetchall()
        if len(fetched_list) == 0:
            return 2

        return 1
    except:
        return 0


def get_teacherid(test_id):
    mydb= connect()
    mycursor= mydb.cursor()

    try:
        mycursor.execute("SELECT teacherid from test_create where test_id="+test_id)
        fetched_list = mycursor.fetchall()
        return fetched_list[0][0]
    except:
        return -1


def delete_test(test_id):
    mydb = connect()
    mycursor = mydb.cursor()

    try:
        mycursor.execute("DELETE FROM test_create where test_id="+test_id)
        mydb.commit()
        return 1
    except:
        return -1


def paper_evaluation(test_id):
    mydb = connect()
    mycursor = mydb.cursor()

    try:
        mycursor.execute("SELECT * FROM test_student where testid=" + str(test_id))
        fetched_list = mycursor.fetchall()
        return fetched_list
    except:
        return 0


def get_ans_script(unique_id):
    mydb = connect()
    mycursor = mydb.cursor()

    try:
        mycursor.execute("SELECT * FROM test_student where uniqueid=\"" + str(unique_id)+"\"")
        fetched_list = mycursor.fetchall()
        return fetched_list[0]
    except:
        return 0


def get_time(test_id):
    mydb=connect()
    mycursor=mydb.cursor()
    try:
        mycursor.execute("SELECT date_time,testdur from test_create where test_id="+test_id)
        fetchedlist = mycursor.fetchall()
        date_time = fetchedlist[0][0]
        end_time = date_time + timedelta(minutes=30)
        start_time = date_time - timedelta(minutes=30)
        mydb.commit()
        utc_dt = datetime.utcnow()
        now = utc_dt + timedelta(hours=5, minutes=30)
        if start_time <= now <= end_time:
            return fetchedlist[0]
        else:
            list = [0, 0]
            return list
    except:
        list = [0, 0]
        return list

def submit_score(score,uniqueid):
    mydb = connect()
    mycursor = mydb.cursor()

    try:
        mycursor.execute("UPDATE test_student SET eval_marks = \"" + score + "\" where uniqueid = \"" + uniqueid + "\"")
        mydb.commit()
        return 1
    except :
        return 0


def view_tests(user_id):
    mydb = connect()
    mycursor = mydb.cursor()

    try:
        mycursor.execute("SELECT * FROM test_student where userid=" + str(user_id))
        fetched_list = mycursor.fetchall()
        return fetched_list
    except:
        return 0



def sendImage(url,testid,userid):
    mydb = connect()
    mycursor = mydb.cursor()
    uniqueid = str(testid)+'.'+str(userid)
    insertFn = "INSERT INTO malpractice_images (unique_id,url) VALUES (%s,%s)"
    test_submit_info = (uniqueid, url)
    mycursor.execute(insertFn, test_submit_info)
    mydb.commit()
    return 1

def fetchImages(uniqueid):
    mydb = connect()
    mycursor = mydb.cursor()

    mycursor.execute("SELECT url from malpractice_images where unique_id=" + uniqueid)
    fetchedlist = mycursor.fetchall()



    return fetchedlist


#print(fetchImages("51.6")[2][0])