from llm import chat


SYSTEM = """You are a coding assistant inside an educational agent loop.
Be concise. Ask for missing code when needed. Do not pretend you edited files yet."""


def main() -> None:
    messages = [{"role": "system", "content": SYSTEM}]

    while True:
        text = input("You > ").strip()
        if text in {"/exit", "/quit"}:
            break
        if not text:
            continue

        messages.append({"role": "user", "content": text})
        reply = chat(messages)
        messages.append(reply)
        print("\nAgent >", reply.get("content") or "", "\n")


if __name__ == "__main__":
    main()
