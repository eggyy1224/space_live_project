"""LangGraph workflow for autonomous director mode."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional, TypedDict

import httpx
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph

logger = logging.getLogger(__name__)


class DirectorState(TypedDict, total=False):
    """State object for DirectorGraph."""

    user_text: Optional[str]
    messages: List[BaseMessage]
    plan: Dict[str, Any]
    result: Dict[str, Any]


class DirectorGraph:
    """Autonomous director workflow orchestrating dialogue and cinematics."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000/api",
        llm: Optional[ChatGoogleGenerativeAI] = None,
    ) -> None:
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url)
        self.llm = llm or ChatGoogleGenerativeAI(model="models/gemini-pro")
        self.app = self._build_graph()

    def _build_graph(self):
        sg = StateGraph(DirectorState)
        sg.add_node("analyze", self._analyze_input)
        sg.add_node("execute", self._execute_plan)
        sg.set_entry_point("analyze")
        sg.add_edge("analyze", "execute")
        sg.add_edge("execute", END)
        return sg.compile()

    async def run(self, text: str) -> Dict[str, Any]:
        state: DirectorState = {
            "user_text": text,
            "messages": [HumanMessage(content=text)],
        }
        return await self.app.astart(state)

    async def _analyze_input(self, state: DirectorState) -> DirectorState:
        """Use LLM to decide dialogue and cinematic actions."""
        prompt = (
            "你是一個電影導演AI，接收對話或場景描述後決定適合的角色台詞、攝影機角度、"
            "情緒及音效，以 JSON 格式輸出指令。輸入: {text}"
        )
        try:
            response = await self.llm.ainvoke(
                prompt.format(text=state.get("user_text", ""))
            )
            plan = json.loads(response.content)
        except Exception as e:  # pragma: no cover - fallback for malformed LLM output
            logger.warning("解析計畫失敗: %s", e)
            # 簡易預設計畫
            plan = {
                "dialogue": state.get("user_text", ""),
                "camera": {"pitch": 0, "yaw": 0, "roll": 0, "duration": 1.0},
            }
        state["plan"] = plan
        state.setdefault("messages", []).append(AIMessage(content=str(plan)))
        return state

    async def _execute_plan(self, state: DirectorState) -> DirectorState:
        """Send generated plan to backend control APIs."""
        plan = state.get("plan", {})
        try:
            if dialogue := plan.get("dialogue"):
                await self.client.post(
                    "/control/send-message", json={"content": dialogue}
                )
            if bgm := plan.get("bgm") or plan.get("sfx"):
                await self.client.post(
                    "/control/background-audio",
                    json={"bgmUrl": plan.get("bgm"), "sfxUrl": plan.get("sfx")},
                )
            if camera := plan.get("camera"):
                await self.client.post("/control/camera/transition", json=camera)
            if emotion := plan.get("emotion"):
                await self.client.post(
                    "/control/emotion-trajectory",
                    json=emotion,
                )
            if state_update := plan.get("state"):
                await self.client.post(
                    "/control/broadcast",
                    json={"type": "director-state", "payload": state_update},
                )
        except Exception as e:  # pragma: no cover - network failure
            logger.error("執行導演計畫時失敗: %s", e)
        state["result"] = plan
        return state
