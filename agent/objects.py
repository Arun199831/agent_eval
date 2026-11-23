from pydantic import BaseModel, Field


class Answer(BaseModel):
    answer: str = Field(description="the answer which is needed for question")
    conversation: bool = Field(
        description="this is a indicator if conversation should still continue or not \
                             if agent made decision about refund this should be false orelse if agent need \
                             more info it should be true "
    )


class PurchaseItem(BaseModel):
    name: str = Field(description="name of the item purchased")
