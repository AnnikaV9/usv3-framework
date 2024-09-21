import traceback
import asyncio
import usv3.bot

if __name__ == "__main__":
    try:
        bot = usv3.bot.Bot()
        asyncio.run(bot.main())

    except KeyboardInterrupt:
        raise SystemExit

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        raise SystemExit
