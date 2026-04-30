2026-01-01: UX/Accessibility Learning - Streamlit styling with :has() pseudo-class and hidden marker approach combined with st.container() ensures stable, robust UI customization, completely preventing layout scattering, unlike native index-based nth-child targeting which often breaks.

## 2025-01-28 - Missing AI Loading States & Empty Inputs
**Learning:** Found a recurring UX gap where AI interactions (like Drug API analysis and NAFDAC lookups) lacked loading indicators and input validation. This creates a confusing "dead" state where users click and nothing happens while waiting for the Gemini API, or worse, they trigger empty API calls.
**Action:** Always wrap `genai.GenerativeModel.generate_content` calls in `with st.spinner("..."):` to provide immediate visual feedback. Additionally, enforce inline validation (e.g., `if not input.strip(): st.warning(...)`) before executing the API request.
## 2025-01-29 - Disabled States vs Hidden Actions
**Learning:** In Streamlit, conditionally hiding buttons completely (e.g., `if file_uploaded:` wrapping the `st.button()` declaration) is a poor UX pattern because it removes affordance and context. Users don't know an action is possible or what is required to unlock it.
**Action:** Use the `disabled` parameter on the button directly (e.g., `st.button(disabled=not file_uploaded, help="Upload a file to enable")`) so the UI layout remains stable, the action is discoverable, and the hover tooltip explains the prerequisite.
## 2025-05-01 - Silent Form Failures in Streamlit
**Learning:** Forms in Streamlit often lack clear indicators for required fields, and submitting them with missing required fields often fails silently. This leaves the user wondering if the form was actually submitted and what went wrong.
**Action:** Always provide explicit visual indicators (like `*`) for required fields. In the form submission handling logic, use an `else` branch to provide an explicit `st.error` message when validation fails, ensuring the user is informed of the issue.
