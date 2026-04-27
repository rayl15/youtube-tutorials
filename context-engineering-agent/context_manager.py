class ContextManager:
    def __init__(self, system_prompt: str, max_history_turns: int = 10):
        self.system_prompt = system_prompt
        self.max_history_turns = max_history_turns
        self.conversation_history = []
        self.task_context = {}

    def set_task_context(self, context: dict):
        """Inject fresh task-specific context each turn."""
        self.task_context = context

    def add_turn(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})

    def build_context(self) -> list:
        """Assembles exactly what the LLM sees. Nothing more."""
        messages = []
        # Only the last N turns — no stale context
        recent = self.conversation_history[-self.max_history_turns:]
        messages.extend(recent)
        return messages

    def build_system_prompt(self) -> str:
        """System prompt + task context, injected fresh every turn."""
        task_section = ""
        if self.task_context:
            task_section = "\n\nCURRENT TASK CONTEXT:\n"
            for key, value in self.task_context.items():
                task_section += f"- {key}: {value}\n"
        return self.system_prompt + task_section

    def extract_relevant(self, tool_result: str, max_tokens: int = 500) -> str:
        """Don't dump full tool results. Extract relevant parts only."""
        # Simple truncation — in production, use an LLM to summarize
        words = tool_result.split()
        if len(words) > max_tokens:
            return " ".join(words[:max_tokens]) + "... [truncated]"
        return tool_result
