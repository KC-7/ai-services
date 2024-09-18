# run.py

import os
import json
import math
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_mail import Mail, Message
from openai import OpenAI
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from openai import OpenAIError

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

# Configure Flask-Mail using environment variables
app.config['MAIL_SERVER'] = os.environ.get(
    'MAIL_SERVER', 'smtp.your-email-provider.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 465))
app.config['MAIL_USERNAME'] = os.environ.get(
    'MAIL_USERNAME', 'your-email@example.com')
app.config['MAIL_PASSWORD'] = os.environ.get(
    'MAIL_PASSWORD', 'your-email-password')
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', False)
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', True)

mail = Mail(app)

# Configure OpenAI

# Define WTForms for Contact Form


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[
                        DataRequired(), Email(), Length(max=120)])
    phone = StringField('Phone', validators=[Length(max=20)])
    message = TextAreaField('Message', validators=[
                            DataRequired(), Length(max=500)])


# Enforce HTTPS only if not in testing mode
if not app.config.get("TESTING"):
    Talisman(app, content_security_policy=None)


# Initialize Flask-Limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[]
    # default_limits=["100 per day", "25 per hour"]
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html", page_title="About")


@app.route("/about/<member_name>")
def about_member(member_name):
    member = {}
    try:
        with open("data/company.json", "r") as json_data:
            data = json.load(json_data)
            for obj in data:
                if obj["url"] == member_name:
                    member = obj
                    break
    except FileNotFoundError:
        flash("Company data file not found.", "danger")
    return render_template("member.html", member=member)


@app.route('/submit-contact-form', methods=['POST'])
def submit_contact_form():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        phone = form.phone.data
        message = form.message.data

        try:
            msg = Message('New Contact Form Submission',
                          sender=app.config['MAIL_USERNAME'],
                          recipients=[app.config['MAIL_USERNAME']])
            msg.body = f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}"
            mail.send(msg)
            flash('Your message has been sent successfully!', 'success')
        except Exception as e:
            flash(
                'There was an error sending your message. Please try again later.', 'danger')
    else:
        # Collect form errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(
                    f"Error in {getattr(form, field).label.text}: {error}", 'danger')

    return redirect('/contact')


@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    return render_template("contact.html", page_title="Contact", form=form)


@app.route("/services")
def services():
    return render_template("services.html", page_title="Services")

# Function to load blog data from JSON file


def load_blog_data():
    try:
        with open('static/data/blog.json') as f:
            return json.load(f)['blogs']
    except FileNotFoundError:
        flash("Blog data file not found.", "danger")
        return []

# Blog listing with pagination


@app.route('/blog')
def blog_list():
    page = int(request.args.get('page', 1))
    sort = request.args.get('sort', 'date')
    per_page = 5
    blogs = load_blog_data()

    # Sorting logic
    if sort == 'title':
        blogs.sort(key=lambda x: x['title'].lower())
    elif sort == 'date':
        blogs.sort(key=lambda x: x['date'], reverse=True)

    total_pages = math.ceil(len(blogs) / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_blogs = blogs[start:end]

    return render_template('blog_list.html', blogs=paginated_blogs, page=page, total_pages=total_pages, sort=sort, max=max, min=min)

# Individual blog post


@app.route('/blog/<slug>')
def blog_post(slug):
    blogs = load_blog_data()
    blog = next((b for b in blogs if b['slug'] == slug), None)
    if blog:
        return render_template('blog_post.html', blog=blog)
    else:
        flash("Blog post not found.", "warning")
        return redirect(url_for('blog_list'))

# Chatbot


client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))


@app.route("/chatbot", methods=["POST"])
@limiter.limit("5 per minute")  # Apply rate limiting to the chatbot route
def chatbot():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'response': 'No message provided.'}), 400

    try:
        response = client.chat.completions.create(model="gpt-4o-mini",
                                                  messages=[
                                                      {"role": "system",
                                                       "content": "You are KC-7's Assistant, a highly knowledgeable and professional virtual assistant. Your goal is to assist users in navigating the KC-7 website and understanding its range of AI services. Provide clear information on AI consulting, custom AI development, and AI integration services, including chatbots, content creation, and custom solutions. Encourage clients to engage by recommending direct contact through email (k@kc-7.com) or the contact form. Guide users to relevant sections, such as case studies, testimonials, and service details. Ensure all responses are aligned with KC-7’s offerings and advise clients on how AI can address their business challenges. Maintain a friendly, professional tone, and focus on promoting KC-7 as the ideal partner for AI solutions. Avoid personal opinions or unrelated information, focusing solely on KC-7's expertise and the business benefits of its services."},
                                                      {"role": "user",
                                                          "content": user_message}
                                                  ],
                                                  max_tokens=150,
                                                  temperature=0.7)
        chatbot_response = response.choices[0].message.content.strip()
    except openai.OpenAIError as e:
        app.logger.error(f"OpenAI API Error: {e}")
        chatbot_response = "Sorry, there was an error processing your request."

    return jsonify({'response': chatbot_response})


# Custom Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True
    )
