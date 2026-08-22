import streamlit as st

from src.pipeline import PolicyLensPipeline
from src.models.schemas import ComplianceRequest


st.set_page_config(
    page_title="PolicyLens",
    page_icon="🔍",
    layout="wide"
)


pipeline = PolicyLensPipeline()



with st.sidebar:

    st.title("🔍 PolicyLens")

    st.write(
        "AI-powered corporate policy "
        "compliance analyzer."
    )

    st.divider()

    st.subheader("How it works")

    st.write("1. Submit an employee request")
    st.write("2. Retrieve relevant policies")
    st.write("3. Rerank policy evidence")
    st.write("4. Analyze compliance")
    st.write("5. Generate a verdict")

    st.divider()

    st.caption("PolicyLens V1")



st.title("🔍 PolicyLens")

st.caption(
    "AI-powered corporate policy compliance analyzer"
)

st.divider()




with st.container(border=True):

    st.subheader("📋 Compliance Request")

    col1, col2 = st.columns(2)

    with col1:

        employee = st.text_input(
            "Employee Name",
            placeholder="e.g. Rahul Sharma"
        )

    with col2:

        department = st.selectbox(
            "Department",
            [
                "Engineering",
                "Finance",
                "HR",
                "IT",
                "Procurement",
                "Sales",
                "Marketing",
                "Other"
            ]
        )

    request_text = st.text_area(
        "Request",
        placeholder="Describe the action you are requesting...",
        height=120
    )

    reason = st.text_area(
        "Reason",
        placeholder="Why are you making this request?",
        height=100
    )

    additional_information = st.text_area(
        "Additional Information",
        placeholder="Add approvals, context, or other relevant information...",
        height=100
    )

    analyze = st.button(
        "🔍 Analyze Request",
        type="primary",
        use_container_width=True
    )



if analyze:

    if not employee or not request_text or not reason:

        st.warning(
            "Please provide the employee name, request, and reason."
        )

    else:

        request = ComplianceRequest(
            employee=employee,
            department=department,
            request=request_text,
            reason=reason,
            additional_information=additional_information
        )

        try:

            with st.spinner("Analyzing request..."):

                result = pipeline.run(request)



            st.divider()

            st.subheader("📊 Compliance Result")

            verdict = result.verdict.value


            if verdict == "COMPLIANT":

                st.success(
                    f"✅ {verdict}"
                )

            elif verdict == "PARTIALLY_COMPLIANT":

                st.warning(
                    f"⚠️ {verdict}"
                )

            elif verdict == "NON_COMPLIANT":

                st.error(
                    f"❌ {verdict}"
                )

            elif verdict == "INSUFFICIENT_EVIDENCE":

                st.info(
                    f"🔎 {verdict}"
                )

            else:

                st.info(
                    f"ℹ️ {verdict}"
                )



            with st.expander(
                "📝 Explanation",
                expanded=True
            ):

                st.write(result.explanation)



            if result.requirements:

                st.subheader("📌 Requirements")

                for requirement in result.requirements:

                    if requirement.status.value == "SATISFIED":

                        icon = "✅"

                    elif requirement.status.value == "NOT_SATISFIED":

                        icon = "❌"

                    else:

                        icon = "⚠️"


                    with st.expander(
                        f"{icon} Section {requirement.section} · "
                        f"{requirement.status.value}"
                    ):

                        st.write(
                            requirement.description
                        )

                        st.caption(
                            f"Rationale: {requirement.rationale}"
                        )



            if result.violations:

                st.subheader("❌ Violations")

                for violation in result.violations:

                    st.error(
                        violation
                    )



            if result.missing_evidence:

                st.subheader("🔎 Missing Evidence")

                for item in result.missing_evidence:

                    st.warning(
                        item
                    )



            if result.evidence:

                st.subheader("📚 Policy Evidence")

                for item in result.evidence:

                    with st.expander(
                        f"📄 {item.policy} · Section {item.section}"
                    ):

                        st.write(
                            item.content
                        )

                        st.caption(
                            f"Source: {item.source}"
                        )


        except Exception as e:

            st.error(
                "An error occurred while analyzing the request."
            )

            st.exception(e)



st.divider()

st.caption(
    "PolicyLens · AI-powered policy compliance analysis · V1"
)