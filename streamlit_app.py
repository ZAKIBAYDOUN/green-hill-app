import os
import json
import streamlit as st
from ghc_twin import app
from models import TwinState

st.set_page_config(page_title="GHC Digital Twin Tester", page_icon="🧪", layout="wide")
st.title("Green Hill Canarias – Digital Twin Tester")
st.caption("Visual interface to run and debug the LangGraph app (ghc)")

with st.sidebar:
    st.header("Settings")
    default_question = st.text_input("Question", value="What is the 9-month plan for EU-GMP compliance and ROI >20%?")
    vector_dir = st.text_input("VECTOR_STORE_DIR", value=os.getenv("VECTOR_STORE_DIR", "vector_store"))
    os.environ["VECTOR_STORE_DIR"] = vector_dir
    run_button = st.button("Run Graph")
    st.markdown("---")
    st.caption("Tip: Leave question empty to test missing-input handling.")

col1, col2 = st.columns(2)

if run_button:
    st.subheader("Input")
    st.code(json.dumps({"question": default_question}, ensure_ascii=False, indent=2), language="json")

    try:
        # Build initial state (question may be empty)
        init_state = TwinState(question=default_question if default_question.strip() else None)
        result = app.invoke(init_state)

        with col1:
            st.subheader("Final Answer")
            st.write(result.get("final_answer"))
            st.subheader("Errors")
            errs = result.get("errors", [])
            if errs:
                for e in errs:
                    st.error(e)
            else:
                st.success("No errors")

        with col2:
            st.subheader("State Snapshot")
            st.json(result, expanded=False)
            st.subheader("Agent Outputs")
            for key in [
                "strategy_output","finance_output","operations_output",
                "market_output","risk_output","compliance_output","innovation_output"
            ]:
                if result.get(key) is not None:
                    with st.expander(key, expanded=False):
                        st.json(result.get(key), expanded=False)

    except Exception as e:
        st.exception(e)
        st.stop()

st.markdown("---")
st.caption("Use: `streamlit run streamlit_app.py` to launch locally. Configure OPENAI_API_KEY to enable vector store.")
