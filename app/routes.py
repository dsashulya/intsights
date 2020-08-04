from flask import render_template, redirect, request, url_for, flash, abort
from werkzeug.utils import secure_filename
import os
from app import app
from app import db
from models import Company, Department, Internship, Review
from datetime import datetime
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
months = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь','июль','август','сентябрь','октябрь','ноябрь','декабрь']
timing_codes = {1:'месяц', 2:'2 месяца', 3:'3 месяца', 
4:'3-6 месяцев', 5:'6-9 месяцев', 6:'до года', 7:'от года до двух', 8:'два года'}
schedule_codes = {1:'полный день', 2:'сменный график', 3:'гибкий график', 4:'удаленная работа', 5:'вахтовый метод'}
worktype_codes = {1:'полная', 2:'частичная', 3:'проектная работа'}

def summarise_types(items_list, column):
    """ receives a list of serialized objects 
    returned from db query and a column name
    returns a set of unique column values """
    types = set()
    for item in items_list:
        types.add(item[column])
    return types

def summarise_percentage(items_list, column):
    """ receives a list of serialized objects and a column name 
    returns integer percentage of 1's in the column """
    if not len(items_list):
        return 0
    paid = 0
    for item in items_list:
        if item[column] == 1:
            paid += 1
    return int(round(paid*100/len(items_list), 0))

def mean_rating(items_list, rating):
    """ receives a list of serialized objects and a column name
    returns integer mean of the column """
    if len(items_list):
        return int(round(sum(item[rating] for item in items_list)/len(items_list), 0))
    else:
        return 0

def chunks(l, n):
    """ yield successive chunks of size n from l """
    length = len(l)
    for i in range(0, length, n):
        yield l[i:i +n]

