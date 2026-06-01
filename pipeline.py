from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain
from vector_store import store_research, retrieve_relevant_context

def run_research_pipeline(topic: str) -> dict:
    state = {}

    # Step 1 - Search
    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    state["search_results"] = search_result['messages'][-1].content

    # Step 2 - Scrape
    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })
    state['scraped_content'] = reader_result['messages'][-1].content

    # ✨ NEW — Store in vector DB
    store_research(
        topic=topic,
        content=state['scraped_content'],
        source="scraped_web"
    )
    store_research(
        topic=topic,
        content=state['search_results'],
        source="search_results"
    )

    # ✨ NEW — Retrieve relevant chunks via RAG
    rag_context = retrieve_relevant_context(
        topic=topic,
        query=f"key facts, findings and insights about {topic}"
    )

    # Step 3 - Write using RAG context
    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"SCRAPED CONTENT:\n{state['scraped_content']}\n\n"
        f"MOST RELEVANT CHUNKS (via RAG):\n{rag_context}"  # ✨ injected
    )
    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    # Step 4 - Critic
    state["feedback"] = critic_chain.invoke({"report": state["report"]})

    return state

if __name__ == "__main__":
    topic = input("\nEnter a research topic: ")
    run_research_pipeline(topic)