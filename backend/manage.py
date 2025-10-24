from app import create_app, db
from app.models import User, Case
import os
import click

app = create_app()

@app.cli.command()
def init_db():
    db.create_all()
    print("Database tables created successfully!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

@app.cli.command()
def run():
    app.run(host='0.0.0.0', port=5000, debug=True)

@app.cli.command()
def seed_db():
    try:
        # Create admin user
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        # Create regular user
        user = User.query.filter_by(username='user1').first()
        if not user:
            user = User(
                username='user1',
                email='user1@example.com',
                role='user'
            )
            user.set_password('user123')
            db.session.add(user)
        
        db.session.commit()
        
        # Create sample cases
        if Case.query.count() == 0:
            cases = [
                Case(
                    title='System Login Issue',
                    description='Users unable to login to the system',
                    status='open',
                    priority='high',
                    created_by=admin.id,
                    assigned_to=user.id
                ),
                Case(
                    title='Feature Request: Dark Mode',
                    description='Implement dark mode for better user experience',
                    status='in_progress',
                    priority='medium',
                    created_by=user.id
                ),
                Case(
                    title='Database Performance',
                    description='Optimize database queries for better performance',
                    status='closed',
                    priority='high',
                    created_by=admin.id,
                    assigned_to=admin.id
                )
            ]
            
            for case in cases:
                db.session.add(case)
        
        db.session.commit()
        print("Database seeded successfully!")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding database: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)