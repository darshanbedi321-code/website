import streamlit as st
from sql import Database

st.set_page_config(page_title="Library Books", page_icon="L", layout="wide")

st.markdown(
    """
    <style>
        .stApp {
            background: radial-gradient(circle at top left, rgba(255, 214, 153, 0.22), transparent 35%),
                        linear-gradient(135deg, #0f172a 0%, #111827 45%, #1f2937 100%);
            color: #f8fafc;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .hero-card {
            padding: 1.5rem 1.75rem;
            border-radius: 24px;
            background: rgba(15, 23, 42, 0.78);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 24px 60px rgba(15, 23, 42, 0.35);
            margin-bottom: 1rem;
        }
        .hero-kicker {
            text-transform: uppercase;
            letter-spacing: 0.18em;
            color: #f59e0b;
            font-size: 0.78rem;
            margin-bottom: 0.4rem;
        }
        .hero-title {
            font-size: 2.3rem;
            font-weight: 800;
            margin: 0;
        }
        .hero-text {
            color: rgba(248, 250, 252, 0.78);
            margin-top: 0.5rem;
            font-size: 1rem;
        }
        section[data-testid="stSidebar"] {
            background: rgba(15, 23, 42, 0.92);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
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


def render_table(rows):
    if rows:
        st.dataframe([row_to_dict(row) for row in rows], use_container_width=True, hide_index=True)
    else:
        st.info("No books found.")


db = get_database()
if db.conn is None:
    st.error(db.connection_error or "Database connection failed.")
    st.stop()

available_books = db.books()
all_books = db.all_books()

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-kicker">Library dashboard</div>
        <h1 class="hero-title">Store, issue, and track books in one place</h1>
        <div class="hero-text">Use the sidebar to add a new title, issue a book, or review the current inventory.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)
col1.metric("Total books", len(all_books))
col2.metric("Available", len(available_books))
col3.metric("Issued", max(0, len(all_books) - len(available_books)))

page = st.sidebar.radio("Navigate", ["Add Book", "Issue Book", "Available Books", "All Books"], index=0)
st.sidebar.caption("Your library database stays in sync with every action.")

if page == "Add Book":
    st.subheader("Add a book")
    with st.form("add_book_form", clear_on_submit=True):
        book_name = st.text_input("Book name", placeholder="Enter the title of the book")
        submitted = st.form_submit_button("Store book")

    if submitted:
        if not book_name.strip():
            st.warning("Enter a book name first.")
        else:
            result = db.store(book_name.strip())
            if result == 1:
                st.success(f"{book_name.strip()} was stored in the library.")
                st.rerun()
            else:
                st.error("Could not store the book.")

elif page == "Issue Book":
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
            st.caption(f"Auto fine: {fine}")
            issue_clicked = st.form_submit_button("Issue book")

        if issue_clicked:
            if not issued_by.strip():
                st.warning("Enter the borrower name first.")
            else:
                result = db.issue(selected_book, issued_by.strip(), fine, int(days))
                if result == 1:
                    st.success(f"{selected_book} has been issued to {issued_by.strip()}.")
                    st.rerun()
                elif result == 0:
                    st.warning("That book is not available for issue.")
                else:
                    st.error("Could not issue the book.")

elif page == "Available Books":
    st.subheader("Available books")
    render_table(available_books)

else:
    st.subheader("All books")
    render_table(all_books)
