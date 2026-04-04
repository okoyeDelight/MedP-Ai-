import streamlit as st
import google.generativeai as genai

# 1. Setup
genai.configure(api_key="AIzaSyDScvVrWLB_KzagEm517qV6BTeyQfhpbUY")

st.set_page_config(page_title="Herbal AI", page_icon="🌿")
st.title("🌿 Herbal Remedy AI Guide")
st.write("Pharmacognosy Assistant for Pharmacy Students")

# 2. Input
user_input = st.text_input("What is the symptom?")

# 3. Search Logic
if st.button("Search Remedies"):
    if user_input:
        with st.spinner("Analyzing..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"You are a Pharmacognosy expert. Give a layman herbal remedy for {user_input} with plant name, preparation, and safety."
                response = model.generate_content(prompt)
                st.success("Analysis Complete!")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter a symptom.")
        # Image search logic
                match = re.search(r"SEARCH_TERM:\s*(.+)", text)
                if match:
                    plant = urllib.parse.quote(match.group(1).strip())
                    st.markdown(f"**[View Images on Google](https://www.google.com/search?tbm=isch&q={plant}+plant)**")
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a symptom.")
except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a symptom first.")

st.sidebar.info("This is a pharmacy student project for educational purposes, innofest 26.")

