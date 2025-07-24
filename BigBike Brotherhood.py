import streamlit as st
import pandas as pd
import matplotlib as plt
import numpy as py
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.yfinance import YFinanceTools

# Set up the Streamlit app
st.set_page_config(
    page_title="BigBike Brotherhood",
    page_icon="196010620-silhouette-of-biker-riding-adventure-motorbike-illustration-logo-vector.jpg",
    layout="wide",
    initial_sidebar_state="auto"
)

st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
    </style>
""", unsafe_allow_html=True)

# Inject custom CSS for font styling
st.markdown("""
    <style>
    html, body, [class*="st-"] {
        font-family: 'Segoe UI', sans-serif;
        font-weight: bold;
        color: #008080;
        font-size: 12x;
    }

    /* Style for specific titles */
    .main-title {
        font-size: 48px;
        font-weight: bold;
        color: #404040;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    .sub-title {
        font-size: 25px;
        color: #ffffffcc;
        text-align: center;
        margin-bottom: 40px;
    }
    </style>
""", unsafe_allow_html=True)

# Apply styled titles
st.markdown('<div class="main-title">BigBike Brotherhood</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Elevate Your Riding Experience.</div>', unsafe_allow_html=True)

# Custom CSS with online image as background
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://wallpapercave.com/wp/wp2017060.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: left top;
        background-attachment: fixed;
    }
    </style>
    """,unsafe_allow_html=True
)

with st.sidebar:
    st.header("🔑 API Configuration")
    openai_api_key = st.text_input("OpenAI API Key", type="password")

    st.markdown("---")
    st.header("🏍️ BigBike Brotherhood App")
    st.markdown("""
    Our Premium Services:
    - ✅ Determine Your **Perfect Bike**
    - 📊 Give You **The Best Price** For Bike of Your Choice
    - 💨 Precisely **Locate** Your Dream Bike
    """)
    st.header("⚠️ Disclaimer")
    st.markdown("""
    We tailored your dream **Big Bike** from your profile, please specify your riding profile to ensure your best riding experience.
    """)

    if not openai_api_key:
        st.warning("Please Enter Your **Private API Key** To Continue Your Bike Selection.")
        st.stop()

