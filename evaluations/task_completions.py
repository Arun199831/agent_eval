import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent"))

from agent import agent
from datasets import dataset
from evaluations_models import eval_model

from deepeval.metrics import TaskCompletionMetric
from deepeval.integrations.langchain import CallbackHandler

SUCCESSFUL_TASK_DESCRIPTION = """
The agent is a refund-support assistant. Judge the run ONLY against the one
scenario below that matches the user's message. Ignore the other scenarios.

Scenario A - no username given:
  Success = the agent asks the user for their username and does nothing else.

Scenario B - username given, user wants information only (e.g. what they purchased):
  Success = the agent answers from the purchase records and issues no refund ticket.
  Telling the user about a refund is NOT required in this scenario.

Scenario C - username given, user requests a refund:
  Success = a ticket is issued only for requested items that were actually purchased
  and were bought within 30 days before the date returned by the date tool (and not
  in the future). Nothing else is refunded. The agent tells the user whether a
  refund was issued and, if not, why.

Scenario D - username given but no records are found for it:
  Success = no ticket is issued, and the agent tells the user it could not find
  an account or purchase records for that username. Either "account not found"
  or "no purchase history found for that username" counts. Asking the user to
  re-check or re-enter the username is fine and should not be penalised.
"""

metrics = [
    TaskCompletionMetric(
        threshold=0.8,
        model=eval_model,
        task=SUCCESSFUL_TASK_DESCRIPTION,
        include_reason=True,
    )
]


for golden in dataset.evals_iterator(metrics=metrics):
    response = agent.invoke(
        {"messages": [{"role": "user", "content": golden.input}]},
        config={
            "configurable": {"thread_id": str(uuid4())},
            "callbacks": [CallbackHandler()],
        },
    )
