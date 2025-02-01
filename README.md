# Learnwise

## Description
**Learnwise** is a web application built with **Django** aimed at connecting learners and mentors. The platform allows users to create profiles, follow others, engage in educational content, and schedule video sessions. It is designed to provide a collaborative learning environment with features for social interaction, content sharing, and mentorship.

## Features
- **User Roles**: Two types of users—learners and mentors.
- **Profile Management**: Create and manage profiles for both learners and mentors.
- **Follow/Unfollow**: Follow mentors and view followers/following lists.
- **Content Interaction**: Like, comment, and save posts.
- **Search & Filter**: Search and filter users based on specific criteria.
- **Video Conferencing**: Schedule and participate in video calls for mentorship sessions.
- **Ratings & Reviews**: Rate and review mentors.
- **Location-Based Features**: Users can search for mentors or learners based on location.
- **Messaging**: Send and receive messages between users.
- **Tags**: Categorize and search content using tags.

## Requirements
- Dependencies as listed in `requirements.txt`

## Setup and Installation

### Step 1: Clone the Repository
Clone the repository to your local machine using the following command:

```bash
git clone https://github.com/your-username/learnwise.git
```

### Step 2: Create a Virtual Environment
Create a virtual environment for the project to isolate dependencies:

#### For Windows:
```bash
python -m venv venv
```

#### For macOS/Linux:
```bash
python3 -m venv venv
```

### Step 3: Activate the Virtual Environment
Activate the virtual environment:

#### For Windows:
```bash
venv\Scripts\activate
```

#### For macOS/Linux:
```bash
source venv/bin/activate
```

### Step 4: Install Dependencies
Install the necessary dependencies by running the following command:

```bash
pip install -r requirements.txt
```

### Step 5: Setup the Database
Run migrations to set up the database schema:

```bash
python manage.py migrate
```

### Step 6: Run the Development Server
To start the Django development server, run:

```bash
python manage.py runserver
```

You can now access the application by navigating to [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your web browser.

## Contributing
We welcome contributions! If you'd like to contribute to Learnwise, please follow these steps:

1. **Fork** the repository.
2. **Create a new branch**:  
   ```bash
   git checkout -b feature-branch
   ```
3. **Make your changes**.
4. **Commit your changes**:  
   ```bash
   git commit -am 'Add new feature'
   ```
5. **Push to the branch**:  
   ```bash
   git push origin feature-branch
   ```
6. **Open a pull request**.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact
For any queries or support, feel free to reach out at **aayushparajuli23@gmail.com**.

