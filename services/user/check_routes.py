from app import app

print("=== Checking Flask App Routes ===")
print(f"Flask app name: {app.name}")
print("Registered routes:")

for rule in app.url_map.iter_rules():
    methods = ', '.join(rule.methods)
    print(f" - {rule.endpoint}: {rule.rule} [{methods}]")

print("\nIf you don't see the expected routes, you might be running a different app.py file.")
print("Try stopping all Flask servers and restart with: python app.py") 