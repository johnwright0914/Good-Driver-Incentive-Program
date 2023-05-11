import csv
import datetime
import os
from django.contrib.auth.models import User 
from .models import Profile
import matplotlib.pyplot as plt

# example user
user = "JohnDoe"

# create a dictionary to store the number of password changes for each user
password_changes = {}

# function to log password changes
def log_password_change(user):
    # check if the user already exists in the dictionary
    if user in password_changes:
        # if so, increment the number of password changes
        password_changes[user] += 1
    else:
        # if not, add the user to the dictionary with a count of 1
        password_changes[user] = 1
    
    # log the password change with a timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"{user} changed their password on {timestamp}. Total password changes: {password_changes[user]}"
    print(log_message)

    # write the log message to a CSV file
    with open("password_changes.csv", mode="a", newline="") as csv_file:
        fieldnames = ["user", "timestamp", "password_changes"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if csv_file.tell() == 0:
            writer.writeheader()
        writer.writerow({"user": user, "timestamp": timestamp, "password_changes": password_changes[user]})

def log_application_sent(user, application_type, status):
    # log the application sent with a timestamp, date, and status
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    log_message = f"{user} sent a {application_type} application to the database on {timestamp}. Status: {status}."
    print(log_message)

    # write the log message to a CSV file
    with open("application_log.csv", mode="a", newline="") as csv_file:
        fieldnames = ["user", "application_type", "timestamp", "date", "status"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if csv_file.tell() == 0:
            writer.writeheader()
        writer.writerow({"user": user, "application_type": application_type, "timestamp": timestamp, "date": date, "status": status})



def log_account_deletion(user, user_type):
    # log the account deletion with a timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"{user} deleted a {user_type} account on {timestamp}."
    print(log_message)

    # write the log message to a CSV file
    with open("account_deletions.csv", mode="a", newline="") as csv_file:
        fieldnames = ["user", "user_type", "timestamp"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if csv_file.tell() == 0:
            writer.writeheader()
        writer.writerow({"user": user, "user_type": user_type, "timestamp": timestamp})


# function to log account creation
def log_account_creation(user, user_type):
    # log the account creation with a timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"{user} created a {user_type} account on {timestamp}."
    print(log_message)

    # write the log message to a CSV file
    with open("account_creations.csv", mode="a", newline="") as csv_file:
        fieldnames = ["user", "user_type", "timestamp"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if csv_file.tell() == 0:
            writer.writeheader()
        writer.writerow({"user": user, "user_type": user_type, "timestamp": timestamp})

# function to log login attempts
def log_login_attempts(user, success, ip):
    # log the login attempt with a timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    success_str = "success" if success else "failure"
    log_message = f"{user} attempted to log in on {timestamp} from {ip}. Result: {success_str}"
    print(log_message)
    
    profile = Profile.objects.get(user=user)
    
    if ip not in profile.known_ips:
        profile.known_ips = profile.known_ips + "," + ip
        log_message = f"{user} attempted to log in on {timestamp} from unknown ip {ip}. Result: {success_str}"
        profile.save()
    
    # write the log message to a CSV file
    with open("login_attempts.csv", mode="a", newline="") as csv_file:
        fieldnames = ["user", "ip", "timestamp", "result"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if csv_file.tell() == 0:
            writer.writeheader()
        writer.writerow({"user": user, "ip": ip, "timestamp": timestamp, "result": success_str})

def log_points_removed(user, points):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"{timestamp}: {points} points removed from {user}."
    print(log_message)
    
    with open("points_log.csv", mode="a", newline="") as csv_file:
        fieldnames = ["timestamp", "user", "points"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if csv_file.tell() == 0:
            writer.writeheader()
        writer.writerow({"timestamp": timestamp, "user": user, "points": -points})

def log_points_added(user, points):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"{timestamp}: {points} points added to {user}."
    print(log_message)
    
    with open("points_log.csv", mode="a", newline="") as csv_file:
        fieldnames = ["timestamp", "user", "points"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if csv_file.tell() == 0:
            writer.writeheader()
        writer.writerow({"timestamp": timestamp, "user": user, "points": points})

def points_filter(users):
    with open("points_log.csv", mode="r") as csv_file:
        reader = csv.DictReader(csv_file)
        filtered_users = [row for row in reader if int(row['user']) in users]
    return filtered_users

def log_item_added(name, price):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"{timestamp}: {name} added to catalog with price {price}."
    print(log_message)

    with open("catalog_log.csv", mode="a", newline="") as csv_file:
        fieldnames = ["timestamp", "name", "price", "action"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if csv_file.tell() == 0:
            writer.writeheader()
        writer.writerow({"timestamp": timestamp, "name": name, "price": price, "action": "added"})

def log_item_removed(name):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"{timestamp}: {name} removed from catalog."
    print(log_message)

    with open("catalog_log.csv", mode="a", newline="") as csv_file:
        fieldnames = ["timestamp", "name", "price", "action"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if csv_file.tell() == 0:
            writer.writeheader()
        writer.writerow({"timestamp": timestamp, "name": name, "price": "", "action": "removed"})


def download_logs(start_date, end_date):
    # create a list to store the rows that fall within the date range
    rows_to_download = []

    # open the password_changes.csv file and add rows to the list if they fall within the date range
    with open("password_changes.csv", mode="r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            timestamp = datetime.datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            if start_date <= timestamp.date() <= end_date:
                row["timestamp"] = timestamp.strftime("%m/%d/%Y")
                rows_to_download.append(row)

    # open the account_creations.csv file and add rows to the list if they fall within the date range
    with open("account_creations.csv", mode="r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            timestamp = datetime.datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            if start_date <= timestamp.date() <= end_date:
                row["timestamp"] = timestamp.strftime("%m/%d/%Y")
                rows_to_download.append(row)

    # open the login_attempts.csv file and add rows to the list if they fall within the date range
    with open("login_attempts.csv", mode="r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            timestamp = datetime.datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            if start_date <= timestamp.date() <= end_date:
                row["timestamp"] = timestamp.strftime("%m/%d/%Y")
                rows_to_download.append(row)
    
    # add points log data to the rows_to_download list
    with open("points_log.csv", mode="r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            timestamp = datetime.datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            if start_date <= timestamp.date() <= end_date:
                row["timestamp"] = timestamp.strftime("%m/%d/%Y %H:%M:%S")
                rows_to_download.append(row)

    # add catalog log data to the rows_to_download list
    with open("catalog_log.csv", mode="r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            timestamp = datetime.datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            if start_date <= timestamp.date() <= end_date:
                row["timestamp"] = timestamp.strftime("%m/%d/%Y %H:%M:%S")
                rows_to_download.append(row)

    # write the rows to a new CSV file
    filename = f"logs_{start_date.strftime('%m%d%Y')}_{end_date.strftime('%m%d%Y')}.csv"
    with open(filename, mode="w", newline="") as csv_file:
        fieldnames = ["user", "timestamp", "password_changes", "user_type", "result", "points", "name", "price", "action"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_to_download)
    
    print(f"Logs downloaded to {filename}.")


# log_account_creation(user)
# output: "JohnDoe created an account on 2023-03-27 12:00:00."

# example usage
# log_password_change(user)  # output: "JohnDoe changed their password on 2023-03-16 12:00:00. Total password changes: 1"
# log_password_change(user)  # output: "JohnDoe changed their password on 2023-03-16 12:05:00. Total password changes: 2"


# example usage
   # user = "JohnDoe"
    #log_login_attempts(user, True)  # output: "JohnDoe attempted to log in on 2023-03-27 12:00:00. Result: success"
    # log_login_attempts(user, False)  # output: "JohnDoe attempted to log in on 2023-03-27 12:05:00. Result: failure"

    # write the logs to a new CSV file

    '''# example usage
start_date = datetime.date(2023, 1, 1)
end_date = datetime.date(2023, 2, 15)
download_logs(start_date, end_date)'''