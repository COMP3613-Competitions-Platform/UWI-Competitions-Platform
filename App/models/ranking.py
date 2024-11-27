from App.database import db

class RankingHistory(db.Model):
    __tablename__ = 'ranking_history'

    id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    date = db.Column(db.String(50), nullable=False)
    rank = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    student = db.relationship('Student', backref=db.backref('ranking_history', lazy=True, cascade='all, delete-orphan'))


    def __init__(self, student_id, date, rank, rating):
        self.student_id = student_id
        self.date = date
        self.rank = rank
        self.rating = rating


    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "date": self.date,
            "rank": self.rank,
            "rating": self.rating
        }
        


