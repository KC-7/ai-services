import os
import json
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
import json
import math

if os.path.exists("env.py"):
    import env


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")


@app.route("/")
def index():
    return render_template("index.html")
    # Note: Flask expects this file to be in templates folder


@app.route("/about")
def about():
    data = []
    with open("data/company.json", "r") as json_data:
        data = json.load(json_data)
    return render_template("about.html", page_title="About", company=data)


@app.route("/about/<member_name>")
def about_member(member_name):
    member = {}
    with open("data/company.json", "r") as json_data:
        data = json.load(json_data)
        for obj in data:
            if obj["url"] == member_name:
                member = obj
    return render_template("member.html", member=member)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        flash("Thanks {}, we have received your message!".format(
            request.form.get("name")))
    return render_template("contact.html", page_title="Contact")


@app.route("/services")
def services():
    return render_template("services.html", page_title="Services")


# Function to load blog data from JSON file
def load_blog_data():
    with open('static/data/blog.json') as f:
        return json.load(f)['blogs']


# Blog listing with pagination
@app.route('/blog')
def blog_list():
    page = int(request.args.get('page', 1))  # Get current page number
    per_page = 5
    blogs = load_blog_data()
    total_pages = math.ceil(len(blogs) / per_page)

    # Paginate blogs
    start = (page - 1) * per_page
    end = start + per_page
    paginated_blogs = blogs[start:end]

    return render_template('blog_list.html', blogs=paginated_blogs, page=page, total_pages=total_pages)


# Individual blog post
@app.route('/blog/<slug>')
def blog_post(slug):
    blogs = load_blog_data()
    blog = next((b for b in blogs if b['slug'] == slug), None)
    if blog:
        return render_template('blog_post.html', blog=blog)
    else:
        return redirect(url_for('blog_list'))


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True
    )
