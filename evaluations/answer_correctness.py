import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent"))

from agent import agent
from datasets import dataset
from evaluations_models import eval_model

from deepeval import evaluate
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams

EVALUATION_STEPS = [
    "From the expected output, identify the outcome: a refund ticket was issued, "
    "a refund was denied, the user was asked for or to re-check their username, "
    "or only information was given.",
    "Check that the actual output reaches the same outcome. If the outcome is "
    "opposite (a refund issued instead of denied, or the reverse), score very low.",
    "If the expected output names a refund amount or specific items, the actual "
    "output must state the same amount and the same items. A different amount "
    "or a different item list is a major error.",
    "If the expected output gives a reason (outside 30 days, item not purchased, "
    "no account found), the actual output should give the same reason or an "
    "equivalent one.",
    "Ignore wording, tone, and harmless extra detail such as purchase dates or a "
    "statement that no ticket was issued. Do not ignore amounts, items, or outcome.",
]


def main():
    test_cases = build_test_cases()
    evaluate(test_cases=test_cases, metrics=[build_metric()])


def build_metric():
    return GEval(
        name="Answer Correctness",
        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
            SingleTurnParams.EXPECTED_OUTPUT,
        ],
        evaluation_steps=EVALUATION_STEPS,
        threshold=0.8,
        model=eval_model,
    )


def build_test_cases():
    test_cases = []
    for golden in dataset.goldens:
        try:
            test_cases.append(build_test_case(golden))
        except Exception as error:
            print(f"SKIPPED: {golden.input!r} -> {error}")
    return test_cases


def build_test_case(golden):
    response = agent.invoke(
        {"messages": [{"role": "user", "content": golden.input}]},
        config={"configurable": {"thread_id": str(uuid4())}},
    )
    return LLMTestCase(
        input=golden.input,
        actual_output=response["structured_response"].answer,
        expected_output=golden.expected_output,
    )


if __name__ == "__main__":
    main()
