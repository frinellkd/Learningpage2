# Import libraries needed for project

# for youtube connection
from xml.etree import ElementTree

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Visit, Topic_visited, Topic, Topic_video, Note, Event_data, connect_to_db, db, Topic_wiki

from sqlalchemy import update

import sqlite3, json

from datetime import datetime


db_connection = sqlite3.connect("learningpage.db", check_same_thread=False)
db_cursor = db_connection.cursor()

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    
    topic_data = db.session.query(Topic.topic_id, Topic.topic_title, 
                Topic.center_lat, Topic.center_lng, Topic.description,
                Topic.main_date, Topic.image).order_by(Topic.topic_id).all()

    delete_data = db.session.query(Topic.topic_id, 
                Topic.topic_title).filter(Topic.createdby >= 0).all()

    return render_template("homepage.html", topic_data=topic_data, delete_data=delete_data)

@app.route("/remove_topic")
def deletetopic():
    print "Made it to function"
    delete_data = db.session.query(Topic.topic_id).filter(Topic.createdby >= 0).all()

    for data in delete_data:
        print "data id: ", data.topic_id
        event = request.args.get(str(data.topic_id))
        print "event retrieved:", event
        if event == 'checked':
            Topic.query.filter_by(topic_id=data.topic_id).delete()
            
            
    flash("Delete completed.")
    db.session.commit()


    return redirect('/')

@app.route('/new_event/<int:id>')
def addNewEvent(id):
    """Gets the information obtained from the form and process it for adding to the timeline"""    

    event_title = request.args.get("event_title")
    event_day   = request.args.get("event_day")
    event_month = request.args.get("event_month")
    event_year  = request.args.get("event_year")
    event_lat   = request.args.get("event_lat")
    event_lng   = request.args.get("event_lng")
    event_image = request.args.get("event_image")
    event_desc  = request.args.get("event_desc")

    date = datetime(int(event_year), int(event_month), int(event_day))

    new_event = Event_data(topic_id=id, lat=event_lat, lng=event_lng, description=event_desc,
        event_date=date, event_title=event_title, image=event_image)

    db.session.add(new_event)
    db.session.commit()

    return redirect('/view/' + str(id))

@app.route('/new_topic')
def addNewTopic():
    """Gets the information obtained from the form and process it for adding to the timeline"""    

    topic_title = request.args.get("topic_title")
    topic_day   = request.args.get("topic_day")
    topic_month = request.args.get("topic_month")
    topic_year  = request.args.get("topic_year")
    topic_lat   = request.args.get("topic_lat")
    topic_lng   = request.args.get("topic_lng")
    topic_image = request.args.get("topic_image")
    topic_desc  = request.args.get("topic_desc")

    date = datetime(int(topic_year), int(topic_month), int(topic_day))

    new_topic = Topic(center_lat=topic_lat, center_lng=topic_lng, description=topic_desc,
        main_date=date, topic_title=topic_title, image=topic_image)

    print "TOPIC TO ADD:", new_topic

    db.session.add(new_topic)
    db.session.commit()

    #Adds the new topic as an event

    topic_id = db.session.query(Topic.topic_id).filter(Topic.description
        ==topic_desc, Topic.main_date==date, Topic.topic_title==topic_title).one()

    new_event = Event_data(topic_id=topic_id[0], lat=topic_lat, lng=topic_lng, description=topic_desc,
        event_date=date, event_title=topic_title, image=topic_image )

    db.session.add(new_event)
    db.session.commit()

    return redirect('/')

@app.route("/remove_event/<int:id>")
def deleteevent(id):
    delete_data = db.session.query(Event_data.event_data_id, 
                Event_data.event_title).filter(Event_data.topic_id==id).filter(Event_data.createdby >= 0).order_by(Event_data.event_date).all()

    for data in delete_data:
        print data.event_data_id
        event = request.args.get(str(data.event_data_id))
        print event
        if event == 'checked':
            Event_data.query.filter_by(event_data_id=data.event_data_id).delete()
            
            
    flash("Delete completed.")
    db.session.commit()


    return redirect('/view/' + str(id))

@app.route("/edit_event")
def editevent():
    event_id = request.args.get("event_id")
    print "event id: ", event_id
    
    edit_data = db.session.query(Event_data.event_data_id, Event_data.lat, 
        Event_data.lng, Event_data.event_date, Event_data.image, 
        Event_data.description,
                Event_data.event_title).filter(Event_data.event_data_id==event_id).filter(Event_data.createdby >= 0).order_by(Event_data.event_date).one()

    event_data = {
            'title': edit_data.event_title,
            'lat': edit_data.lat,
            'lng' : edit_data.lng,
            'event_id' : edit_data.event_data_id,
            'image' : edit_data.image,
            'description' : edit_data.description,
            'day' : '%02d'%edit_data.event_date.day,
            'month' : '%02d'%edit_data.event_date.month,
            'year' : str(edit_data.event_date.year)

    }

    return  json.dumps(event_data)

