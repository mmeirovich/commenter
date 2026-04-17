import json
from pathlib import Path

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

from commenter.core.config import settings
from commenter.models.comment import CommentRequest, CommentResponse

_CONFIG_DIR = Path(__file__).parent / "config"


@CrewBase
class CommentCrew:
    agents_config = str(_CONFIG_DIR / "agents.yaml")
    tasks_config = str(_CONFIG_DIR / "tasks.yaml")

    @agent
    def analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["analyst"],  # type: ignore[index]
            verbose=False,
            allow_delegation=False,
            llm=settings.openai_model,
        )

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],  # type: ignore[index]
            tools=[SerperDevTool()],
            verbose=False,
            allow_delegation=False,
            llm=settings.openai_model,
        )

    @agent
    def opinion_former(self) -> Agent:
        return Agent(
            config=self.agents_config["opinion_former"],  # type: ignore[index]
            verbose=False,
            allow_delegation=False,
            llm=settings.openai_model,
        )

    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config["writer"],  # type: ignore[index]
            verbose=False,
            allow_delegation=False,
            llm=settings.openai_model,
        )

    @task
    def analyze_task(self) -> Task:
        return Task(config=self.tasks_config["analyze_task"])  # type: ignore[index]

    @task
    def research_task(self) -> Task:
        return Task(config=self.tasks_config["research_task"])  # type: ignore[index]

    @task
    def opinion_task(self) -> Task:
        return Task(config=self.tasks_config["opinion_task"])  # type: ignore[index]

    @task
    def write_task(self) -> Task:
        return Task(config=self.tasks_config["write_task"])  # type: ignore[index]

    @crew
    def build(self) -> Crew:
        return Crew(
            agents=self.agents,  # type: ignore[attr-defined]
            tasks=self.tasks,  # type: ignore[attr-defined]
            process=Process.sequential,
            verbose=False,
        )


async def generate_comment(request: CommentRequest) -> CommentResponse:
    content_section = (
        f"CONTENT:\n{request.post_text}"
        if request.post_text
        else "CONTENT: (not provided — infer from the title alone)"
    )

    result = CommentCrew().build().kickoff(
        inputs={
            "post_title": request.post_title,
            "content_section": content_section,
        }
    )

    raw = str(result).strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        data: dict[str, object] = json.loads(raw)
        return CommentResponse(
            comment=str(data.get("comment", raw)),
            summary=str(data.get("summary", "")),
            sources=list(data.get("sources", [])),  # type: ignore[arg-type]
        )
    except json.JSONDecodeError:
        return CommentResponse(comment=raw, summary="", sources=[])
