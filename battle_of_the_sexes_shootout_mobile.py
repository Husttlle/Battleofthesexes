
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# Fantasy league team mapping
TEAM_MAPPING = {
    "Minnesota Vikings": "The Allen Wrench",
    "Tampa Bay Buccaneers": "Dusted RBs Retirement Home",
    "Baltimore Ravens": "Yeah i suck at fantasy football",
    "Green Bay Packers": "Big Penix Energy",
    "New England Patriots": "Really Bad Replacements",
    "Los Angeles Chargers": "Roy The Rocket",
    "Philadelphia Eagles": "Bumbling Idiots",
    "Houston Texans": "Onii Chan",
    "New York Giants": "Hall Too Well (20 Min Version)",
    "San Francisco 49ers": "Buddy Boyz Dexter",
    "Cleveland Browns": "Malachis Mauraders",
    "Las Vegas Raiders": "Came and Wentz"
}

FILTERED_TEAMS = list(TEAM_MAPPING.keys())

st.set_page_config(page_title="Battle Of The Sexes Shootout", layout="wide")
st.markdown("## 🏈 Battle Of The Sexes Shootout")
st.caption("Retro NFL vibes + Mobile Ready + Live Leaderboard. Auto-refreshes every 30 seconds.")

@st.cache_data(ttl=30)
def fetch_data():
    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
    try:
        response = requests.get(url)
        data = response.json()
        stats_list = []

        for game in data.get("events", []):
            competition = game.get("competitions", [{}])[0]
            status = competition.get("status", {}).get("type", {}).get("description", "").lower()

            if status not in ["in progress", "halftime", "end of period"]:
                continue

            for team in competition.get("competitors", []):
                team_name = team["team"]["displayName"]
                if team_name not in FILTERED_TEAMS:
                    continue

                stats = team.get("statistics", [])
                total, passing, rushing = 0, 0, 0

                for stat in stats:
                    if "Total Yards" in stat.get("name", ""):
                        total = stat.get("value", 0)
                    elif "Passing Yards" in stat.get("name", ""):
                        passing = stat.get("value", 0)
                    elif "Rushing Yards" in stat.get("name", ""):
                        rushing = stat.get("value", 0)

                stats_list.append({
                    "Fantasy Team": TEAM_MAPPING[team_name],
                    "NFL Team": team_name,
                    "Total Yards": total,
                    "Passing Yards": passing,
                    "Rushing Yards": rushing
                })

        return pd.DataFrame(stats_list)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

df = fetch_data()

if df.empty:
    st.warning("No live games currently involving your fantasy teams.")
else:
    leaderboard = df.sort_values("Total Yards", ascending=False).reset_index(drop=True)
    st.markdown("### 🥇 Live Leaderboard (Top 3)")
    for i in range(min(3, len(leaderboard))):
        medal = ["🥇", "🥈", "🥉"][i]
        st.markdown(f"{medal} **{leaderboard.iloc[i]['Fantasy Team']}** — {leaderboard.iloc[i]['Total Yards']} Total Yards")

    st.markdown("---")
    st.subheader("📋 Full Stats")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("📊 Visual Breakdown")

    def style_bar_chart(metric, color):
        df_sorted = df.sort_values(metric, ascending=False)
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.barh(df_sorted["Fantasy Team"], df_sorted[metric], color=color)
        ax.set_title(metric.upper(), fontsize=14, weight='bold')
        ax.set_xlabel("Yards")
        ax.invert_yaxis()
        ax.grid(True, linestyle="--", alpha=0.4)
        return fig

    st.markdown("### Total Yards")
    st.pyplot(style_bar_chart("Total Yards", "#ff4b4b"))

    st.markdown("### Passing Yards")
    st.pyplot(style_bar_chart("Passing Yards", "#1f77b4"))

    st.markdown("### Rushing Yards")
    st.pyplot(style_bar_chart("Rushing Yards", "#2ca02c"))
