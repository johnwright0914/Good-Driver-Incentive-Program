import matplotlib.pyplot as plt
import pandas as pd

def generate_password_change_report(start_date, end_date):
    # read password_changes.csv and filter by date range
    df = pd.read_csv("password_changes.csv")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]

    # group by user and count password changes
    user_counts = df.groupby(['user']).size().reset_index(name='counts')
    user_counts = user_counts.sort_values('counts', ascending=False)

    # plot the password change report
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(user_counts['user'], user_counts['counts'])
    ax.set_xlabel('User')
    ax.set_ylabel('Number of Password Changes')
    ax.set_title('Password Change Report')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

def generate_login_attempt_report(start_date, end_date):
    # read login_attempts.csv and filter by date range
    df = pd.read_csv("login_attempts.csv")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]

    # group by user and count login attempts
    user_counts = df.groupby(['user']).size().reset_index(name='counts')
    user_counts = user_counts.sort_values('counts', ascending=False)

    # plot the login attempt report
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(user_counts['user'], user_counts['counts'])
    ax.set_xlabel('User')
    ax.set_ylabel('Number of Login Attempts')
    ax.set_title('Login Attempt Report')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

def generate_application_sent_report(start_date, end_date):
    # read the CSV file
    df = pd.read_csv("application_log.csv")

    # group by date and count the number of applications sent
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]

    # create a line plot of the data
    plt.plot(df.index, df["user"])
    plt.title("Applications Sent")
    plt.xlabel("Date")
    plt.ylabel("Number of Applications")
    plt.show()

def generate_account_creation_report():
    # read the CSV file
    df = pd.read_csv("account_creations.csv")

    # group by date and count the number of accounts created
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.groupby(df["timestamp"].dt.date).count()

    # create a line plot of the data
    plt.plot(df.index, df["user"])
    plt.title("Accounts Created")
    plt.xlabel("Date")
    plt.ylabel("Number of Accounts")
    plt.show()

def generate_account_deletion_report():
    # read the CSV file
    df = pd.read_csv("account_deletions.csv")

    # group by date and count the number of accounts deleted
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.groupby(df["timestamp"].dt.date).count()

    # create a line plot of the data
    plt.plot(df.index, df["user"])
    plt.title("Accounts Deleted")
    plt.xlabel("Date")
    plt.ylabel("Number of Accounts")
    plt.show()

def generate_points_change_report(start_date, end_date):
    # read the CSV file
    df = pd.read_csv("points_log.csv")

    # group by date and count the number of applications sent
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]

    # create a line plot of the data
    plt.plot(df.index, df["user"])
    plt.title("Points Gained or Lost")
    plt.xlabel("Date")
    plt.ylabel("Points")
    plt.show()
