Purrfect Homes is a Django-based web application developed for a university course. It aims to support cat adoption by providing a platform where users can browse adoptable cats, submit adoption requests, read blog posts, explore events, make donations, and where staff can manage requests.
Main Features:

    🏠 Home Page
    🐱 Cats: list and detail views for adoptable cats
    📄 Adoption Requests: create and manage requests
    👤 User Profile
    🏢 Shelters: list of partner shelters
    📝 Blog: articles and updates
    📅 Events: cat-related events and initiatives
    💝 Donations: support shelters with online donations
    🛠️ Staff Tools: approve/reject adoption requests

Project Setup:

    git clone https://github.com/Alle-marchio/purrfect-homes.git
    cd purrfect-homes
    python -m venv env
    source env/bin/activate  # or env\Scripts\activate on Windows
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver

