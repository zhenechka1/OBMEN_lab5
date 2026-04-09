from bot.planner_bot import PlannerBot

TOKEN = "..."


def main():
    planner_bot = PlannerBot(TOKEN)
    planner_bot.run()


if __name__ == "__main__":
    main()
