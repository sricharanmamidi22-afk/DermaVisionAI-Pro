import os
import sys

# This ensures that even if you run it from inside the backend folder, 
# it can find the other modules, but we still prefer running from root.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.database.models import User, Analysis, db

class ConsoleAssistant:
    def __init__(self):
        # We initialize the app to get access to the attached AI services
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        self.analyzer = self.app.skin_analyzer
        self.chatbot = self.app.chatbot_service

    def show_header(self):
        print("\n" + "="*50)
        print("[DERMAVISION] DERMAVISION AI: INTERNAL SYSTEMS CONSOLE")
        print("="*50)

    def list_personnel(self):
        users = User.query.all()
        print(f"\n[SECURE] Personnel Records Found: {len(users)}")
        for u in users:
            print(f" > ID: {u.id:03} | Username: {u.username} | Email: {u.email}")

    def run_diagnostic(self):
        print("\n[AI] Scanning 'uploads' directory for pending DSC images...")
        upload_dir = self.app.config['UPLOAD_FOLDER']
        files = [f for f in os.listdir(upload_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        
        if not files:
            print("[ERROR] No images found in uploads folder.")
            return

        print(f"Found {len(files)} images. Analyzing most recent...")
        latest_file = max([os.path.join(upload_dir, f) for f in files], key=os.path.getctime)
        
        # This calls your actual SkinAnalyzer service
        results = self.analyzer.analyze(latest_file)
        print(f"[OK] Analysis Complete for {os.path.basename(latest_file)}:")
        for key, val in results.items():
            print(f"   - {key.upper()}: {val}")

    def chat_test(self):
        print("\n[CHAT] Enter 'exit' to return to menu.")
        while True:
            user_msg = input("User: ")
            if user_msg.lower() == 'exit': break
            
            # Use the actual chatbot logic
            response = self.chatbot.get_response(user_msg)
            print(f"Assistant: {response}\n")

    def run(self):
        while True:
            self.show_header()
            print("1. List All Personnel (Users)")
            print("2. Run AI Diagnostic (Latest Upload)")
            print("3. Test Chatbot Concierge")
            print("4. Clear System Logs (Database Wipe)")
            print("5. Exit")
            
            cmd = input("\nDERMA_CLI > ")

            if cmd == '1': self.list_personnel()
            elif cmd == '2': self.run_diagnostic()
            elif cmd == '3': self.chat_test()
            elif cmd == '4':
                confirm = input("Are you sure? This wipes all scan history (y/n): ")
                if confirm.lower() == 'y':
                    db.drop_all()
                    db.create_all()
                    print("[OK] Database Reset.")
            elif cmd == '5':
                print("Closing Secure Link...")
                break

if __name__ == "__main__":
    assistant = ConsoleAssistant()
    assistant.run()