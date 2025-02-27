import mysql.connector
import random
from faker import Faker
import sys

# Ensure the result of randomizations is always the same
seed = 1510
random.seed(seed)
Faker.seed(seed) 
fake = Faker()

cnx = mysql.connector.connect(
    host='localhost',
	user='root',
	password='password',
	database='myschedule',
	port=3306
)
cursor = cnx.cursor()

def make_insert_student(student_id):
    first, last = fake.first_name(), fake.last_name()
    program, faculty = random.choice(
        seq=[
            ('Accounting and Financial Management', 'Arts'), ('Actuarial Science', 'Mathematics'), ('Anthropology', 'Arts'), ('Applied Mathematics', 'Mathematics'), ('Architectural Engineering', 'Engineering'), ('Architecture', 'Engineering'),  ('Biochemistry', 'Science'), ('Biological and Medical Physics', 'Science'), ('Biology', 'Science'), ('Biomedical Engineering', 'Engineering'), ('Chemical Engineering', 'Engineering'), ('Chemistry', 'Science'), ('Civil Engineering', 'Engineering'), ('Classical Studies', 'Arts'), ('Climate and Environmental Change', 'Environment'), ('Cognitive Science', 'Arts'), ('Computational Mathematics', 'Mathematics'), 
        ]
    )
    pwd = first + last
    # This can never fail, so we can safely add it to prod_data_insert.sql
    return "insert into student values({}, '{}', '{}', '{}', '{}', '{}');".format(student_id, first[:25], last[:25], program, faculty, pwd.lower()[:20])
    
def make_friendships(friendships, start_sid, end_sid):
    for frienderid in range(start_sid, end_sid):
        num_friends = random.randint(0, 10)
        # Sample without duplicates
        friends = random.sample(range(start_sid, end_sid), k=num_friends)
        for friendeeid in friends:
            # Protect these statements from failing
            if (frienderid != friendeeid):
                friendships.append((frienderid, friendeeid))

def make_likes(likes, csub, cnum, start_sid, end_sid):
    # random.randint() follows a uniform distribution
    # Make high values of likes a rarer occurence by adjusting the mean like count to be close to 0
    num_likers = random.randint(-100, 100)
    if num_likers > 0:
        # Sample without duplicates
        likers = random.sample(range(start_sid, end_sid), k=num_likers)
        for sid in likers:
            # Protect these statements from failing
            likes.append((sid, csub, cnum)) 

def make_insert_attends(student_id, component_id):
    return "insert into attends values({}, {});".format(student_id, component_id)


# Create the students
print('use myschedule;')

START_STUDENT_ID = 10000001
# The first 5 students were generated manually (sample data)
student_id = START_STUDENT_ID + 5
for i in range(10000):
    query = make_insert_student(student_id) 
    cursor.execute(query)
    print(query)
    student_id += 1
END_STUDENT_ID = student_id

print('\n')

# Create the friendships among students
friendships = []
make_friendships(friendships, START_STUDENT_ID, END_STUDENT_ID)

# Enroll students in classes
query = 'SELECT id, enrollTot FROM component'
cursor.execute(query)
results = cursor.fetchall()

enrollments = []
for row in results:
    cid, enrollTot = row
    successfulInserts = 0
    attempts = 0
     # We should insert enrollTot students   
    while successfulInserts < enrollTot:  
        attempts += 1   
        # If (# attemps so far == # students), generate more students to improve the success rate
        # This is a randomized algorithm
        if attempts > END_STUDENT_ID - START_STUDENT_ID:
            old_end = END_STUDENT_ID
            END_STUDENT_ID += 5000
            for id in range(old_end, END_STUDENT_ID):
                insert_student = make_insert_student(id)
                cursor.execute(insert_student)
                print(insert_student)
            make_friendships(friendships, old_end, END_STUDENT_ID)
            print("stderr: student count is now {}, enrollments so far is {}".format(END_STUDENT_ID - START_STUDENT_ID, len(enrollments)), file=sys.stderr)

        # Attempt the insert on a random student
        # This will fail if the added component interferes with an existing component of the student's schedule
        sid = random.randint(START_STUDENT_ID, END_STUDENT_ID)
        query = make_insert_attends(sid, cid)
        try:
            cursor.execute(query)
            enrollments.append((sid, cid))
            successfulInserts += 1
        except mysql.connector.Error as err:
            pass


# Generate likes relations
query = 'SELECT DISTINCT csub, cnum FROM course'
cursor.execute(query)
results = cursor.fetchall()
likes = []
for row in results:
    csub, cnum = row
    make_likes(likes, csub, cnum, START_STUDENT_ID, END_STUDENT_ID)


print("insert into friends values" + ',\n'.join(['({},{})'.format(friender, friendee) for friender, friendee in friendships]) + ';')
print("insert into attends values" + ',\n'.join(['({},"{}")'.format(sid, cid) for sid, cid in enrollments]) + ';')
print("insert into likes values" + ',\n'.join(['({},"{}","{}")'.format(sid, csub, cnum) for sid, csub, cnum in likes]) + ';')

# Don't actually commit anything
cnx.rollback()
cursor.close()
cnx.close()