@app.route("/update_event/<int:id>")
def updateEvent(id):
    """Gets the information obtained from the form and process it for changing the database and updating it."""    
    
    event_id = request.args.get("event_id")
    event_title = request.args.get("event_title")
    event_day   = request.args.get("event_day")
    event_month = request.args.get("event_month")
    event_year  = request.args.get("event_year")
    event_lat   = request.args.get("event_lat")
    event_lng   = request.args.get("event_lng")
    event_image = request.args.get("event_image")
    event_desc  = request.args.get("event_desc")
    

    date = datetime(int(event_year), int(event_month), int(event_day))

    update_event = Event_data.query.filter_by(event_data_id=event_id).one()
    update_event.lat=event_lat
    update_event.lng=event_lng 
    update_event.description=event_desc
    update_event.event_date=date
    update_event.event_title=event_title
    update_event.image = event_image
    
    db.session.commit()

    return redirect('/view/' + str(id))  

@app.route('/login_submit')
def login_submit():
    """checks whether person has a current logi and if so, logs them in.  If not it swnds them to a page to creates an account """
    user_name = request.args.get("user_name")
    password = request.args.get("password")

    current_users = db.session.query(User.user_name, User.user_id).filter_by(user_name=user_name, password=password).all()
    
    if len(current_users) >= 1:
        session_id = current_users[0][1]
        
    else:
        if len(db.session.query(User.user_name).filter_by(user_name=user_name).all()) >= 1:
            flash("Incorrect password.  Please try again")
            return redirect('/login_form')

        else: 
            flash('There is no user matching the username you provided.  Please create an account.')
            return redirect('/')

    if session_id:
        # creates an instance of visit when someone logs in.
        visit = Visit(user_id=session_id)
        db.session.add(visit)
        db.session.commit()


        # creates an instance of the session when someone logs in.
        session['user_id'] = session_id
        flash('You are logged in')

    return redirect('/users/' + str(session_id))


@app.route('/check_user_name', methods=['POST'])
def check_user_name():
    """ Checks if a user name is used or not and returns that message via ajax to the page"""
    user_name = request.form.get("user_name")

    user_name_check = db.session.query(User.user_id).filter_by(user_name=user_name).all()


    if len(user_name_check) >=1:
        return '<img src=static/img/redx.png width=7%> Not Available'
    else:
        return '<img src=static/img/greentick.jpg width=10%> Available'

@app.route('/new_user_form')
def create_new_user():

    return render_template('new_user_form.html')

@app.route('/new_user_submit')
def new_user_submit():
    """creates a new account """
    
    first_name = request.args.get("first_name")
    last_name = request.args.get("last_name")
    user_name = request.args.get("user_name")
    password = request.args.get("password")



    user_existing_check = db.session.query(User.user_id).filter_by(first_name=first_name, last_name=last_name).all()
    
            

    if len(user_existing_check) >= 1:
        flash('There is already an account registered under that name')
        return redirect('/login_form')

    else:    
        #SQL Statement entering user info
        user = User(first_name=first_name, last_name=last_name, user_name=user_name, 
                    password= password)

        db.session.add(user) 
        db.session.commit()
            
        user_id = db.session.query(User.user_id).filter_by(user_name=user_name, password=password).one()   
        session_id = user_id[0]
               

    if session_id:
        # creates an instance of visit when someone logs in.
        visit = Visit(user_id=session_id)
        db.session.add(visit)
        db.session.commit()


        # creates an instance of the session when someone logs in.
        session['user_id'] = session_id
        flash('You are logged in')

    return redirect('/users/' + str(session_id))

@app.route('/logout')
def log_out():

    session.clear()
    flash('You are logged out.')
    return redirect('/')       


#######################################################

