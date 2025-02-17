from src.google_meet.google_meet_bot import GoogleMeetBot


if __name__ == "__main__":
    google_meet_link = "https://meet.google.com/ugg-mmxu-qfx"
    profile_path = r"C:\Users\Email.LIT\AppData\Local\Google\Chrome\User Data"

    bot = GoogleMeetBot(google_meet_link, profile_path)
    member_names = bot.get_memeber_names()
    pass