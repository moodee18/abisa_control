import sys
sys.path.insert(0, '.')
from database import DatabaseManager, verify_password, UserAccount

db = DatabaseManager('sqlite:///data/abisalud.db')
session = db.get_session()
user = session.query(UserAccount).filter_by(username='admin').first()
print("User found:", user.username)
print("Password hash:", user.password_hash)
print("verify admin123:", verify_password("admin123", user.password_hash))
print("verify admin:", verify_password("admin", user.password_hash))
session.close()

