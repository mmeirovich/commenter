from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool

from commenter.core.config import settings
from commenter.models.comment import CommentRequest, CommentResponse


def _build_crew(request: CommentRequest) -> Crew:
    search_tool = SerperDevTool()

    analyst = Agent(
        role="Post Analyst",
        goal="Deeply understand the blog post's topic, main arguments, and target audience.",
        backstory=(
            "You are a senior content analyst with 15 years of experience dissecting blog posts "
            "across tech, science, and culture. You extract the core thesis, identify weak arguments, "
            "and spot what the author got right or wrong."
        ),
        tools=[],
        verbose=False,
        allow_delegation=False,
        llm=settings.openai_model,
    )

    researcher = Agent(
        role="Web Researcher",
        goal="Find recent, authoritative data and counter-examples related to the post's topic.",
        backstory=(
            "You are a diligent researcher who specializes in fast, targeted web searches. "
            "You locate credible sources, recent stats, and contrarian viewpoints that enrich any discussion."
        ),
        tools=[search_tool],
        verbose=False,
        allow_delegation=False,
        llm=settings.openai_model,
    )

    opinion_former = Agent(
        role="Opinion Strategist",
        goal="Formulate a clear, opinionated stance on the post that is well-supported and interesting.",
        backstory=(
            "You are a sharp-tongued but fair commentator who has written thousands of blog comments. "
            "You never sit on the fence — you form a clear point of view, back it with evidence, "
            "and express it concisely."
        ),
        tools=[],
        verbose=False,
        allow_delegation=False,
        llm=settings.openai_model,
    )

    writer = Agent(
        role="Comment Writer",
        goal=(
            "Write the final comment: concise, opinionated, engaging, and where relevant, "
            "include a supporting or contrasting URL."
        ),
        backstory=(
            "You are an expert copywriter who crafts comments that add real value to discussions. "
            "Your comments are never sycophantic — they are direct, insightful, and invite dialogue."
        ),
        tools=[],
        verbose=False,
        allow_delegation=False,
        llm=settings.openai_model,
    )

    content_section = (
        f"CONTENT:\n{request.post_text}"
        if request.post_text
        else "CONTENT: (not provided — infer from the title alone)"
    )
    analyze_task = Task(
        description=(
            f"Analyze the following blog post:\n\n"
            f"TITLE: {request.post_title}\n\n"
            f"{content_section}\n\n"
            "Identify: main thesis, key claims, target audience, notable strengths, and any gaps or errors."
        ),
        expected_output=(
            "A structured analysis with sections: Main Thesis, Key Claims (bullet list), "
            "Strengths, Gaps/Errors, and Audience."
        ),
        agent=analyst,
    )

    research_task = Task(
        description=(
            "Using the analysis above, search the web for:\n"
            "1. Recent data or studies that support or contradict the main claims.\n"
            "2. Alternative viewpoints from credible sources.\n"
            "3. The single most relevant URL to reference in a comment.\n\n"
            "Focus on content published in the last 2 years."
        ),
        expected_output=(
            "A research brief with: key findings (bullet list), contrarian evidence (if any), "
            "and the single best URL to cite."
        ),
        agent=researcher,
        context=[analyze_task],
    )

    opinion_task = Task(
        description=(
            "Based on the post analysis and research findings, decide on a clear stance:\n"
            "- Do you largely agree, disagree, or offer a nuanced view?\n"
            "- What is the single most important point to make?\n"
            "- What tone fits best (constructive, challenging, supportive, skeptical)?"
        ),
        expected_output=(
            "A one-paragraph opinion brief: stance (agree/disagree/nuanced), "
            "the central point to make, supporting evidence, and recommended tone."
        ),
        agent=opinion_former,
        context=[analyze_task, research_task],
    )

    write_task = Task(
        description=(
            "Write the final blog comment. Requirements:\n"
            "- 3–6 sentences, conversational but substantive.\n"
            "- Express the opinion clearly — no hedging.\n"
            "- If a URL was found, include it naturally (not as a bare link).\n"
            "- End with a question or statement that invites the author to respond.\n\n"
            "Also provide:\n"
            "- A one-sentence summary of the comment's stance.\n"
            "- A list of any URLs referenced (empty list if none).\n\n"
            "Return a JSON object with keys: comment (string), summary (string), sources (list of strings)."
        ),
        expected_output=(
            'Valid JSON with keys "comment" (string), "summary" (string), "sources" (list of strings).'
        ),
        agent=writer,
        context=[analyze_task, research_task, opinion_task],
    )

    return Crew(
        agents=[analyst, researcher, opinion_former, writer],
        tasks=[analyze_task, research_task, opinion_task, write_task],
        process=Process.sequential,
        verbose=False,
    )


async def generate_comment(request: CommentRequest) -> CommentResponse:
    import json

    crew = _build_crew(request)
    result = crew.kickoff()

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
        return CommentResponse(
            comment=raw,
            summary="",
            sources=[],
        )
