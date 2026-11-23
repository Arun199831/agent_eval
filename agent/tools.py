import os

from langchain.tools import tool
from data import users_data
from dotenv import load_dotenv
import logging
from objects import PurchaseItem
from datetime import date

load_dotenv()


@tool
def get_user_purchase_history(user: str) -> dict:
    """this tool takes username and returns a dict of the users purchase history if the user exists"""
    logging.info(f"using get_user_purchase_history tool to get user :{user} ")
    if users_data.get(user):
        return users_data[user]
    return {"status": "there is no data for this user "}


@tool
def calculate_right_refund(user: str, items: list[PurchaseItem]) -> str:
    """this tool takes a list of items to be returned and the username and will return how much the refund worth"""
    logging.info(f"using calculate_right_refund tool to calculate {user} refund ")
    if users_data.get(user):
        total_refund = 0
        for item in items:
            if users_data[user].get(item.name):
                total_refund += users_data[user][item.name]["price"]
        return f"the value of refund is : {total_refund}"
    return {"status": "there was no user found "}


@tool
def issue_refund_ticket(user: str, refund_amount: int) -> str:
    """this tool sends a ticket to the right team to return the refund"""
    logging.info(f"using the issue_refund_ticket tool for user : {user} ")
    return (
        f"a refund ticket has been issued successfully with amount of {refund_amount}"
    )


from datetime import date


@tool
def get_today_date() -> str:
    """Return today's date in YYYY-MM-DD format. Takes no arguments."""

    logging.info("Using the date tool")

    return os.getenv("AGENT_TODAY", date.today().isoformat())
