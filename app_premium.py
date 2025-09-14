import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import re
from datetime import datetime, date
import pdfplumber
import requests
from io import BytesIO

# Page config
st.set_page_config(
    page_title="AI Finance Buddy",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Dark Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        background: #111827;
        font-family: 'Inter', sans-serif;
        color: #F9FAFB;
    }
    .stApp {
        background: #111827;
    }
    
    /* Glassmorphism cards */
    .glass-card {
        background: rgba(31, 41, 55, 0.8);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(75, 85, 99, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .main-header {
        background: linear-gradient(135deg, #4F46E5 0%, #9333EA 100%);
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 20px 60px rgba(79, 70, 229, 0.3);
        color: white;
        border: 1px solid rgba(147, 51, 234, 0.2);
    }
    
    .metric-card {
        background: rgba(31, 41, 55, 0.8);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(75, 85, 99, 0.3);
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        margin: 0.5rem 0;
        border-left: 4px solid #10B981;
        transition: all 0.3s ease;
        color: #F9FAFB;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(16, 185, 129, 0.2);
        border-left-color: #34D399;
    }
    
    .insight-card {
        background: rgba(31, 41, 55, 0.9);
        backdrop-filter: blur(25px);
        border: 1px solid rgba(79, 70, 229, 0.3);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 20px 50px rgba(79, 70, 229, 0.2);
        margin: 1.5rem 0;
        color: #F9FAFB;
    }
    
    .investment-card {
        background: rgba(16, 185, 129, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 20px 50px rgba(16, 185, 129, 0.1);
        margin: 1.5rem 0;
        color: #F9FAFB;
    }
    
    .cost-cutting-card {
        background: rgba(239, 68, 68, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 20px 50px rgba(239, 68, 68, 0.1);
        margin: 1.5rem 0;
        color: #F9FAFB;
    }
    
    .salary-card {
        background: rgba(31, 41, 55, 0.9);
        backdrop-filter: blur(25px);
        border: 1px solid rgba(79, 70, 229, 0.3);
        padding: 3rem;
        border-radius: 25px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 25px 70px rgba(79, 70, 229, 0.2);
        color: #F9FAFB;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #4F46E5 0%, #9333EA 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(79, 70, 229, 0.3);
        font-family: 'Inter', sans-serif;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(79, 70, 229, 0.4);
        background: linear-gradient(135deg, #5B21B6 0%, #A855F7 100%);
    }
    
    .sidebar .stSelectbox > div > div {
        background: rgba(31, 41, 55, 0.8);
        border: 1px solid rgba(75, 85, 99, 0.3);
        border-radius: 12px;
        color: #F9FAFB;
    }
    
    .rupee-symbol {
        color: #10B981;
        font-weight: bold;
    }
    
    .indian-flag {
        background: linear-gradient(to right, #ff9933 33%, #ffffff 33%, #ffffff 66%, #138808 66%);
        height: 4px;
        width: 100%;
        margin: 10px 0;
        border-radius: 2px;
    }
    
    .report-card {
        background: rgba(31, 41, 55, 0.95);
        backdrop-filter: blur(30px);
        border: 1px solid rgba(79, 70, 229, 0.2);
        padding: 2rem;
        border-radius: 16px;
        margin: 1rem 0;
        color: #F9FAFB;
        font-family: 'Inter', monospace;
        white-space: pre-wrap;
        max-height: 400px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

def parse_text_input(text):
    """Parse plain text input into DataFrame"""
    lines = text.strip().split('\n')
    data = []
    for line in lines:
        match = re.search(r'(.+?)\s+(\d+(?:\.\d+)?)', line.strip())
        if match:
            category = match.group(1).strip()
            amount = float(match.group(2))
            data.append({
                'Category': category,
                'Amount': amount,
                'Date': date.today().strftime('%Y-%m-%d')
            })
    return pd.DataFrame(data)

def parse_pdf(pdf_file):
    """Parse PDF file and extract financial data"""
    data = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                for line in lines:
                    match = re.search(r'(.+?)\s+(\d+(?:\.\d+)?)', line.strip())
                    if match:
                        category = match.group(1).strip()
                        amount = float(match.group(2))
                        data.append({
                            'Category': category,
                            'Amount': amount,
                            'Date': date.today().strftime('%Y-%m-%d')
                        })
    return pd.DataFrame(data)

def normalize_data(df):
    """Convert DataFrame to unified JSON format"""
    if df.empty:
        return []
    
    normalized = []
    for _, row in df.iterrows():
        normalized.append({
            "category": str(row.get('Category', 'Unknown')),
            "amount": float(row.get('Amount', 0)),
            "date": str(row.get('Date', date.today().strftime('%Y-%m-%d')))
        })
    return normalized

def generate_financial_report(data, salary):
    """Generate downloadable financial report"""
    if not data:
        return "No data available for analysis."
    
    total_spending = sum(item['amount'] for item in data)
    categories = {}
    for item in data:
        categories[item['category']] = categories.get(item['category'], 0) + item['amount']
    
    savings = salary - total_spending
    savings_rate = (savings / salary * 100) if salary > 0 else 0
    
    # Generate formatted report
    report = f"""
═══════════════════════════════════════════════════════════════
                    AI FINANCE BUDDY - FINANCIAL REPORT
═══════════════════════════════════════════════════════════════

📊 FINANCIAL OVERVIEW
─────────────────────────────────────────────────────────────
Monthly Salary:           ₹{salary:,.0f}
Total Monthly Spending:   ₹{total_spending:,.0f}
Monthly Savings:          ₹{savings:,.0f}
Savings Rate:             {savings_rate:.1f}%

💰 SPENDING BREAKDOWN
─────────────────────────────────────────────────────────────
"""
    
    for category, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        percentage = (amount / total_spending * 100) if total_spending > 0 else 0
        report += f"{category:<20} ₹{amount:>8,.0f} ({percentage:>5.1f}%)\n"
    
    report += f"""

🎯 FINANCIAL HEALTH ASSESSMENT
─────────────────────────────────────────────────────────────
"""
    
    if savings_rate >= 20:
        report += "✅ EXCELLENT: Your savings rate is outstanding!\n"
    elif savings_rate >= 10:
        report += "⚠️  GOOD: Your savings rate is decent but can be improved.\n"
    else:
        report += "❌ NEEDS IMPROVEMENT: Your savings rate is below recommended levels.\n"
    
    report += f"""

📈 INVESTMENT RECOMMENDATIONS
─────────────────────────────────────────────────────────────
Recommended Monthly SIP:  ₹{max(1000, savings * 0.6):,.0f}
Emergency Fund Target:    ₹{total_spending * 6:,.0f}

Suggested Indian Stocks:
• Reliance Industries (RELIANCE)
• Tata Consultancy Services (TCS)
• HDFC Bank (HDFCBANK)
• Infosys (INFY)
• ICICI Bank (ICICIBANK)

Mutual Fund Categories:
• Large Cap Funds: 40% allocation
• Mid Cap Funds: 30% allocation
• Small Cap Funds: 20% allocation
• Debt Funds: 10% allocation

✂️ COST CUTTING OPPORTUNITIES
─────────────────────────────────────────────────────────────
"""
    
    # Find top 3 spending categories
    top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]
    for i, (category, amount) in enumerate(top_categories, 1):
        potential_saving = amount * 0.15  # 15% reduction
        report += f"{i}. {category}: Reduce by ₹{potential_saving:,.0f} (15% cut)\n"
    
    report += f"""

💡 ACTIONABLE STEPS
─────────────────────────────────────────────────────────────
1. Set up automatic SIP of ₹{max(1000, savings * 0.6):,.0f}/month
2. Build emergency fund of ₹{total_spending * 6:,.0f}
3. Track expenses weekly using this app
4. Review and optimize spending monthly
5. Consider tax-saving investments (ELSS, PPF)

📅 Generated on: {datetime.now().strftime('%d %B %Y at %I:%M %p')}
═══════════════════════════════════════════════════════════════
"""
    
    return report

def get_ai_insights(data, salary):
    """Get AI insights with Indian investment suggestions"""
    if not data:
        return "No data available for analysis."
    
    total_spending = sum(item['amount'] for item in data)
    categories = {}
    for item in data:
        categories[item['category']] = categories.get(item['category'], 0) + item['amount']
    
    savings = salary - total_spending
    savings_rate = (savings / salary * 100) if salary > 0 else 0
    
    prompt = f"""
    You are an expert Indian financial advisor. Analyze this personal financial data:
    
    Monthly Salary: ₹{salary:,.0f}
    Total Monthly Spending: ₹{total_spending:,.0f}
    Monthly Savings: ₹{savings:,.0f}
    Savings Rate: {savings_rate:.1f}%
    
    Spending Breakdown:
    {json.dumps(categories, indent=2)}
    
    Provide detailed analysis with:
    
    1. **FINANCIAL HEALTH ASSESSMENT**
    - Budget analysis and spending patterns
    - Savings rate evaluation (ideal is 20-30%)
    
    2. **INDIAN INVESTMENT RECOMMENDATIONS**
    - Suggest specific Indian stocks (Reliance, TCS, HDFC Bank, etc.)
    - SIP recommendations for mutual funds (amount based on income)
    - PPF, ELSS, and tax-saving options
    - Emergency fund suggestions (6 months expenses)
    
    3. **COST-CUTTING STRATEGIES**
    - Identify top 3 categories to reduce spending
    - Specific actionable steps to cut costs
    - Alternative cheaper options for expenses
    
    4. **ACTIONABLE FINANCIAL PLAN**
    - Monthly investment allocation
    - Short-term and long-term goals
    - Risk management strategies
    
    Keep it practical, India-specific, and actionable. Use Indian financial terms and context.
    """
    
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
        
        if not api_key or api_key == "your-groq-api-key-here":
            return "Please add your Groq API key to .streamlit/secrets.toml"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "model": "llama-3.1-8b-instant",
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            st.error(f"API Error: {response.status_code}")
            return f"AI service temporarily unavailable. Basic analysis: You're saving ₹{savings:,.0f} ({savings_rate:.1f}%) from your ₹{salary:,.0f} salary. Consider investing in SIP and reducing spending in {max(categories, key=categories.get)}."
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return f"AI analysis unavailable. Basic summary: Savings rate {savings_rate:.1f}%, total spending ₹{total_spending:,.0f} from ₹{salary:,.0f} salary."

def create_premium_pie_chart(data):
    """Create premium spending breakdown pie chart"""
    if not data:
        return go.Figure()
    
    categories = {}
    for item in data:
        categories[item['category']] = categories.get(item['category'], 0) + item['amount']
    
    colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff9ff3', '#54a0ff']
    
    fig = px.pie(
        values=list(categories.values()),
        names=list(categories.keys()),
        title="💰 Monthly Spending Breakdown",
        color_discrete_sequence=colors
    )
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Amount: ₹%{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12, family="Poppins"),
        title_font_size=16
    )
    return fig

def create_savings_chart(data, salary):
    """Create premium savings vs spending chart"""
    if not data or salary == 0:
        return go.Figure()
    
    total_spending = sum(item['amount'] for item in data)
    savings = salary - total_spending
    
    fig = go.Figure(data=[
        go.Bar(
            name='💸 Spending', 
            x=['Monthly Budget'], 
            y=[total_spending], 
            marker_color='#ff6b6b',
            text=[f'₹{total_spending:,.0f}'],
            textposition='auto'
        ),
        go.Bar(
            name='💰 Savings', 
            x=['Monthly Budget'], 
            y=[savings], 
            marker_color='#4ecdc4',
            text=[f'₹{savings:,.0f}'],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title=f"📊 Monthly Budget Overview (₹{salary:,.0f} salary)",
        barmode='stack',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', family="Poppins"),
        showlegend=True
    )
    return fig

def main():
    # Main Header
    st.markdown("""
    <div class="main-header">
        <h1>💰 AI Finance Buddy</h1>
        <h3>🇮🇳 Your Intelligent Indian Financial Companion</h3>
        <div class="indian-flag"></div>
        <p>Powered by AI • Built for Indian Investors • Smart Financial Planning</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'financial_data' not in st.session_state:
        st.session_state.financial_data = []
    if 'salary' not in st.session_state:
        st.session_state.salary = 0
    if 'step' not in st.session_state:
        st.session_state.step = 1
    
    # Step 1: Salary Input
    if st.session_state.step == 1:
        st.markdown("""
        <div class="salary-card">
            <h2>💰 Step 1: What's Your Monthly Salary?</h2>
            <p>Let's start your financial journey with your income details</p>
            <div class="indian-flag"></div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            salary_input = st.number_input(
                "Enter your monthly salary (₹)",
                min_value=0.0,
                value=float(st.session_state.salary) if st.session_state.salary else 0.0,
                step=5000.0,
                format="%.0f"
            )
            
            if st.button("🚀 Next: Add Your Expenses", type="primary", use_container_width=True):
                if salary_input > 0:
                    st.session_state.salary = salary_input
                    st.session_state.step = 2
                    st.rerun()
                else:
                    st.error("Please enter a valid salary amount")
        
        if salary_input > 0:
            st.success(f"💰 Monthly Salary: ₹{salary_input:,.0f}")
        
        return
    
    # Step 2: Expense Input and Analysis
    elif st.session_state.step == 2:
        # Top bar with salary
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**💰 Monthly Salary: <span class='rupee-symbol'>₹{st.session_state.salary:,.0f}</span>**", unsafe_allow_html=True)
        with col2:
            if st.button("⬅️ Change Salary"):
                st.session_state.step = 1
                st.rerun()
        
        # Premium Sidebar
        with st.sidebar:
            st.markdown("### 📊 Add Your Monthly Expenses")
            
            input_method = st.selectbox(
                "Choose input method:",
                ["📝 Paste Text", "📄 Upload Excel/CSV", "📋 Upload PDF"]
            )
            
            df = pd.DataFrame()
            
            if input_method == "📝 Paste Text":
                st.markdown("**Format: Category Amount**")
                text_input = st.text_area(
                    "Enter your expenses:",
                    placeholder="Rent 25000\nGroceries 8000\nTransport 3000\nUtilities 4000\nEntertainment 5000\nDining Out 6000",
                    height=200
                )
                if text_input:
                    try:
                        df = parse_text_input(text_input)
                        st.success("✅ Expenses parsed!")
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            elif input_method == "📄 Upload Excel/CSV":
                uploaded_file = st.file_uploader("Upload your file", type=['csv', 'xlsx', 'xls'])
                if uploaded_file:
                    try:
                        if uploaded_file.name.endswith('.csv'):
                            df = pd.read_csv(uploaded_file)
                        else:
                            df = pd.read_excel(uploaded_file)
                        st.success("✅ File uploaded!")
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            elif input_method == "📋 Upload PDF":
                uploaded_file = st.file_uploader("Upload PDF file", type=['pdf'])
                if uploaded_file:
                    try:
                        df = parse_pdf(uploaded_file)
                        st.success("✅ PDF processed!")
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            if not df.empty:
                st.session_state.financial_data = normalize_data(df)
                st.write("**Preview:**", df.head())
            
            # Quick demo data
            if st.button("🎯 Load Indian Sample Data"):
                demo_data = [
                    {"category": "Rent", "amount": 25000, "date": "2025-01-01"},
                    {"category": "Groceries", "amount": 8000, "date": "2025-01-15"},
                    {"category": "Transport", "amount": 3000, "date": "2025-01-10"},
                    {"category": "Utilities", "amount": 4000, "date": "2025-01-05"},
                    {"category": "Entertainment", "amount": 5000, "date": "2025-01-12"},
                    {"category": "Dining Out", "amount": 6000, "date": "2025-01-08"},
                    {"category": "Shopping", "amount": 7000, "date": "2025-01-14"},
                ]
                st.session_state.financial_data = demo_data
                st.rerun()
        
        # Main Dashboard
        if st.session_state.financial_data:
            data = st.session_state.financial_data
            total_spending = sum(item['amount'] for item in data)
            savings = st.session_state.salary - total_spending
            savings_rate = (savings / st.session_state.salary * 100) if st.session_state.salary > 0 else 0
            
            # Premium Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>💸 Total Spending</h4>
                    <h2>₹{total_spending:,.0f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                color = "#4ecdc4" if savings > 0 else "#ff6b6b"
                st.markdown(f"""
                <div class="metric-card">
                    <h4>💰 Monthly Savings</h4>
                    <h2 style="color: {color}">₹{savings:,.0f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                if savings_rate >= 20:
                    color, status = "#4ecdc4", "Excellent"
                elif savings_rate >= 10:
                    color, status = "#feca57", "Good"
                else:
                    color, status = "#ff6b6b", "Needs Improvement"
                    
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📊 Savings Rate</h4>
                    <h2 style="color: {color}">{savings_rate:.1f}%</h2>
                    <p style="color: {color}; font-size: 12px;">{status}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                categories_count = len(set(item['category'] for item in data))
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📂 Categories</h4>
                    <h2>{categories_count}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Premium Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(create_premium_pie_chart(data), use_container_width=True)
            
            with col2:
                st.plotly_chart(create_savings_chart(data, st.session_state.salary), use_container_width=True)
            
            # Expenses Table
            st.subheader("📋 Your Monthly Expenses")
            df_display = pd.DataFrame(data)
            df_display['amount'] = df_display['amount'].apply(lambda x: f"₹{x:,.0f}")
            st.dataframe(df_display, use_container_width=True)
            
            # AI Analysis Section
            st.subheader("🤖 AI Financial Analysis & Investment Recommendations")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("🧠 Generate Complete Financial Report", type="primary", use_container_width=True):
                    with st.spinner("🔍 Analyzing your finances and generating comprehensive report..."):
                        # Generate formatted report
                        report = generate_financial_report(data, st.session_state.salary)
                        
                        # Store report in session state
                        st.session_state.financial_report = report
                        
                        # Display report in a nice format
                        st.markdown(f"""
                        <div class="report-card">
                            {report}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Get AI insights for additional analysis
                        ai_insights = get_ai_insights(data, st.session_state.salary)
                        
                        st.markdown(f"""
                        <div class="insight-card">
                            <h3>🤖 AI Analysis</h3>
                            <div style="white-space: pre-wrap;">{ai_insights}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="glass-card">
                    <h4>💡 Features</h4>
                    <p>🇮🇳 Indian Stock Recommendations</p>
                    <p>📊 SIP Investment Plans</p>
                    <p>✂️ Cost Cutting Strategies</p>
                    <p>💰 Tax Saving Options</p>
                    <p>🎯 Goal-based Planning</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Export Section
            st.subheader("📥 Download Financial Reports")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'financial_report' in st.session_state:
                    st.download_button(
                        "📋 Download Financial Report",
                        st.session_state.financial_report,
                        "AI_Financial_Report.txt",
                        "text/plain"
                    )
            
            with col2:
                csv_data = pd.DataFrame(data).to_csv(index=False)
                st.download_button(
                    "📄 Download CSV Data",
                    csv_data,
                    "expense_data.csv",
                    "text/csv"
                )
            
            with col3:
                excel_buffer = BytesIO()
                pd.DataFrame(data).to_excel(excel_buffer, index=False)
                st.download_button(
                    "📊 Download Excel Data",
                    excel_buffer.getvalue(),
                    "expense_data.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        else:
            st.markdown("""
            <div class="glass-card">
                <h3>👈 Get Started!</h3>
                <p>Please add your monthly expenses using the sidebar to unlock:</p>
                <ul>
                    <li>🇮🇳 Indian stock market recommendations</li>
                    <li>📊 SIP investment suggestions</li>
                    <li>✂️ Personalized cost-cutting strategies</li>
                    <li>💰 Tax-saving investment options</li>
                    <li>📋 Downloadable financial report</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()