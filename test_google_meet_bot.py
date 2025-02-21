from src.google_meet.google_meet_bot import GoogleMeetBot
import asyncio

async def main():
    google_meet_link = "https://meet.google.com/ahh-esnc-xav"
    profile_path = r"C:\Users\Email.LIT\AppData\Local\Google\Chrome\User Data"

    bot = GoogleMeetBot(google_meet_link, profile_path, 0)
    bot.connect_to_meet()
    member_names = bot.get_memeber_names()
    bot.disconnect()


if __name__ == "__main__":
    asyncio.run(main())