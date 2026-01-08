import streamlit as st
import requests

st.title("AI Powered SQL Query Generator")

user_input = st.text_input("Enter your query:")

if st.button("Generate SQL"):
    payload = {
        "prompt": user_input
    }

    response = requests.post(
        "http://127.0.0.1:8000/generate_sql/",
        json=payload
    )

    if response.status_code == 200:
        sql_query = response.json().get("sql_Query", "Error generating query")
        st.code(sql_query, language="sql")
        st.session_state["generated_sql"] = sql_query
    else:
        st.error("Backend error while generating SQL")

if "generated_sql" in st.session_state:
    if st.button("Execute SQL"):
        response = requests.post(
            "http://127.0.0.1:8000/execute_sql/",
            json={"query": st.session_state["generated_sql"]}
        )

        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            optimization_tips = data.get("optimization_tips", "No optimization tips available")

            st.subheader("Query Results:")
            st.write(results)

            st.subheader("Optimization Tips:")
            st.write(optimization_tips)
        else:
            st.error("Backend error while executing SQL")