if openai_api_key:
    try:
        model = OpenAIChat(model="gpt-4o", api_key=openai_api_key)
        tools = YFinanceTools(
            stock_price=True,
            analyst_recommendations=True,
            company_info=True,
            company_news=True
        )
        agent = Agent(model=model, tools=[tools], show_tool_calls=True)
    except Exception as e:
        st.error(f"Failed Initializing Model: {e}")
        st.stop()

    st.header("1. 🏍️ Please Enter Your Desired Bike Brand")
    bike_selection = st.selectbox("Bike Brand:", ["Ducati", "MV Agusta", "Yamaha", "Honda", "Suzuki"])

    st.header("2. 😎 Rider's Profile")
    riding_experience = st.selectbox("How Long You Have Been Driving?", ["<1 Year", "1-3 Years", "3-5 Years", ">5 Years"])
    bike_usage = st.selectbox("Where Do You Usually Ride The Bike", ["Office", "Bike Event", "Overlander"])
    maintenance_behavior = st.selectbox("How Often Do You Take Your Bike For A Service?", ["2x per Month", "1x per Month", "Hardly Have A Time", "Never"])

    if st.button("Your Riding Profile", use_container_width=True):
        profile_score = age // 10 + ["<1 tahun", "1-3 tahun", "3-5 tahun", ">5 tahun"].index(investment_horizon)
        profile_score += ["Rendah", "Sedang", "Tinggi"].index(risk_tolerance) * 2

        if profile_score <= 5:
            risk_profile = "Konservatif"
            allocation = {"Cash Asset": 60, "Income Asset": 30, "Growth Asset": 10}
        elif profile_score <= 9:
            risk_profile = "Moderat"
            allocation = {"Cash Asset": 20, "Income Asset": 50, "Growth Asset": 30}
        else:
            risk_profile = "Agresif"
            allocation = {"Cash Asset": 10, "Income Asset": 30, "Growth Asset": 60}

        st.success(f"Profil Risiko Anda: {risk_profile}")

        if total_amount:
            st.header("3. 🧾 Alokasi Aset")

            cash_amount = total_amount * allocation["Cash Asset"] / 100
            income_amount = total_amount * allocation["Income Asset"] / 100
            growth_amount = total_amount * allocation["Growth Asset"] / 100

            st.markdown("""
                **Rekomendasi Alokasi:**
                - Cash Asset: Rp {:,.0f} ({}%)
                - Income Asset: Rp {:,.0f} ({}%)
                - Growth Asset: Rp {:,.0f} ({}%)
            """.format(cash_amount, allocation['Cash Asset'], income_amount, allocation['Income Asset'], growth_amount, allocation['Growth Asset']))

            # Pie Chart
            st.subheader("📊 Visualisasi Alokasi Aset")
            labels = list(allocation.keys())
            values = [cash_amount, income_amount, growth_amount]
            fig1, ax1 = plt.subplots()
            ax1.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')
            st.pyplot(fig1)

            # Step 4: Get Product Recommendation
            st.header("4. 📋 Rekomendasi Produk")
            query = f"""
            Saya adalah investor dengan profil risiko {risk_profile}. Tolong rekomendasikan masing-masing satu produk terbaik untuk:
            - Cash Asset: reksa dana pasar uang (Indonesia)
            - Income Asset: obligasi atau reksa dana pendapatan tetap (Indonesia)
            - Growth Asset: saham atau reksa dana saham (Indonesia)
            Untuk masing-masing produk, berikan:
            - Nama Produk & Kode
            - Jenis Produk
            - Return tahunan saat ini (%)
            - Simulasi proyeksi 3 dan 5 tahun berdasarkan return saat ini
            - Sumber data (jika memungkinkan berikan hyperlink nya)
            """
            with st.spinner("Mengambil rekomendasi produk..."):
                try:
                    product_response = agent.run(query)
                    product_text = product_response.content if hasattr(product_response, 'content') else product_response
                    st.markdown(product_text)

                    # Auto-extract return % using regex
                    cash_return = re.search(r"Cash.*?([\d\.]+)%", product_text)
                    income_return = re.search(r"Income.*?([\d\.]+)%", product_text)
                    growth_return = re.search(r"Growth.*?([\d\.]+)%", product_text)

                    # Default values if not found
                    cash_rate = float(cash_return.group(1)) / 100 if cash_return else 0.03
                    income_rate = float(income_return.group(1)) / 100 if income_return else 0.06
                    growth_rate = float(growth_return.group(1)) / 100 if growth_return else 0.10

                    # Growth Projection
                    st.subheader("📈 Proyeksi Pertumbuhan Dana Selama 5 Tahun (Berdasarkan Produk)")
                    years = np.arange(0, 6)

                    def simulate_growth(principal, rate):
                        return [principal * (1 + rate) ** year for year in years]

                    growth_cash = simulate_growth(cash_amount, cash_rate)
                    growth_income = simulate_growth(income_amount, income_rate)
                    growth_growth = simulate_growth(growth_amount, growth_rate)

                    total_projection = np.array(growth_cash) + np.array(growth_income) + np.array(growth_growth)

                    df_growth = pd.DataFrame({
                        "Tahun": years,
                        "Cash Asset": growth_cash,
                        "Income Asset": growth_income,
                        "Growth Asset": growth_growth,
                        "Total": total_projection
                    })

                    fig2, ax2 = plt.subplots()
                    ax2.plot(df_growth["Tahun"], df_growth["Cash Asset"], label="Cash Asset")
                    ax2.plot(df_growth["Tahun"], df_growth["Income Asset"], label="Income Asset")
                    ax2.plot(df_growth["Tahun"], df_growth["Growth Asset"], label="Growth Asset")
                    ax2.plot(df_growth["Tahun"], df_growth["Total"], label="Total", linewidth=3, linestyle='--')
                    ax2.set_xlabel("Tahun")
                    ax2.set_ylabel("Nilai Portfolio (Rp)")
                    ax2.set_title("Simulasi Pertumbuhan Aset 5 Tahun Berdasarkan Produk")
                    ax2.legend()
                    st.pyplot(fig2)

                except Exception as e:
                    st.error(f"Gagal mendapatkan rekomendasi produk: {e}")

            st.header("5. 📚 Alasan Pemilihan Produk & Market Outlook")
            reason_query = (
                f"Jelaskan mengapa produk rekomendasi ini cocok untuk investor dengan profil risiko {risk_profile}. "
                f"Sertakan kinerja historis produk, serta pandangan pasar terkini di Indonesia dan global."
            )
            with st.spinner("Mengambil informasi tambahan..."):
                try:
                    reason_response = agent.run(reason_query)
                    st.write(reason_response.content if hasattr(reason_response, 'content') else reason_response)
                except Exception as e:
                    st.error(f"Gagal mendapatkan alasan produk: {e}")

    # Step 6: Chatbot
    st.header("6. 💬 Chatbot Investasi")
    st.markdown("Tanyakan apa saja seputar investasi, reksa dana, saham, atau tips finansial:")

    user_question = st.text_area("Masukkan pertanyaan Anda", placeholder="Contoh: Apakah sekarang waktu yang tepat untuk membeli saham teknologi?")

    if st.button("Tanyakan", use_container_width=True) and user_question:
        try:
            chat_response = agent.run(user_question)
            st.markdown("**Jawaban:**")
            st.write(chat_response.content if hasattr(chat_response, 'content') else chat_response)
        except Exception as e:
            st.error(f"Gagal menjawab pertanyaan: {e}")