@app.route('/view/<int:id>')
def view_topic_selected(id):

    """ Takes the topic id from the URL and uses it to locate correct information to display"""
    try:
        # gets all the the youtube keys from the database
        youtube_keys = db.session.query(Topic_video.youtube_video_key, Topic_video.video_title).filter(Topic_video.topic_id == id).all()
        print "youtube_keys: ", youtube_keys
        # gets the path for the wiki page from the database
        topic_selected_wiki = db.session.query(Topic_wiki.wiki_json).filter(Topic_wiki.topic_id == id).one()

        print "topic_selected_wiki", topic_selected_wiki

        topic_wiki = str(topic_selected_wiki.wiki_json).strip()

        data = open(topic_wiki).read()
        wiki_data = json.loads(data)
        wiki_data_title = wiki_data['parse']['title']
        wiki_data_parsed = wiki_data['parse']['text']['*']

        print "wiki_data_parsed", wiki_data_parsed

        # prepares the path by stripping off a retrun (will do this before populating the database in the future)
        

        print "topic_wiki: ", topic_wiki

    except Exception as e:
        print e
        print "has no youtube and wiki!"
        youtube_keys = None
        topic_wiki = None
        wiki_data_parsed = None
        wiki_data_title = None

        # map_data = db.session.query(Topic.zoom, Topic.maxzoom, Topic.minzoom,
        #         Topic.center_lat, Topic.center_lng).filter(Topic.topic_id==id).one()

        # time_data = db.session.query(Topic.band1,Topic.band2,Topic.band3,
        #                      Topic.main_date).filter(Topic.topic_id==id).one()

        # delete_data = db.session.query(Event_data.event_data_id, 
        #         Event_data.event_title).filter(Event_data.topic_id==id).filter(Event_data.createdby >= 0).order_by(Event_data.event_date).all()
        # # logs a instance of a topic being visited if the person is logged on.
        
        # data_set = db.session.query(Event_data.topic_id, Event_data.event_title, 
        #         Event_data.lat, Event_data.lng, Event_data.description,
        #         Event_data.event_date, Event_data.image, Event_data.event_data_id,
        #         Topic.topic_title).join(Topic).filter(Event_data.topic_id==id).order_by(Event_data.event_date).all()


        # if 'user_id' in session:
        #     user_id=session['user_id']
        #     v_info = db.session.query(Visit.visit_id).filter_by(user_id=user_id).all()
        #     current_visit = v_info[-1][0]
        #     t_visited = Topic_visited(visit_id=current_visit, topic_id=id)
        #     db.session.add(t_visited)
        #     db.session.commit()


        # return render_template("view.html", topic_id=id, 
        #     map_data=map_data, time_data=time_data, delete_data=delete_data, event_data=data_set)


    
    data_set = db.session.query(Event_data.topic_id, Event_data.event_title, 
                Event_data.lat, Event_data.lng, Event_data.description,
                Event_data.event_date, Event_data.image, Event_data.event_data_id,
                Topic.topic_title).join(Topic).filter(Event_data.topic_id==id).order_by(Event_data.event_date).all()

    delete_data = db.session.query(Event_data.event_data_id, 
                Event_data.event_title).filter(Event_data.topic_id==id).filter(Event_data.createdby >= 0).order_by(Event_data.event_date).all()
 
    map_data = db.session.query(Topic.zoom, Topic.maxzoom, Topic.minzoom,
                Topic.center_lat, Topic.center_lng).filter(Topic.topic_id==id).one()

    time_data = db.session.query(Topic.band1,Topic.band2,Topic.band3,
                             Topic.main_date).filter(Topic.topic_id==id).one()

    topic_title = db.session.query(Topic.topic_title).filter(Topic.topic_id==id).one()


    # logs a instance of a topic being visited if the person is logged on.
    if 'user_id' in session:
        user_id=session['user_id']
        v_info = db.session.query(Visit.visit_id).filter_by(user_id=user_id).all()
        current_visit = v_info[-1][0]
        t_visited = Topic_visited(visit_id=current_visit, topic_id=id)
        db.session.add(t_visited)
        db.session.commit()


        

    return render_template("view.html", youtube_keys=youtube_keys, 
        wiki_data=wiki_data_parsed, wiki_title=wiki_data_title, topic_id=id, 
        event_data=data_set, map_data=map_data, time_data=time_data, delete_data=delete_data, topic_title=topic_title)



#########################################################



@app.route('/users/<int:id>')
def userinfo(id):

    user_info = User.query.filter_by(user_id = id).one()
    
    topics_visited = db.session.query(Visit.visit_id,
                                    Topic_visited.visit_id,  
                                    Topic.topic_title,
                                    Visit.visit_date).join(Topic_visited).join(Topic).filter(Visit.user_id == id).all()

    print "topics_visited:", topics_visited                                
    
    return render_template("user_info.html", user=user_info, topics_visited=topics_visited)

@app.route('/user_redirect')
def userinfo_helper():
    try:

        session_id = session['user_id']

    except:
        
        flash("You are not logged on so there is no information page for you")
        return redirect('/')    

    return redirect('/users/' + str(session_id))





if __name__ == "__main__":
    # Debug toolbar has been turned on while working on this app
    # Will be turned off when finished
    app.debug = False

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()