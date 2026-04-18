import os
import streamlit as st
from dotenv import load_dotenv
from strands import Agent
from mcp_config import get_github_mcp_client, get_filesystem_mcp_client
from model_config import load_model

load_dotenv()

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="GitHub Repo Analyst",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 GitHub Repository Analyst")
st.caption("Powered by Strands Agents + MCP")

# ── Load system prompt ────────────────────────────────────────
with open("prompts/system_prompt.txt", "r") as f:
    system_prompt = f.read()

# ── Sidebar — Model Switcher ──────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")

    provider = st.selectbox(
        "Model Provider",
        ["Ollama (Local)", "Anthropic API", "AWS Bedrock"],
        index=0
    )

    # Show relevant info per provider
    if provider == "Ollama (Local)":
        st.success("✅ Free — runs locally")
        st.caption("Make sure Ollama is running on localhost:11434")

    elif provider == "Anthropic API":
        st.warning("💳 Requires Anthropic API key in .env")
        st.caption("Uses claude-3-5-haiku — fast and cheap")

    elif provider == "AWS Bedrock":
        st.warning("☁️ Requires AWS credentials in .env")
        st.caption("Uses Claude Haiku via Bedrock")

    st.divider()
    st.caption("GitHub token required in .env for all providers")

# ── Session state for conversation ───────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = None
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False
if "github_mcp" not in st.session_state:
    st.session_state.github_mcp = None
if "filesystem_mcp" not in st.session_state:
    st.session_state.filesystem_mcp = None

# ── Main UI ───────────────────────────────────────────────────
repo_url = st.text_input(
    "GitHub Repository URL",
    placeholder="https://github.com/facebook/react"
)

analyze_btn = st.button("🚀 Analyze Repository", use_container_width=True)

# ── Analysis ──────────────────────────────────────────────────
if analyze_btn:
    if not repo_url.strip():
        st.warning("Please enter a GitHub repository URL.")
    else:
        st.session_state.messages = []
        st.session_state.analyzed = False

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("🤖 Agent Thinking")
            thought_box = st.empty()
            thoughts = []

        with col2:
            st.subheader("📄 Final Report")
            report_box = st.empty()
            report_box.info("Report will appear here once analysis is complete...")

        with st.spinner(f"Starting MCP servers with {provider}..."):
            try:
                model = load_model(provider)

                github_mcp = get_github_mcp_client()
                filesystem_mcp = get_filesystem_mcp_client()

                github_mcp.__enter__()
                filesystem_mcp.__enter__()

                github_tools = github_mcp.list_tools_sync()
                filesystem_tools = filesystem_mcp.list_tools_sync()

                thoughts.append(f"✅ Provider: {provider}")
                thoughts.append(f"\n✅ GitHub MCP tools loaded:")
                for t in github_tools:
                    thoughts.append(f"   → {t.tool_name}")
                thoughts.append(f"\n✅ Filesystem MCP tools loaded:")
                for t in filesystem_tools:
                    thoughts.append(f"   → {t.tool_name}")
                thought_box.code("\n".join(thoughts), language="markdown")

                agent = Agent(
                    model=model,
                    system_prompt=system_prompt,
                    tools=[*github_tools, *filesystem_tools]
                )

                # Store in session state for conversation mode
                st.session_state.agent = agent
                st.session_state.github_mcp = github_mcp
                st.session_state.filesystem_mcp = filesystem_mcp
                st.session_state.analyzed = True

                response = agent(
                    f"Analyze this GitHub repository and save a full report: {repo_url}"
                )

                report_text = str(response)
                report_box.markdown(report_text)

                # Store initial message in history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": report_text
                })

                # Download button
                repo_name = repo_url.replace("https://github.com/", "").replace("/", "_")
                report_path = f"reports/{repo_name}_report.md"

                if os.path.exists(report_path):
                    with open(report_path, "r") as f:
                        report_content = f.read()
                    st.download_button(
                        label="⬇️ Download Report",
                        data=report_content,
                        file_name=f"{repo_name}_report.md",
                        mime="text/markdown",
                        use_container_width=True
                    )

            except Exception as e:
                st.error(f"Something went wrong: {e}")

# ── Conversation Mode ─────────────────────────────────────────
if st.session_state.analyzed and st.session_state.agent:
    st.divider()
    st.subheader("💬 Chat with Agent about this Repo")

    # Display chat history
    for msg in st.session_state.messages[1:]:  # skip initial report
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Ask a followup question about the repo...")

    if user_input:
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.agent(user_input)
                    reply = str(response)
                    st.markdown(reply)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": reply
                    })
                except Exception as e:
                    st.error(f"Error: {e}")