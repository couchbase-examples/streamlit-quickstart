import streamlit as st
import json
from couchbase_streamlit_connector.connector import CouchbaseConnector

def initialize_connection():
    # Set the application title
    st.title("Couchbase + Streamlit Application")
    
    # Sidebar for connection settings
    with st.sidebar:
        st.header("Connection Settings") # Sidebar header for clarity

        # User input fields for Couchbase connection parameters
        conn_str = st.text_input("Connection String")  # Connection string for Couchbase
        username = st.text_input("Username")  # Username for authentication
        password = st.text_input("Password", type="password")  # Password (masked for security)
        bucket_name = st.text_input("Bucket Name")  # Couchbase bucket to connect to
        scope_name = st.text_input("Scope Name")  # Scope within the bucket
        collection_name = st.text_input("Collection Name")  # Collection within the scope
        
        # Button to establish a connection
        if st.button("Connect", key="connect_btn"):
            try:
                # Attempt to create a connection using the provided details
                connection = st.connection(
                    "couchbase",  # Connection alias
                    type=CouchbaseConnector,  # Specify the Couchbase connector type
                    CONNSTR=conn_str,  # Connection string
                    USERNAME=username,  # Username for authentication
                    PASSWORD=password,  # Password for authentication
                    BUCKET_NAME=bucket_name,  # Name of the target bucket
                    SCOPE_NAME=scope_name,  # Name of the target scope
                    COLLECTION_NAME=collection_name  # Name of the target collection
                )

                # Store the connection in session state for later use
                st.session_state["connection"] = connection  
                
                # Display success message if connection is successful
                st.success("Connected successfully!")
            except Exception as e:
                # Display an error message if connection fails
                st.error(f"Connection failed: {e}")
                
def insert_document():
    st.subheader("Create Document")  # Section header for inserting a document

    # Expander widget to collapse/expand the document insertion panel
    with st.expander("Insert a new document", expanded=False):
        # Input field for Document ID (unique identifier for the document)
        doc_id = st.text_input("Document ID", key="create_id")

        # Multi-line text area for entering document data in JSON format
        doc_data = st.text_area(
            "Document Data (JSON)",
            value='{\n  "name": "John Doe",\n  "email": "john@example.com"\n}',  # Pre-filled example JSON
            key="create_data"
        )

        # Button to insert the document
        if st.button("Insert", key="create_btn"):
            try:
                # Convert input JSON string to a Python dictionary safely
                json_data = json.loads(doc_data)  # Using json.loads() instead of eval() to prevent security risks

                # Insert the document into Couchbase using the active connection
                st.session_state["connection"].insert_document(doc_id, json_data)

                # Display success message upon successful insertion
                st.success("Document inserted successfully!")
            except Exception as e:
                # Display error message if insertion fails
                st.error(f"Insert failed: {e}")
                
def fetch_document():
    st.subheader("Read Document")  # Section header for fetching a document

    # Expander widget to optionally collapse/expand the fetch panel
    with st.expander("Fetch an existing document", expanded=False):
        # Input field for the Document ID to retrieve
        doc_id = st.text_input("Document ID to fetch", key="read_id")

        # Button to trigger document retrieval
        if st.button("Fetch", key="read_btn"):
            try:
                # Fetch the document from Couchbase using the provided ID
                doc = st.session_state["connection"].get_document(doc_id)

                # Display the retrieved document in JSON format for easy reading
                st.json(doc)
            except Exception as e:
                # Show an error message if fetching fails (e.g., document not found, connection issue)
                st.error(f"Fetch failed: {e}")
                
def update_document():
    st.subheader("Update Document")  # Section header for updating a document

    # Expander widget to optionally collapse/expand the update panel
    with st.expander("Update an existing document", expanded=False):
        # Input field for the Document ID to update
        doc_id = st.text_input("Document ID to update", key="update_id")

        # Multi-line text area for entering new document data in JSON format
        new_data = st.text_area(
            "Updated Data (JSON)",
            key="update_data",
            value='{\n  "name": "John Doe",\n  "email": "john@example.com"\n}',  # Pre-filled example JSON
        )

        # Button to update the document
        if st.button("Update", key="update_btn"):
            try:
                # Convert input JSON string to a Python dictionary safely
                json_data = json.loads(new_data)  # Using json.loads() instead of eval() for security

                # Replace the existing document with new data
                st.session_state["connection"].replace_document(doc_id, json_data)

                # Display success message upon successful update
                st.success("Document updated successfully!")
            except Exception as e:
                # Display an error message if the update fails
                st.error(f"Update failed: {e}")
                
def delete_document():
    st.subheader("Delete Document")  # Section header for deleting a document

    # Expander widget to optionally collapse/expand the delete panel
    with st.expander("Delete an existing document", expanded=False):
        # Input field for the Document ID to delete
        doc_id = st.text_input("Document ID to delete", key="delete_id")

        # Button to trigger document deletion
        if st.button("Delete", key="delete_btn"):
            try:
                # Remove the document from Couchbase using the provided ID
                st.session_state["connection"].remove_document(doc_id)

                # Display success message upon successful deletion
                st.success("Document deleted successfully!")
            except Exception as e:
                # Show an error message if deletion fails (e.g., document not found, connection issue)
                st.error(f"Delete failed: {e}")
                
def query_data():
    st.subheader("Query Data")  # Section header for executing queries

    # Expander widget to collapse/expand the query execution panel
    with st.expander("Execute SQL++ Query", expanded=False):
        # Multi-line text area for entering a SQL++ (N1QL) query
        query = st.text_area(
            "SQL++ Query",
            value="SELECT * FROM `travel-sample`.inventory.airline LIMIT 5;",  # Pre-filled example query
            key="query_input"
        )

        # Button to execute the query
        if st.button("Execute Query", key="query_btn"):
            try:
                # Execute the SQL++ query using the active Couchbase connection
                results = st.session_state["connection"].query(query)

                # Convert query results from an iterator to a list for display
                data = []
                for row in results:
                    data.append(row)

                # Display query results in Streamlit
                st.write(data)
            except Exception as e:
                # Show an error message if the query execution fails
                st.error(f"Query failed: {e}")
                
def main():
    # Initialize the Couchbase connection settings in the sidebar
    initialize_connection()
    
    # Check if a connection is successfully established
    if "connection" in st.session_state:
        # Create tabbed navigation for different database operations
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Create", "Read", "Update", "Delete", "Query"
        ])

        # Assign each tab to its respective function
        with tab1:
            insert_document()  # Tab for inserting new documents
        with tab2:
            fetch_document()  # Tab for reading (fetching) documents
        with tab3:
            update_document()  # Tab for updating existing documents
        with tab4:
            delete_document()  # Tab for deleting documents
        with tab5:
            query_data()  # Tab for executing SQL++ queries
    else:
        # Display an informational message if no connection is found
        st.info("Please connect to Couchbase using the sidebar to start.")

# Run the Streamlit application
if __name__ == "__main__":
    # Set up the page configuration (title, icon, layout)
    st.set_page_config(
        page_title="Basic CRUD App using Couchbase-Streamlit-Connector",  # Title of the web app
        page_icon="🔌",  # Page icon (plugin symbol)
        layout="wide"  # Use a wide layout for better visibility
    )
    
    # Call the main function to start the app
    main()