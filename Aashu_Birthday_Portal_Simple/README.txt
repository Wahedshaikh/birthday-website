AASHU BIRTHDAY PORTAL
======================

Main files:
1. app.py              -> Python/Flask backend + database + email
2. templates/index.html -> Complete website (HTML + CSS + JavaScript)
3. requirements.txt     -> install dependencies

RUN:
1. Open this folder in VS Code.
2. Open Terminal.
3. Run:
   pip install -r requirements.txt
4. Run:
   python app.py
5. Open:
   http://127.0.0.1:5000

ADMIN:
Open:
http://127.0.0.1:5000/admin

Default password:
aashu123

IMPORTANT:
Change the admin password from the Admin page.

WHATSAPP:
The final surprise opens WhatsApp with a prewritten birthday message and lets
the birthday girl choose Hadi's chat. She reviews the text and taps Send herself;
the message is never sent automatically.

GLOBAL EDITS:
All website content is stored in SQLite database (birthday.db).
Therefore, when the same hosted website is opened from another phone/laptop,
the saved admin changes are shown there too.

SURPRISE EXPERIENCE:
The birthday surprise is split into individual screens with Previous/Next
navigation. It plays short browser-generated sound effects for button clicks,
balloon pops, candle blowing, and cake cutting. It does not use spoken messages
or request microphone access. The Bestie Masti screen includes a spin-the-wheel
birthday dare game with a confetti celebration.

PUBLIC LINK:
After testing locally, deploy this Flask project to a Python-compatible host
with persistent storage. Keep birthday.db persistent so admin edits remain saved.
