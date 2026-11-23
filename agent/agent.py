from models import model
from tools import (
    get_user_purchase_history,
    calculate_right_refund,
    issue_refund_ticket,
    get_today_date,
)
from dotenv import load_dotenv
from prompts import agent_system_prompt
from objects import Answer, PurchaseItem
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import HumanMessage
from uuid import uuid4

load_dotenv()

agent = create_agent(
    model=model,
    system_prompt=agent_system_prompt,
    tools=[
        calculate_right_refund,
        get_user_purchase_history,
        calculate_right_refund,
        get_today_date,
        issue_refund_ticket,
    ],
    response_format=Answer,
    checkpointer=InMemorySaver(),
)


def run_conversation():
    config = {"configurable": {"thread_id": str(uuid4())}}
    text = "i would like to have refund"
    print(text)
    question = HumanMessage(
        content="I want to return a book and a calculator I purchased from your store"
    )
    conversation = True

    while conversation:
        print("Before agent.invoke")

        response = agent.invoke({"messages": [question]}, config=config)

        print("After agent.invoke")
        print("Agent:", response["structured_response"].answer)
        response = agent.invoke({"messages": [question]}, config=config)

        structured_response = response["structured_response"]

        # print(structured_response.answer)

        conversation = structured_response.conversation

        if conversation:
            user_input = input("reply: \n")
            question = HumanMessage(content=user_input)


if __name__ == "__main__":
    run_conversation()
