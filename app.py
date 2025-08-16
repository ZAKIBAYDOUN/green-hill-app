import json
from pathlib import Path
from typing import Optional, List

import pandas as pd
import streamlit as st
import yaml
from pydantic import BaseModel, Field, SecretStr, field_validator
from dotenv import load_dotenv
import os

# --------- Bootstrapping ---------
st.set_page_config(page_title="Workspace", page_icon="🗂️", layout="wide")
load_dotenv(override=False)

# --------- Config schema (edit to your needs) ---------
class AppConfig(BaseModel):
    project_name: str = Field("My Workspace", description="Display name")
    api_url: str = Field("https://api.example.com", description="Base API URL")
    api_key: Optional[SecretStr] = Field(default=None, description="Optional secret API key")
    model_name: str = Field("gpt-4o-mini", description="Model or engine")
    temperature: float = Field(0.2, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(512, ge=1, le=4096, description="Token limit")
    threshold: float = Field(0.5, ge=0.0, le=1.0, description="Generic threshold")
    tags: List[str] = Field(default_factory=lambda: ["default"], description="Free-form tags")
    enable_advanced: bool = Field(False, description="Toggle advanced features")

    @field_validator("api_key", mode="before")
    @classmethod
    def default_api_key(cls, v):
        # Pull from env if not provided
        if v in (None, "", "null"):
            env_key = os.getenv("API_KEY") or os.getenv("OPENAI_API_KEY")
            return SecretStr(env_key) if env_key else None
        return v

# --------- Session state helpers ---------
def get_state():
    if "config" not in st.session_state:
        st.session_state.config = AppConfig()  # default
    if "inputs" not in st.session_state:
        st.session_state.inputs = {"text": "", "uploaded_name": None, "uploaded_text": ""}
    if "outputs" not in st.session_state:
        st.session_state.outputs = []  # list of dicts
    return st.session_state

def save_result(name: str, content: str, meta: dict):
    st.session_state.outputs.append(
        {"name": name, "content": content, "meta": meta}
    )

def export_config_button(cfg: AppConfig):
    data = cfg.model_dump(mode="json")
    # Don’t serialize secret value directly
    if cfg.api_key:
        data["api_key"] = "***stored_in_env_or_runtime***"
    st.download_button(
        "⬇️ Download config (YAML)",
        data=yaml.safe_dump(data, sort_keys=False).encode("utf-8"),
        file_name="config.yaml",
        mime="text/yaml",
        use_container_width=True,
    )

def export_results_button():
    if not st.session_state.outputs:
        st.info("No results to export yet.")
        return
    df = pd.DataFrame(st.session_state.outputs)
    st.download_button(
        "⬇️ Download results (CSV)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="results.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.download_button(
        "⬇️ Download results (JSON)",
        data=json.dumps(st.session_state.outputs, ensure_ascii=False, indent=2),
        file_name="results.json",
        mime="application/json",
        use_container_width=True,
    )

# --------- UI: Sidebar for variables ---------
def sidebar_config(cfg: AppConfig) -> AppConfig:
    st.sidebar.header("Variables")
    st.sidebar.caption("Centralized configuration. Save/Load below.")

    with st.sidebar.expander("Project", expanded=True):
        project_name = st.text_input("Project name", value=cfg.project_name)
        tags = st.text_input("Tags (comma-separated)", value=",".join(cfg.tags))

    with st.sidebar.expander("Model & API", expanded=True):
        api_url = st.text_input("API URL", value=cfg.api_url)
        model_name = st.text_input("Model name", value=cfg.model_name)
        temperature = st.slider("Temperature", 0.0, 2.0, value=cfg.temperature, step=0.05)
        max_tokens = st.number_input("Max tokens", 1, 4096, value=cfg.max_tokens, step=16)
        threshold = st.slider("Threshold", 0.0, 1.0, value=cfg.threshold, step=0.05)
        # API key entry: avoids storing in downloads
        api_key_input = st.text_input(
            "API key (not saved to file)", type="password", value=cfg.api_key.get_secret_value() if cfg.api_key else ""
        )
        enable_advanced = st.toggle("Enable advanced", value=cfg.enable_advanced)

    # Load config
    with st.sidebar.expander("Save / Load", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            export_config_button(cfg)
        with col2:
            export_results_button()
        uploaded_cfg = st.file_uploader("Load config (YAML/JSON)", type=["yaml", "yml", "json"], label_visibility="collapsed")
        if uploaded_cfg is not None:
            try:
                raw = uploaded_cfg.read()
                try:
                    data = yaml.safe_load(raw)
                except Exception:
                    data = json.loads(raw)
                new_cfg = AppConfig(**data)
                # Preserve transient API key if set via input
                if api_key_input:
                    new_cfg.api_key = SecretStr(api_key_input)
                st.session_state.config = new_cfg
                st.success("Config loaded.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to load config: {e}")

    # Return updated config
    updated = AppConfig(
        project_name=project_name,
        api_url=api_url,
        api_key=SecretStr(api_key_input) if api_key_input else None,
        model_name=model_name,
        temperature=float(temperature),
        max_tokens=int(max_tokens),
        threshold=float(threshold),
        tags=[t.strip() for t in tags.split(",") if t.strip()],
        enable_advanced=bool(enable_advanced),
    )
    return updated

# --------- Processing stub (replace with your logic) ---------
def process_text(text: str, cfg: AppConfig) -> str:
    # Example: configurable transformation to show the plumbing works
    base = text.strip()
    if not base:
        return ""
    out = base
    if cfg.threshold >= 0.5:
        out = out.upper()
    if cfg.enable_advanced:
        out = f"[{cfg.model_name} | temp={cfg.temperature} | max={cfg.max_tokens}]\n" + out
    return out

# --------- Main app ---------
def main():
    state = get_state()
    cfg: AppConfig = state.config

    # Sidebar variables
    st.session_state.config = sidebar_config(cfg)
    cfg = st.session_state.config

    # Header
    st.title(f"🗂️ {cfg.project_name}")
    st.caption("One place for variables, inputs, and outputs")

    # Tabs for Input / Output / Variables
    tabs = st.tabs(["Input", "Output", "Variables"])

    # Input tab
    with tabs[0]:
        st.subheader("Inputs")
        st.write("Provide text directly or upload a file.")
        t1, t2 = st.columns([2, 1], vertical_alignment="bottom")

        with t1:
            txt = st.text_area("Text input", value=state.inputs["text"], height=180, placeholder="Paste text here...")
        with t2:
            uploaded = st.file_uploader("Upload file (.txt, .md, .json)", type=["txt", "md", "json"])
            if uploaded is not None:
                content = uploaded.read().decode("utf-8", errors="ignore")
                # simple JSON pretty-print if applicable
                try:
                    obj = json.loads(content)
                    content = json.dumps(obj, ensure_ascii=False, indent=2)
                except Exception:
                    pass
                state.inputs["uploaded_name"] = uploaded.name
                state.inputs["uploaded_text"] = content

        if state.inputs["uploaded_text"]:
            with st.expander(f"Preview: {state.inputs['uploaded_name']}", expanded=False):
                st.code(state.inputs["uploaded_text"], language="markdown")

        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            if st.button("Process text", use_container_width=True):
                res = process_text(txt, cfg)
                if res:
                    save_result("text_input", res, {"source": "text_area"})
                    st.success("Processed text.")
                else:
                    st.info("Nothing to process.")
        with c2:
            if st.button("Process uploaded", use_container_width=True, disabled=not bool(state.inputs["uploaded_text"])):
                res = process_text(state.inputs["uploaded_text"], cfg)
                if res:
                    save_result(state.inputs["uploaded_name"] or "uploaded", res, {"source": "file"})
                    st.success("Processed uploaded content.")
                else:
                    st.info("Nothing to process.")

        # Persist current text input
        state.inputs["text"] = txt

    # Output tab
    with tabs[1]:
        st.subheader("Outputs")
        if not state.outputs:
            st.info("No outputs yet. Run a process from the Input tab.")
        else:
            df = pd.DataFrame(state.outputs)
            with st.expander("Table view", expanded=True):
                st.dataframe(df, use_container_width=True, height=280)
            with st.expander("Detail view", expanded=False):
                for i, row in enumerate(state.outputs):
                    st.markdown(f"**#{i+1} — {row['name']}**")
                    st.code(row["content"])
                    st.json(row["meta"])

    # Variables tab
    with tabs[2]:
        st.subheader("Current variables")
        colA, colB = st.columns(2)
        with colA:
            st.json(cfg.model_dump(mode="json", exclude={"api_key"}), expanded=False)
        with colB:
            if cfg.api_key:
                st.success("API key: set (hidden)")
            else:
                st.warning("API key: not set")
        st.divider()
        st.caption("Tip: Use Save/Load in the sidebar to persist configs and share them.")

    # Subtle styling for a cleaner look
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] { background-color: #0f172a10; }
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] { padding: 8px 16px; border-radius: 8px; }
        .stButton>button { border-radius: 8px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()
