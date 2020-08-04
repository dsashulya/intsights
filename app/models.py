from datetime import datetime
from app import db


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    img = db.Column(db.String(30), unique=False, default="./static/default.jpg")
    internships = db.relationship('Internship', backref='company', lazy=True)
    departments = db.relationship('Department', backref='company', lazy=True)

    def serialize(self):
        return {"id": self.id,
        "name": self.name,
        "img": self.img}


class Internship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey(
        'company.id'), nullable=False)
    departments = db.relationship(
        'Department', backref = 'internship', lazy=True)
    
    def serialize(self):
        return {"id": self.id,
        "title": self.title,
        "company_id": self.company_id}

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey(
        'company.id'), nullable=False)
    internship_id = db.Column(db.Integer, db.ForeignKey(
        'internship.id'), nullable=False)
    reviews = db.relationship('Review', backref='department', lazy=True)
    requirements = db.Column(db.String(1000))
    responsibilities = db.Column(db.String(1000))
    timing = db.Column(db.Integer)
    location = db.Column(db.String(50), default='Санкт-Петербург')
    programmes = db.Column(db.String(250), nullable=True)

    def serialize(self):
        return {"id": self.id,
        "title": self.title,
        "company_id": self.company_id,
        "internship_id": self.internship_id,
        "reviews": len(self.reviews),
        "requirements": self.requirements,
        "responsibilities": self.responsibilities,
        "timing": self.timing,
        "location": self.location,
        "programmes": self.programmes}


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    month_start = db.Column(db.Text, nullable=False)
    year_start = db.Column(db.Integer, nullable=False)
    month_end = db.Column(db.Text, nullable=True)
    year_end = db.Column(db.Integer, nullable=True)
    workType = db.Column(db.Integer, nullable=False)
    schedule = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    usefulnessRating = db.Column(db.Integer, nullable=False)
    responsibilitiesRating = db.Column(db.Integer, nullable=False)
    scheduleRating = db.Column(db.Integer, nullable=False)
    mentorshipRating = db.Column(db.Integer, nullable=False)
    contract = db.Column(db.Integer, nullable=False)
    paid = db.Column(db.Integer, nullable=False) # 0/1
    workContinued = db.Column(db.Integer, nullable=False) # 0/1
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
    pros = db.Column(db.Text, nullable=True)
    cons = db.Column(db.Text, nullable=True)
    review = db.Column(db.Integer)
    department_id = db.Column(
        db.Integer, db.ForeignKey('department.id'), nullable=False)

    def serialize(self):
        return {"id": self.id,
        "department_id": self.department_id,
        "month_start": self.month_start,
        "year_start": self.year_start,
        "month_end": self.month_end,
        "year_end": self.year_end,
        "workType": self.workType,
        "schedule": self.schedule,
        "rating": self.rating,
        "responsibilitiesRating": self.responsibilitiesRating,
        "scheduleRating": self.scheduleRating,
        "mentorshipRating": self.mentorshipRating,
        "usefulnessRating": self.usefulnessRating,
        "contract": self.contract,
        "paid": self.paid,
        "workContinued": self.workContinued,
        "date_posted": self.date_posted,
        "pros": self.pros,
        "cons": self.cons,
        "review": self.review}


