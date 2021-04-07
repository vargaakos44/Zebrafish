import sqlite3


def create_tables():
    conn = sqlite3.connect('C:\\Thesis\\Survey.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS Survey(surveyPath TEXT, surveyName TEXT PRIMARY KEY, preprocessed INTEGER )')
    c.execute('CREATE TABLE IF NOT EXISTS SubSurvey(subSurveyPath TEXT, subSurveyName TEXT PRIMARY KEY'
              ', parentName TEXT, preprocessed INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS Circles(X INTEGER , Y INTEGER , Radius INTEGER ,'
              ' imageName TEXT PRIMARY KEY)')
    c.close()
    conn.close()


def insert_survey(a, b, d):
    conn = sqlite3.connect('C:\\Thesis\\Survey.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO Survey (surveyPath, surveyName, preprocessed) VALUES(?, ?, ?)', (a, b, d))
        conn.commit()
        c.close()
        conn.close()
        return True
    except sqlite3.IntegrityError as e:
        print('sqlite error: ', e.args[0])
        c.close()
        conn.close()
        return False


def insert_sub_survey(a, b, d, f):
    conn = sqlite3.connect('C:\\Thesis\\Survey.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO SubSurvey (subSurveyPath, subSurveyName, parentName, preprocessed) VALUES (?, ?, ?, ?)', (a, b, d, f))
        conn.commit()
        c.close()
        conn.close()
        return True
    except sqlite3.IntegrityError as e:
        print('sqlite error: ', e.args[0])
        c.close()
        conn.close()
        return False


def select_survey_names():
    conn = sqlite3.connect('C:\\Thesis\\Survey.db')
    c = conn.cursor()
    c.execute('SELECT * FROM Survey')
    data = c.fetchall()
    c.close()
    conn.close()
    return data


def select_survey_path(param):
    conn = sqlite3.connect('C:\\Thesis\\Survey.db')
    c = conn.cursor()
    c.execute('SELECT * FROM Survey WHERE surveyName LIKE (?)', (param, ))
    data = c.fetchall()
    c.close()
    conn.close()
    return data


def delete_survey(param):
    conn = sqlite3.connect('C:\\Thesis\\Survey.db')
    c = conn.cursor()
    c.execute('DELETE FROM Survey WHERE surveyName LIKE (?)', (param, ))
    conn.commit()
    c.close()
    conn.close()


def delete_attached_sub_surveys(param):
    conn = sqlite3.connect('C:\\Thesis\\Survey.db')
    c = conn.cursor()
    c.execute('DELETE FROM SubSurvey WHERE parentName LIKE (?)', (param, ))
    conn.commit()
    c.close()
    conn.close()


def select_sub_survey_names(param):
    conn = sqlite3.connect('C:\\Thesis\\Survey.db')
    c = conn.cursor()
    c.execute('SELECT * FROM SubSurvey WHERE parentName LIKE (?)', (param, ))
    data = c.fetchall()
    c.close()
    conn.close()
    return data


def select_sub_survey_path(param):
    conn = sqlite3.connect('C:\\Thesis\\Survey.db')
    c = conn.cursor()
    c.execute('SELECT * FROM SubSurvey WHERE subSurveyName LIKE (?)', (param, ))
    data = c.fetchall()
    c.close()
    conn.close()
    return data


def delete_sub_survey(param):
    conn = sqlite3.connect('C:\\Thesis\\Survey.db')
    c = conn.cursor()
    c.execute('DELETE FROM SubSurvey WHERE subSurveyName LIKE (?)', (param, ))
    conn.commit()
    c.close()
    conn.close()

def insert_circle(p1, p2, p3, p4):
    conn = sqlite3.connect('C:\\Thesis\\Survey.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO Circles(X, Y, Radius, imageName) VALUES (?, ?, ?, ?)',
                  (p1, p2, p3, p4))
        conn.commit()
        c.close()
        conn.close()
        return True
    except sqlite3.IntegrityError as e:
        print('sqlite error: ', e.args[0])
        c.close()
        conn.close()
        return False

def updadte_circle(x, y, r, image_name):
    conn = sqlite3.connect('C:\\Thesis\\Survey.db')
    c = conn.cursor()
    try:
        c.execute('UPDATE Circles SET X = ? , Y = ?, Radius = ? WHERE imageName LIKE (?)', (x, y, r, image_name))
        conn.commit()
        c.close()
        conn.close()
        return True
    except sqlite3.IntegrityError as e:
        print('sqlite error: ', e.args[0])
        c.close()
        conn.close()
        return False

def select_radius(image_name):
    conn = sqlite3.connect('C:\\Thesis\\Survey.db')
    c = conn.cursor()
    c.execute('SELECT * FROM Circles WHERE imageName LIKE (?)', (image_name, ))
    data = c.fetchall()
    c.close()
    conn.close()
    return data

def read_file(param):
    infile = open(param, 'r')
    content = infile.read()
    infile.close()
    return content


def write_file(param_1, param_2):
    outfile = open(param_1, 'w+')
    outfile.write(param_2)
    outfile.close()

