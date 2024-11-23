from App.database import db


class CompetitionStudent(db.Model):
    __tablename__ = 'competition_student'

    comp_id = db.Column(db.Integer, db.ForeignKey('competition.id'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), primary_key=True)
    score = db.Column(db.Integer, default=0)
    competition = db.relationship('Competition', backref=db.backref('competition_student', lazy=True))
    student = db.relationship('Student', backref=db.backref('competition_student', lazy=True))

    def __init__(self, comp_id, student_id, score):
        self.comp_id = comp_id
        self.student_id = student_id
        self.score = score

    def __repr__(self):
        return f'<CompetitionStudent {self.comp_id} : {self.student_id}>'