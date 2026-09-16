from llm import chat


def main() -> None:
    task = input("You > ").strip()
    if not task:
        return

    message = chat(
        [
            {
                "role": "system",
                "content": "You are a concise coding assistant. Explain your reasoning through concrete engineering facts.",
            },
            {"role": "user", "content": task},
        ]
    )
    print("\nAgent >", message.get("content") or "")


if __name__ == "__main__":
    main()
