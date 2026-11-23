import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent"))

from agent import agent
from datasets import dataset
from evaluations_models import eval_model
from tools import (
    calculate_right_refund,
    get_today_date,
    get_user_purchase_history,
    issue_refund_ticket,
)

from deepeval import evaluate
from deepeval.metrics import ArgumentCorrectnessMetric
from deepeval.test_case import LLMTestCase, ToolCall

AGENT_TOOLS = [
    get_user_purchase_history,
    get_today_date,
    calculate_right_refund,
    issue_refund_ticket,
]

SHOW_CALLS = True  # prints what the judge receives; set False once verified


def main():
    descriptions = describe_tools(AGENT_TOOLS)
    test_cases = build_test_cases(descriptions)
    metrics = [
        ArgumentCorrectnessMetric(threshold=0.8, model=eval_model, include_reason=True)
    ]
    evaluate(test_cases=test_cases, metrics=metrics)


def build_test_cases(descriptions):
    test_cases = []  # Apple Rule: default before the loop
    for golden in dataset.goldens:
        try:
            test_cases.append(build_test_case(golden, descriptions))
        except Exception as error:
            print(f"SKIPPED: {golden.input!r} -> {error}")
    return test_cases


def build_test_case(golden, descriptions):
    response = agent.invoke(
        {"messages": [{"role": "user", "content": golden.input}]},
        config={"configurable": {"thread_id": str(uuid4())}},
    )
    tools_called = extract_tool_calls(response, descriptions)

    if SHOW_CALLS:
        show_calls(golden.input, tools_called)

    return LLMTestCase(
        input=golden.input,
        actual_output=response["structured_response"].answer,
        tools_called=tools_called,
    )


def extract_tool_calls(response, descriptions):
    outputs = collect_tool_outputs(response)
    tools_called = []
    for message in response["messages"]:
        for call in getattr(message, "tool_calls", None) or []:
            tools_called.append(
                ToolCall(
                    name=call["name"],
                    description=descriptions.get(call["name"]),
                    input_parameters=call["args"],
                    output=outputs.get(call["id"]),
                )
            )
    return tools_called


def collect_tool_outputs(response):
    outputs = {}
    for message in response["messages"]:
        if getattr(message, "type", None) == "tool":
            outputs[message.tool_call_id] = message.content
    return outputs


def describe_tools(tools):
    descriptions = {}
    for tool in tools:
        name = getattr(tool, "name", None) or tool.__name__
        descriptions[name] = getattr(tool, "description", None) or tool.__doc__
    return descriptions


def show_calls(user_input, tools_called):
    print(user_input)
    for call in tools_called:
        print("   ", call.name, call.input_parameters, "->", call.output)


if __name__ == "__main__":
    main()
