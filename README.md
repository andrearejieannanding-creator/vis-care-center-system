# vis-care-center-system
Learner Profiling and Referral System for Victoria Integrated School CARE Center
🏫 Victoria Integrated School - CARE Center System

An offline-first Learner Profiling, Teacher Referral, and Anecdotal Record Management System built for school guidance counselors and care personnel. Designed to support 1,000+ learner records with local SQLite storage.

🔒 Data Privacy Act (R.A. 10173) Compliance

100% Local Storage: All student data is stored locally in an SQLite database file (care_center.db) on the machine running the app.

Passcode Protection: Built-in passcode lock screen (1234 default) to prevent unauthorized access when left unattended.

🚀 How to Run locally

Ensure Python 3.x is installed on your computer.

Download or clone this repository.

Run the application:

python app.py


📊 CSV Format for SF1 Batch Import

To batch import your 1,000 learners, create a .csv file with the exact column headers below:

lrn,name,grade,section,gender,guardian,contact
109823456701,"Dela Cruz, Juan",7,Rizal,Male,"Maria Dela Cruz",09171234567
109823456702,"Santos, Maria",7,Rizal,Female,"Jose Santos",09187654321
