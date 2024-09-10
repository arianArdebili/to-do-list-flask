from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["SECRET_KEY"] = "your_secret_key"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Todo model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    todo = db.Column(db.String, unique=True, nullable=False)
    completed = db.Column(db.Boolean, default=False)  # New field to track task completion

# Index route
@app.route("/")
def index():
    tasks = Todo.query.all()  # Fetch all tasks
    return render_template("index.html", tasks=tasks)

# Add task route
@app.route('/add', methods=['POST'])
def add():
    todo_item = request.form.get('todo')  # Get the 'todo' value from the form
    if todo_item:
        existing_task = Todo.query.filter_by(todo=todo_item).first()  # Check if task exists
        if existing_task:
            flash("This task already exists. Please add a new task.", "danger")  # Flash a message if duplicate
        else:
            new_todo = Todo(todo=todo_item)  # Create a new Todo object
            db.session.add(new_todo)  # Add it to the session
            db.session.commit()  # Commit the transaction
            flash("Task added successfully!", "success")  # Flash success message
    return redirect(url_for('index'))  # Redirect to the index route

# Update task route
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    existing_task = Todo.query.get_or_404(id)  # Fetch the task or return 404 if not found
    if request.method == 'POST':
        new_task = request.form.get('todo')
        completed = request.form.get('completed') == 'on'  # Check if the 'completed' checkbox is checked
        if new_task:
            duplicate_task = Todo.query.filter_by(todo=new_task).first()
            if duplicate_task and duplicate_task.id != id:
                flash("This task already exists.", "danger")
            else:
                existing_task.todo = new_task
                existing_task.completed = completed  # Update the completed status
                db.session.commit()  # Commit the update
                flash("Task updated successfully!", "success")
        return redirect(url_for('index'))  # Redirect after updating
    return render_template('update.html', task=existing_task)  # Show update form

# Delete task route
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    existing_task = Todo.query.get_or_404(id)  # Fetch the task or return 404 if not found
    db.session.delete(existing_task)  # Delete the task from the database
    db.session.commit()  # Commit the transaction
    flash("Task deleted successfully!", "success")  # Flash success message
    return redirect(url_for('index'))  # Redirect to the index route

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()  # This will drop all tables
        db.create_all()  # This will create all tables with the current model
    app.run(debug=True)
