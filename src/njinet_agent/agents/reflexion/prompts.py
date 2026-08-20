from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)

draft_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are an expert researcher.\n"
                "Provide a detailed answer of at most 250 words. "
                "Reflect critically on it and recommend search queries "
                "that would improve it."
            ),
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

revise_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are an expert researcher.\n"
                "Revise the previous answer using the search results and critique. "
                "Keep it under 250 words, cite sources numerically, "
                "and add a References section."
            ),
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)