def allowed_file(filename):
    """ check if file type is in the allowed list """
    return '.' in filename and \
           filename.split('.')[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    """ shows reviews tab with companies """
    
    jsoncomps = []
    for company in Company.query.all():
        jsoncomps.append(company.serialize())
    jsoncomps = sorted(jsoncomps, key=lambda company: company['name'].upper())
    jsoncomps = list(chunks(jsoncomps, 4))

    internships = Internship.query.all()
    l = len(jsoncomps)
    def filterdb(filteritem):
        return Internship.query.filter_by(company_id=filteritem) 
    return render_template("index.html", l=l, jsoncomps=jsoncomps, internships=internships, title="Компании", filterdb=filterdb)

@app.route("/company/<company_id>")
def show_internships(company_id):
    internships = sorted(Internship.query.filter_by(company_id=company_id), key=lambda department: department.title)
    jsonints = []
    for internship in internships:
        jsonints.append(internship.serialize())
    company = Company.query.filter_by(id=company_id).first().name

    departments = Department.query.filter_by(company_id=company_id)
    jsondepts = []
    for department in departments:
        jsondepts.append(department.serialize())
    return render_template("internships.html", jsonints=jsonints, company_id=company_id,\
        departments=jsondepts, company=company, title="Стажировки")

@app.route("/company/<company_id>/internship/<department_id>")
def show_reviews(company_id, department_id):
    department = Department.query.get_or_404(department_id)
    reviews = sorted(Review.query.filter_by(department_id=department_id), key=lambda review: review.id, reverse=True)
    total = len(reviews)
    jsonreviews = []
    for review in reviews:
        jsonreviews.append(review.serialize())
    workTypes = summarise_types(jsonreviews, 'workType')
    schedules = summarise_types(jsonreviews, 'schedule')
    paid = summarise_percentage(jsonreviews, 'paid')
    workContinued = summarise_percentage(jsonreviews, 'workContinued')
    contract = summarise_percentage(jsonreviews, 'contract')
    meanRating = mean_rating(jsonreviews, 'rating')
    meanResponsibilitiesRating = mean_rating(jsonreviews, 'responsibilitiesRating')
    meanMentorshipRating = mean_rating(jsonreviews, 'mentorshipRating')
    meanScheduleRating = mean_rating(jsonreviews, 'scheduleRating')
    meanUsefulnessRating = mean_rating(jsonreviews, 'usefulnessRating')
    
    try:
        timing = timing_codes[department.timing]
    except:
        timing = '-'
    requirements = department.requirements.split(';') if department.requirements else None
    responsibilities = department.responsibilities.split(';') if department.responsibilities else None
    return render_template("reviews.html", company_id=company_id, department=department, timing=timing,\
        workTypes=workTypes,schedules=schedules,\
        contract=int(contract),meanMentorshipRating=int(meanMentorshipRating), meanScheduleRating=int(meanScheduleRating),\
        requirements=requirements, responsibilities = responsibilities, \
            worktype_codes=worktype_codes, schedule_codes=schedule_codes,\
            reviews=jsonreviews, paid=int(paid), workContinued=int(workContinued), total=total, \
                meanRating=int(meanRating), meanResponsibilitiesRating=int(meanResponsibilitiesRating),\
                    meanUsefulnessRating=int(meanUsefulnessRating), title='Отзывы')

@app.route("/company/<company_id>/internship/<department_id>/reviews")
def show_comments(company_id, department_id):
    department = Department.query.get_or_404(department_id)
    reviews = sorted(Review.query.filter_by(department_id=department_id).filter_by(review=1), key=lambda review: review.id, reverse=True)

    jsonreviews = []
    for review in reviews:
        jsonreviews.append(review.serialize())

    
    timing = timing_codes[department.timing]
    requirements = department.requirements.split(';') if department.requirements else None
    responsibilities = department.responsibilities.split(';') if department.responsibilities else None
   
    reviews_exist = summarise_percentage(jsonreviews, 'review')
    jsonreviews = list(chunks(jsonreviews, 4))
    l = len(jsonreviews)

    return render_template('comments.html', timing=timing,\
        requirements=requirements, responsibilities=responsibilities,\
             company_id=company_id, department=department, reviews_exist=reviews_exist,\
                 jsonreviews=jsonreviews, l=l)

@app.route("/form", methods=["GET", "POST"])
def form():
    failed = 0
    """ renders a survey form to fill in  """
    if request.method == "POST":
        internship = request.form.get("internship")
        start_month = request.form.get("start-month")
        start_year = request.form.get("start-year")
        end_month = request.form.get("end-month")
        end_year = request.form.get("end-year")
        workType = request.form.get("workType")
        schedule = request.form.get("schedule")
        rating = request.form.get("rating")
        responsibilitiesRating = request.form.get("responsibilitiesRating")
        usefulnessRating = request.form.get("usefulnessRating")
        scheduleRating = int(request.form.get("scheduleRating"))
        mentorshipRating = int(request.form.get("mentorshipRating"))
        contract = request.form.get("contract")
        paid = request.form.get("paid") # 0/1
        workContinued = request.form.get("workContinued") # 0/1
        pros = request.form.get("pros")
        cons = request.form.get("cons")
        review = 1 if pros or cons else 0
        if internship and start_month and start_year and end_month and end_year \
            and workType and schedule and scheduleRating and mentorshipRating and contract and rating and \
            responsibilitiesRating and usefulnessRating and paid and workContinued:
            
            review = Review(department_id=int(internship), \
                workType = int(workType), schedule=int(schedule), scheduleRating = int(scheduleRating), \
                    mentorshipRating=int(mentorshipRating), contract=int(contract), \
                month_start=start_month, year_start=int(start_year), month_end=end_month, \
                    year_end=int(end_year), rating=int(rating), \
                        responsibilitiesRating = int(responsibilitiesRating), \
                            usefulnessRating = int(usefulnessRating), paid = int(paid), \
                        workContinued = int(workContinued), pros=pros, cons=cons, review=review)
            db.session.add(review)
            db.session.commit()
            flash('Ваш отзыв опубликован', 'success')
            return redirect(url_for('index'))
        else:
            failed = 1

    companies = sorted(Company.query.all(), key=lambda company: company.name.upper())
    jsonints = []
    for internship in Internship.query.all():
        jsonints.append(internship.serialize())

    jsondepts = []
    for department in Department.query.all():
        jsondepts.append(department.serialize())
    jsondepts = sorted(jsondepts, key=lambda dept: dept['internship_id'])
    current_year = datetime.now().year
    return render_template("form.html", type_of_work=worktype_codes, schedule=schedule_codes,\
                        failed=failed, title='Анкета', months=months, companies=companies, \
                        jsonints = jsonints, jsondepts=jsondepts, current_year=current_year)

@app.route("/add", methods = ["GET", "POST"])
def add_internship():
    """ renders a form to add a new internship/company """
    if request.method == "POST":
        # gets company_id if company listed else company name
        
        filepath = None
        company = int(request.form.get("company")) if request.form.get("company") != "new" else request.form.get("newCompany")
        if type(company) != int:
            internship = request.form.get("newInternship")
            
        else:
            internship = int(request.form.get("internship")) if request.form.get("internship") != "new" \
            else request.form.get("newInternship")

        department = request.form.get("newDepartment")
        location = request.form.get("city")
        timing = int(request.form.get("timing")) if request.form.get("timing") else None
        
        if company and internship and department:
            new_entry = []
            new_company_id = len(Company.query.all()) + 1
            new_internship_id = len(Internship.query.all()) + 1

            # if new company
            if type(company) != int:
                if Company.query.filter_by(name=company).first():
                    flash('Компания уже есть в списке', 'success')
                    return redirect(url_for('add_internship'))

                new_entry.append(Company(name=company, img=filepath))
                new_entry.append(Internship(title=internship, company_id=new_company_id))
                new_entry.append(Department(title=department, internship_id=new_internship_id,\
                    company_id=new_company_id, timing=timing, location=location))

            # if new internship
            elif type(internship) != int:
                new_entry.append(Internship(title=internship, company_id=company))
                new_entry.append(Department(title=department, internship_id=new_internship_id,\
                    company_id=company, timing=timing, location=location))

            # only new dept
            else:
                new_entry.append(Department(title=department, company_id=company, \
                    internship_id=internship, timing=timing, location=location)) 

            for entry in new_entry:
                db.session.add(entry)

            db.session.commit()
            flash('Стажировка добавлена', 'success')
            return redirect(url_for('index'))
        
        else:
            return redirect(url_for('form'))
    

    else:
        timing = {'месяц': 1, '2 месяца': 2, '3 месяца': 3, '3-6 месяцев': 4, '6-9 месяцев': 5, 'до года': 6, 'от года до двух': 7, 'два года': 8}
        companies = sorted(Company.query.all(), key=lambda company: company.name.upper())
        jsonints = []
        for internship in Internship.query.all():
            jsonints.append(internship.serialize())
        return render_template("add.html", title="Добавить", companies=companies,\
            jsonints=jsonints, timing=timing)

