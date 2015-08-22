"""Models and database functions for LearningPage project."""



# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, ForeignKey, or_, create_engine, DateTime, Date
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func



db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):

    __tablename__ = "users"

    user_id = db.Column(Integer, autoincrement=True, primary_key=True)
    first_name = db.Column(String(50), nullable=False)
    last_name = db.Column(String(50), nullable=False)
    user_name = db.Column(String(50), nullable=False)
    password = db.Column(String(50), nullable=False)
    
    

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s>" % (self.user_id, self.user_name, self.first_name, self.last)

    

class Visit(db.Model):

    __tablename__ = "visits"

    visit_id = db.Column(Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(String(200), db.ForeignKey('users.user_id'))
    visit_date = db.Column(DateTime(timezone=True), default=func.now())
   
    # define relationship with user table

    user = db.relationship("User",
                           backref=db.backref("visit"))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Visit visit_id=%s user_id=%s visit_date=%s>" % (
            self.visit_id, self.user_id, self.visit_date)



class Topic_visited(db.Model):

    __tablename__ = "topics_visited"

    topics_visited_id = db.Column(Integer, autoincrement=True, primary_key=True)
    visit_id = db.Column(Integer, ForeignKey('visits.visit_id'), nullable=False)
    topic_id = db.Column(Integer, ForeignKey('topics.topic_id'), nullable=False)

     
   
    # Define relationship with Topic
    topic = db.relationship("Topic",
                           backref=db.backref("topic_visited"))

    visit = db.relationship("Visit",
                           backref=db.backref("topic_visited"))

    
    
class Topic(db.Model):

    __tablename__ = "topics"

    topic_id = db.Column(Integer, autoincrement=True, primary_key=True)
    topic_title = db.Column(String(100), nullable=False)
    zoom = db.Column(Integer)
    maxzoom = db.Column(Integer)
    minzoom = db.Column(Integer)
    start_date = db.Column(Date)
    end_date = db.Column(Date)
    main_date = db.Column(Date)
    center_lat = db.Column(Integer)
    center_lng = db.Column(Integer)
    image= db.Column(String(200))
    description = db.Column(String(500))

class Topic_wiki(db.Model):

    __tablename__ = "topic_wiki"

    topic_wiki_id = db.Column(Integer, autoincrement=True, primary_key=True)
    #once this is converted to a postgresSQL database this will contain the actual JSON data.  
    #Until then it will contain the location of the data
    wiki_json = db.Column(String(50000))
    topic_id = db.Column(Integer, ForeignKey('topics.topic_id'), nullable=False)
    
        
    # Define relationship with Topic
    topic = db.relationship("Topic",
                           backref=db.backref("topic_wiki"))


class Topic_video(db.Model):

    __tablename__ = "topic_videos"

    topic_video_id = db.Column(Integer, autoincrement=True, primary_key=True)
    youtube_video_key = db.Column(Integer, nullable=False)
    topic_id = db.Column(Integer, ForeignKey('topics.topic_id'), nullable=False)
    video_description = db.Column(String(5000), nullable=True)
    video_title = db.Column(String(500))    
    
        
    # Define relationship with Topic
    topic = db.relationship("Topic",
                           backref=db.backref("topic_video"))

   

class Event_data(db.Model):

    __tablename__ = "event_data"

    event_data_id = db.Column(Integer, autoincrement=True, primary_key=True)
    topic_id = db.Column(Integer, ForeignKey('topics.topic_id'), nullable=False)
    lat = db.Column(Integer)
    lng = db.Column(Integer)
    description = db.Column(String(500))
    event_date = db.Column(DateTime)
    event_title = db.Column(String(100))
    image= db.Column(String(200))


    topic = db.relationship("Topic",
                           backref=db.backref("event_data"))

   


class Note(db.Model):

    __tablename__ = "notes"

    note_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    topics_visit_id = db.Column(Integer, ForeignKey('topics_visited.topics_visited_id'), nullable=False)
    

    # Define relationship to Topic_visited
    topics_visited = db.relationship("Topic_visited",
                           backref=db.backref("note"))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Note note_id=%s topics_visited_id=%s>" % (
            self.note_id, self.topis_visited_id)
        
                    


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///learningpage.db'
    db.app = app
    db.init_app(app)
    

if __name__ == "__main__":
    # If this module is run interactively, it will be left 
    # in a state of being making it possible able to work with the database directly.
    
    from server import app
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."

    