import streamlit as st
from sql import Database

st.set_page_config(page_title="Darshan's Library", page_icon="📚", layout="wide")

st.markdown(
    """
    <style>
        .stApp {
            background: radial-gradient(circle at top left, rgba(245, 158, 11, 0.18), transparent 40%),
                        radial-gradient(circle at bottom right, rgba(99, 102, 241, 0.15), transparent 45%),
                        linear-gradient(135deg, #0b1120 0%, #0f172a 45%, #111827 100%);
            color: #f8fafc;
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1150px;
        }

        /* HERO */
        .hero-card {
            padding: 2rem 2.2rem;
            border-radius: 28px;
            background: linear-gradient(135deg, rgba(30,41,59,0.9), rgba(15,23,42,0.9));
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 30px 70px rgba(0,0,0,0.4);
            margin-bottom: 1.5rem;
            position: relative;
            overflow: hidden;
        }
        .hero-kicker {
            display: inline-block;
            text-transform: uppercase;
            letter-spacing: 0.2em;
            color: #fbbf24;
            font-size: 0.72rem;
            font-weight: 700;
            background: rgba(251, 191, 36, 0.12);
            padding: 4px 12px;
            border-radius: 999px;
            margin-bottom: 0.7rem;
        }
        .hero-title {
            font-size: 2.4rem;
            font-weight: 800;
            margin: 0;
            background: linear-gradient(90deg, #f8fafc, #cbd5e1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .hero-text {
            color: rgba(248, 250, 252, 0.72);
            margin-top: 0.6rem;
            font-size: 1rem;
            max-width: 640px;
        }

        /* STAT CARDS */
        .stat-card {
            border-radius: 20px;
            padding: 1.1rem 1.3rem;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            text-align: left;
        }
        .stat-label {
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: rgba(248,250,252,0.55);
            margin-bottom: 0.3rem;
        }
        .stat-value {
            font-size: 1.9rem;
            font-weight: 800;
        }
        .stat-total .stat-value { color: #93c5fd; }
        .stat-available .stat-value { color: #86efac; }
        .stat-issued .stat-value { color: #fca5a5; }

        /* SIDEBAR */
        section[data-testid="stSidebar"] {
            background: rgba(10, 15, 28, 0.96);
            border-right: 1px solid rgba(255,255,255,0.06);
        }

        /* STATUS BADGE */
        .badge {
            display: inline-block;
            padding: 3px 12px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 700;
        }
        .badge-available { background: rgba(34,197,94,0.15); color: #4ade80; border: 1px solid rgba(34,197,94,0.35); }
        .badge-unavailable { background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.35); }

        /* BOOK ROW CARD */
        .book-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.9rem 1.1rem;
            border-radius: 16px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.06);
            margin-bottom: 0.6rem;
        }
        .book-row:hover { background: rgba(255,255,255,0.06); }
        .book-name { font-weight: 600; font-size: 1.02rem; }
        .book-meta { color: rgba(248,250,252,0.55); font-size: 0.82rem; margin-top: 2px; }

        div[data-testid="stForm"] {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 20px;
            padding: 1.4rem;
        }
        .stButton>button, .stFormSubmitButton>button {
            border-radius: 12px;
            font-weight: 700;
            background: linear-gradient(135deg, #f59e0b, #d97706);
            border: none;
            color: #0b1120;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_database():
    return Database()


def row_to_dict(row):
    values = list(row)
    return {
        "id": values[0] if len(values) > 0 else None,
        "bookname": values[1] if len(values) > 1 else None,
        "status": values[2] if len(values) > 2 else None,
        "issuedby": values[3] if len(values) > 3 else None,
        "fined": values[4] if len(values) > 4 else None,
        "days": values[5] if len(values) > 5 else None,
    }


def render_books(rows):
    if not rows:
        st.info("📭 No books found.")
        return

    for row in rows:
        book = row_to_dict(row)
        badge_class = "badge-available" if book["status"] == "available" else "badge-unavailable"
        badge_text = "Available" if book["status"] == "available" else "Issued"
        meta = ""
        if book["status"] != "available" and book["issuedby"]:
            meta = f'Issued to <b>{book["issuedby"]}</b> · {book["days"] or 0} days · Fine ₹{book["fined"] or 0}'

        st.markdown(
            f"""
            <div class="book-row">
                <div>
                    <div class="book-name">📖 {book["bookname"]}</div>
                    <div class="book-meta">{meta}</div>
                </div>
                <span class="badge {badge_class}">{badge_text}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


db = get_database()
if db.conn is None:
    st.error(db.connection_error or "Database connection failed.")
    st.stop()

available_books = db.books()
all_books = db.all_books()
issued_count = max(0, len(all_books) - len(available_books))

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-kicker">📚 Library Dashboard</div>
        <h1 class="hero-title">Store, issue &amp; track your books</h1>
        <div class="hero-text">Add new titles, issue them to readers, and keep an eye on what's available — all in one clean dashboard.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="stat-card stat-total"><div class="stat-label">Total Books</div><div class="stat-value">{len(all_books)}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-card stat-available"><div class="stat-label">Available</div><div class="stat-value">{len(available_books)}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-card stat-issued"><div class="stat-label">Issued</div><div class="stat-value">{issued_count}</div></div>', unsafe_allow_html=True)

st.write("")

st.sidebar.markdown("### 📚 Menu")
page = st.sidebar.radio("Navigate", ["➕ Add Book", "📤 Issue Book", "✅ Available Books", "📖 All Books"], index=0, label_visibility="collapsed")
st.sidebar.caption("Your library stays in sync with every action.")

if page == "➕ Add Book":
    st.subheader("Add a new book")
    with st.form("add_book_form", clear_on_submit=True):
        book_name = st.text_input("Book name", placeholder="Enter the title of the book")
        submitted = st.form_submit_button("Store Book📥")

    if submitted:
        if not book_name.strip():
            st.warning("Enter a book name first.")
        else:
            result = db.store(book_name.strip())
            if result == 1:
                st.success(f"✅ '{book_name.strip()}' was stored in the library.")
                st.rerun()
            else:
                st.error("Could not store the book.")

elif page == "📤 Issue Book":
    st.subheader("Issue a book")
    if not available_books:
        st.info("No available books to issue right now.")
    else:
        with st.form("issue_book_form"):
            book_names = [row[1] for row in available_books if len(row) > 1]
            selected_book = st.selectbox("Select book", book_names)
            issued_by = st.text_input("Issued by", placeholder="Enter the borrower's name")
            days = st.number_input("Days", min_value=1, value=7, step=1)
            fine = max(0, (int(days) - 7) * 10)
            st.caption(f"💰 Auto fine: ₹{fine}")
            issue_clicked = st.form_submit_button("Issue Book 📤")

        if issue_clicked:
            if not issued_by.strip():
                st.warning("Enter the borrower name first.")
            else:
                result = db.issue(selected_book, issued_by.strip(), fine, int(days))
                if result == 1:
                    st.success(f"✅ '{selected_book}' has been issued to {issued_by.strip()}.")
                    st.rerun()
                elif result == 0:
                    st.warning("That book is not available for issue.")
                else:
                    st.error("Could not issue the book.")

elif page == "✅ Available Books":
    st.subheader("Available books")
    render_books(available_books)

else:
    st.subheader("All books")
    render_books(all_books)