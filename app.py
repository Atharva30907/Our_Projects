from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "secret123"

# DATABASE CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)

# ---------------- DATABASE MODEL ----------------
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(200), nullable=False)

# ---------------- HOME PAGE ----------------
@app.route('/')
def index():
    projects = Project.query.limit(3).all()  # ONLY 3 PROJECTS
    return render_template('index.html', projects=projects)

# ---------------- PROJECT DETAILS ----------------
@app.route('/project/<int:id>')
def project_detail(id):
    project = Project.query.get_or_404(id)
    return render_template('project_detail.html', project=project)

# ---------------- ADMIN LOGIN ----------------
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '1234':
            session['admin'] = True
            return redirect('/dashboard')
    return render_template('admin_login.html')

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect('/admin')

    projects = Project.query.all()
    return render_template('admin_dashboard.html', projects=projects)

# ---------------- ADD PROJECT ----------------
@app.route('/add', methods=['POST'])
def add_project():
    title = request.form['title']
    description = request.form['description']
    status = request.form['status']

    image = request.files['image']
    filename = image.filename

    # Save image
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    new_project = Project(
        title=title,
        description=description,
        status=status,
        image=filename
    )

    db.session.add(new_project)
    db.session.commit()

    return redirect('/dashboard')

# ---------------- DELETE PROJECT ----------------
@app.route('/delete/<int:id>')
def delete(id):
    project = Project.query.get(id)
    db.session.delete(project)
    db.session.commit()
    return redirect('/dashboard')

# ---------------- RUN APP ----------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # creates database automatically
    app.run(debug=True)