"""
Purpose: Render visual graph charts and data grids dynamically from API payloads.
"""
from decimal import Decimal
import ast
import json
import streamlit as st
import plotly.express as px
import pandas as pd

class UIVisualizer:

    @staticmethod
    def render_route_badge(route: str):
        """Displays a clean visual anchor tag for execution paths."""
        if not route:
            return
            
        route_colors = {
            "sql": "rgba(28, 131, 225, 0.15)",
            "rag": "rgba(9, 171, 59, 0.15)",
            "hybrid": "rgba(255, 75, 75, 0.15)",
            "error": "rgba(128, 128, 128, 0.15)"
        }
        text_colors = {"sql": "#1C83E1", "rag": "#09AB3B", "hybrid": "#FF4B4B", "error": "#808080"}
        
        normalized_route = route.lower().strip()
        color = route_colors.get(normalized_route, route_colors["error"])
        text_color = text_colors.get(normalized_route, text_colors["error"])
        
        st.markdown(
            f'<span style="background-color: {color}; color: {text_color}; '
            f'padding: 4px 12px; border-radius: 16px; font-weight: bold; '
            f'font-size: 13px; text-transform: uppercase; border: 1px solid {text_color}">'
            f'Route: {route}</span>', 
            unsafe_allow_html=True
        )
        st.markdown("\n")

    @staticmethod
    def render_data_visualizations(response_data: dict, route: str):
        """Extracts tabular lists from responses and plots dynamic data visual graphs."""
        if not route or route.lower() not in ["sql", "hybrid"]:
            return

        if not isinstance(response_data, dict):
            return

        payload = response_data.get("raw_payload") if "raw_payload" in response_data else response_data
        if not isinstance(payload, dict):
            return

        sql_rows = payload.get("result") or payload.get("sql_insight")

        if not sql_rows:
            raw_result = payload.get("response", {})
            if isinstance(raw_result, str):
                try:
                    raw_result = ast.literal_eval(raw_result)
                except Exception:
                    try:
                        raw_result = json.loads(raw_result)
                    except Exception:
                        pass

            if isinstance(raw_result, dict):
                sql_rows = raw_result.get("result") or raw_result.get("sql_insight")
            elif isinstance(raw_result, list):
                sql_rows = raw_result

        if not sql_rows or not isinstance(sql_rows, list) or len(sql_rows) == 0:
            return

        try:
            cleaned_rows = []
            for row in sql_rows:
                if not isinstance(row, dict):
                    continue
                cleaned_row = {
                    k: float(v) if isinstance(v, Decimal) else v 
                    for k, v in row.items()
                }
                cleaned_rows.append(cleaned_row)

            if not cleaned_rows:
                return

            df = pd.DataFrame(cleaned_rows)
            
            with st.expander("Inspect Analytical Data Warehouse Grid", expanded=False):
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                text_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                
                if len(numeric_cols) >= 1 and len(text_cols) >= 1:
                    x_axis = text_cols[0]
                    y_axis = numeric_cols[0]
                    
                    fig = px.bar(
                        df, x=x_axis, y=y_axis, 
                        template="plotly_dark",
                        color_discrete_sequence=["#1C83E1" if route.lower() == "sql" else "#FF4B4B"]
                    )
                    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300)
                    st.plotly_chart(fig, use_container_width=True)
        except Exception:
            pass
