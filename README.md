# LojaTech Support Agent 🤖

An AI customer support agent built in Python, simulating a real returns-handling
workflow: it looks up orders, applies a business policy, and escalates to a human
when it can't resolve something on its own — built on the classic agent loop:
Think → Act → Observe.

Built while following a guided exercise on AI agents (function calling, the
Think → Act → Observe loop, memory, and tool use). I debugged and adapted the
code myself — fixing environment variable issues, a deprecated model name, and
a few bugs along the way — to get it running end-to-end on the free Gemini API
tier.

## 📖 What I Learned

- Function calling / tool use with the Gemini API (`google-genai`)
- The agent loop: Think → Act → Observe
- Keeping business rules in code, not just in the prompt (so the model can't be talked out of them)
- Multi-turn memory with a chat session
- Handling API rate limits with retries and backoff
- Writing a system prompt to constrain agent behavior
- Debugging real-world issues: environment variables, deprecated model names,
  typos in API calls

## 📁 Project

A single agent, `agent.py`, with 3 tools:

1. **get_order** — looks up an order by its number
2. **request_refund** — requests a refund; the return policy (delivered only, within 30 days, up to €100 auto-approved) is enforced in code
3. **open_human_ticket** — escalates to a human when the agent can't resolve the case

## 💻 How to Run

### 1. Get a free API key
Go to [aistudio.google.com](https://aistudio.google.com), sign in with a Google
account, and create a free API key under "Get API key". No credit card needed.

### 2. Install and configure

```bash
pip install -r requirements.txt
export GEMINI_API_KEY="your-key-here"
export GEMINI_MODEL="gemini-3.5-flash-lite"
```

### 3. Run

```bash
python agent.py
```

## 📊 Example

```
Customer: A100, came with a defect
  [step 1] ACT: get_order({'order_id': 'A100'})
  [step 1] OBSERVE: {'customer': 'Marta', 'product': 'Headphones X1', ...}
  [step 2] ACT: request_refund({'order_id': 'A100', 'reason': 'Came with a defect'})
  [step 2] OBSERVE: {'approved': True, 'amount_refunded': 59.9, ...}
Assistant: Your refund for order A100 has been approved...
```

## 🛠 Technologies

- Python 3.x
- [google-genai](https://pypi.org/project/google-genai/) (Gemini API, free tier)
- Editor: Visual Studio Code

## ⚠️ Known Limitations

- Simulated in-memory data — no real database
- Memory lasts only for the current chat session
- No customer authentication — anyone can look up any order
- Depends on the free tier's rate limits (requests per minute/day)

## 🎓 Real-World Use Cases

- Customer support automation for e-commerce
- Any workflow where a business policy must be enforced reliably, with an AI
  handling the conversational layer on top

## 👤 Author

**João Mendes**
Student Developer | Building Projects & Learning
Porto, Portugal
GitHub: [joao-mendes-lab](https://github.com/joao-mendes-lab)

## 🎯 Project Status

✅ Complete — 5 test scenarios passing

---

Made with ❤️ using Python and the Gemini API.