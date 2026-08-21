import streamlit as st

from src.pipeline import PolicyLensPipeline
from src.models.schemas import ComplianceRequest


st.set_page_config(page_title="PolicyLens",page_icon="🔍",layout="wide")


pipeline = PolicyLensPipeline()
st.title("PolicyLens")
st.write("Corporate Policy Compliance Analyzer")

st.divider()


employee = st.text_input(
    "Employee Name"
)


department = st.selectbox("Department",["Engineering","Finance","HR","IT","Procurement","Sales","Marketing","Other"])


request_text = st.text_area("Request",placeholder="Describe the action you are requesting...")


reason = st.text_area("Reason",placeholder="Why are you making this request?")


additional_information = st.text_area("Additional Information",placeholder="Add approvals, context, or any other relevant information...")


st.divider()


if st.button("Analyze Request", type="primary"):

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

            st.subheader("Compliance Verdict")


            verdict = result.verdict.value


            if verdict == "COMPLIANT":
                st.success(verdict)

            elif verdict == "PARTIALLY_COMPLIANT":
                st.warning(verdict)

            elif verdict == "NON_COMPLIANT":
                st.error(verdict)

            else:
                st.info(verdict)


            st.subheader("Explanation")

            st.write(result.explanation)


            if result.requirements:

                st.subheader("Requirements")

                for requirement in result.requirements:

                    if requirement.status.value == "SATISFIED":
                        icon = "✅"

                    elif requirement.status.value == "NOT_SATISFIED":
                        icon = "❌"

                    else:
                        icon = "⚠️"

                    st.write(
                        f"{icon} **Section {requirement.section}**"
                    )

                    st.write(
                        f"**Status:** {requirement.status.value}"
                    )

                    st.write(requirement.description)

                    st.caption(
                        f"Rationale: {requirement.rationale}"
                    )

                    st.divider()


            if result.violations:

                st.subheader("Violations")

                for violation in result.violations:
                    st.error(violation)


            if result.missing_evidence:

                st.subheader("Missing Evidence")

                for item in result.missing_evidence:
                    st.warning(item)


            if result.evidence:

                st.subheader("Policy Evidence")

                for item in result.evidence:

                    with st.expander(
                        f"{item.policy} §{item.section}"
                    ):

                        st.write(item.content)

                        st.caption(
                            f"Source: {item.source}"
                        )


        except Exception as e:

            st.error(
                "An error occurred while analyzing the request."
            )

            st.exception(e)