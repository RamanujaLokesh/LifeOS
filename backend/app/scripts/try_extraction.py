import logging

from app.ai.extraction import extract_memory_candidates

logging.basicConfig(level=logging.WARNING)  # so failures inside the function are visible


def U(text):
    return {"role": "user", "content": text}


def A(text):
    return {"role": "assistant", "content": text}


# (name, messages, expectation, keyword that should appear in a memory)
CASES = [
    ("project", [U("Remember that I'm working on LifeOS, a personal AI assistant.")], "some", "lifeos"),
    ("decision", [U("I decided to use PostgreSQL instead of MongoDB for the database.")], "some", "postgres"),
    ("preference", [U("I prefer short answers with code examples.")], "some", "short"),
    ("goal", [U("My goal is to finish the LifeOS project in six weeks.")], "some", "lifeos"),
    ("multiple", [U("I'm building LifeOS, I prefer Python over JavaScript, and my teammate Arjun is helping me test it.")], "many", None),
    ("question", [U("What's the capital of France?")], "none", None),
    ("greeting", [U("Hi!")], "none", None),
    ("secret", [U("My OpenAI key is sk-test-1234567890abcdef, please use it.")], "none", None),
    ("assistant_idea", [U("Which database should I use?"), A("I recommend MongoDB for this.")], "none", None),
    ("calendar", [U("Schedule my review for Thursday at 3 PM.")], "none", None),
]


def check(expect, keyword, result):
    if expect == "none":
        return len(result) == 0
    if expect == "many":
        return len(result) >= 2
    found = len(result) >= 1
    if keyword:
        found = found and any(keyword in c.content.lower() for c in result)
    return found


def main():
    passed = 0
    for name, messages, expect, keyword in CASES:
        result = extract_memory_candidates(messages, tz="Asia/Kolkata")
        ok = check(expect, keyword, result)
        passed += ok
        print(f"{'PASS' if ok else 'FAIL'}  {name:15} expected={expect}")
        for c in result:
            print(f"        [{c.category}] {c.content}")
    print(f"\n{passed}/{len(CASES)} passed")


if __name__ == "__main__":
    main()