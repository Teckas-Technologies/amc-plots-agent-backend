**Prerequisite:-**

1. Install python3

**Steps to execute clarus backend server:-**

1. Clone this repository

    `git clone git@github.com:hsk77761/AI_Clarus.git`

2. First you need to create your virtual environment using below cmd:-

    `python -m venv venv`

3. Then activate your venv using below cmd:-

    `.\venv\Scripts\Activate`

4. Install neccessary python packages using below cmd:-

    `pip install -r requirements.txt`

5. Configure your OpenAI API key in .env file

    `SECRET_KEY="YOUR_BACKEND_APP_SECRET_KEY"` 
    `OPENAI_API_KEY="YOUR_API_KEY"`
    Note:- Contact Immanuel John for above details.

6. Run your backend app using below cmd:-

    `python app.py`
