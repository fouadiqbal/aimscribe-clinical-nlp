"""Interactive fictional-case demonstration. Run: streamlit run app.py."""
import json
import os
import urllib.error
import streamlit as st
from src.common import ROOT
from src.engine import run, SECTIONS

st.set_page_config(page_title="AIMScribe | Protocol evidence", page_icon="📋", layout="wide")
st.title("AIMScribe")
st.caption("Clinical NLP assessment prototype · Fictional cases · Source-linked recommendations")
mode = st.sidebar.radio("Recommendation mode",["baseline","improved"],format_func=str.title)
st.sidebar.caption("Improved mode checks source prerequisites and missing information before model selection.")
if os.environ.get("AIMSCRIBE_CLOUD") == "1":
    st.sidebar.info("Free CPU model runs in this cloud container. First use downloads the model and may take several minutes.")
    st.warning("Public educational demo: use fictional cases only. Do not enter real patient details or identifying information.")
else:
    st.sidebar.info("Free local inference. First response may take longer while models load.")

BOOL_FIELDS = {
    "warning_signs":"Dengue warning or danger signs present",
    "dengue_ns1_negative":"Dengue NS1 test negative",
    "dengue_ruled_out":"Dengue adequately ruled out by clinician",
    "epidemic_exposure":"Relevant chikungunya epidemic exposure",
    "pregnant":"Pregnant",
    "may_become_pregnant":"May become pregnant",
    "liver_disease":"Preexisting liver disease",
    "kidney_disease":"Preexisting kidney disease",
    "home_care_eligible":"Assessed eligible for dengue home care",
    "persistent_mild_bp_after_2_weeks":"BP 140-159/90-99 persists after two-week review",
    "amlodipine_5mg_unmet_target_after_month":"Target unmet after one month of amlodipine 5 mg",
    "elderly_or_low_body_weight":"Elderly or low body weight (clinician assessed)",
    "outbreak_declared":"Cholera outbreak declared",
    "elderly":"Elderly (clinician assessed)",
    "lethargic_or_unconscious":"Lethargic or unconscious",
    "weak_or_absent_pulse":"Weak or absent pulse",
    "respiratory_distress":"Respiratory distress",
    "sunken_eyes":"Sunken eyes",
    "drinks_poorly":"Unable to drink or drinking poorly",
    "skin_pinch_very_slow":"Skin pinch returns very slowly",
    "restless":"Irritable or restless",
    "rapid_pulse":"Rapid pulse",
    "thirsty":"Thirsty / drinks eagerly",
    "skin_pinch_slow":"Skin pinch returns slowly",
}

with st.form("patient_form"):
    complaint=st.text_area("Chief complaints and symptoms",placeholder="Describe symptoms, findings and their course. A disease name is not required.")
    columns=st.columns(2)
    age=columns[0].text_input("Age (years; blank if unknown)")
    duration=columns[1].text_input("Illness duration (days)")
    sex=columns[0].selectbox("Sex",["Unknown","Female","Male","Other"])
    weight=columns[1].text_input("Weight (kg; if known)")
    columns=st.columns(3)
    history=columns[0].text_area("Medical history")
    medicines=columns[1].text_area("Current medicines")
    allergies=columns[2].text_area("Allergies",placeholder="Blank = unknown; enter 'none known' if checked.")
    with st.expander("Available clinical findings and treatment history"):
        st.caption("Unknown findings remain unknown. These fields help check conditional recommendations.")
        cols=st.columns(3)
        sbp=cols[0].text_input("Systolic BP (mmHg)")
        dbp=cols[1].text_input("Diastolic BP (mmHg)")
        afebrile=cols[2].text_input("Hours since last fever")
        bools={}
        for index,(key,label) in enumerate(BOOL_FIELDS.items()):
            bools[key]=cols[index%3].selectbox(label,["Unknown","Yes","No"],key=key)
    submitted=st.form_submit_button("Review case",type="primary")

if submitted:
    st.session_state.pop("result",None)
    st.session_state.pop("patient",None)
    try:
        patient={"chief_complaints":complaint,"age_years":float(age) if age else None,
                 "duration_days":float(duration) if duration else None,"sex":None if sex=="Unknown" else sex,
                 "weight_kg":float(weight) if weight else None,"history":history or None,
                 "medicines":medicines or None,"allergies":allergies or None,
                 "sbp":float(sbp) if sbp else None,"dbp":float(dbp) if dbp else None,
                 "afebrile_hours":float(afebrile) if afebrile else None,
                 **{k:None if v=="Unknown" else v=="Yes" for k,v in bools.items()}}
        if not complaint.strip():
            raise ValueError("Enter the presenting complaints or observed problem.")
        for key in ["age_years","duration_days","weight_kg","sbp","dbp","afebrile_hours"]:
            if patient[key] is not None and patient[key]<0:
                raise ValueError(f"{key} cannot be negative.")
        if patient["weight_kg"]==0:
            raise ValueError("Weight must be positive when supplied.")
        st.session_state["patient"]=patient
        with st.spinner("Retrieving protocol evidence and running the local model…"):
            if os.environ.get("AIMSCRIBE_CLOUD") == "1":
                from cloud.bootstrap import ensure_model_server
                ensure_model_server()
            st.session_state["result"]=run(patient,mode)
    except (ValueError,FileNotFoundError,RuntimeError,urllib.error.URLError) as exc:
        st.error(str(exc))

if "patient" in st.session_state:
    patient=st.session_state["patient"]
    st.sidebar.subheader("Patient context")
    st.sidebar.write(patient["chief_complaints"])
    st.sidebar.caption(f"Age: {patient.get('age_years') if patient.get('age_years') is not None else 'unknown'} · Illness days: {patient.get('duration_days') if patient.get('duration_days') is not None else 'unknown'}")
    st.sidebar.json({k:v for k,v in patient.items() if v is not None and k!="chief_complaints"},expanded=False)
    with st.container(border=True):
        st.subheader("Patient context")
        st.write(patient["chief_complaints"])
        st.json({k:v for k,v in patient.items() if v is not None and k!="chief_complaints"},expanded=False)

if "result" in st.session_state:
    result=st.session_state["result"]
    st.caption(f"{result['mode'].title()} · {result['elapsed_s']:.1f} seconds · Local model")
    st.subheader("Retrieved evidence")
    for hit in result["retrieved_cards"]:
        card=hit["card"]
        annotation=hit["applicability"]
        status=f" · {annotation['status']}" if annotation else ""
        with st.expander(f"{card['card_id']} · PDF pages {', '.join(map(str,sorted({e['pdf_page'] for e in card['evidence']})))}{status}"):
            st.write(card["recommended_action"])
            if annotation:
                st.write(annotation)
            for ev in card["evidence"]:
                st.caption(f"{card['source']['title']} · {card['source']['version']} · PDF page {ev['pdf_page']} · {ev['method']}")
                st.text(ev["passage"])
    if result["validation_errors"]:
        st.error("The model response failed structural/reference checks. It is not presented as a usable recommendation.")
        st.write(result["validation_errors"])
        st.code(result["raw_model_text"])
    else:
        labels={"probable_diagnoses":"Probable / differential diagnoses","investigations":"Investigations and assessment",
                "medication_plan":"Medication and treatment planning","advice":"Advice, follow-up and referral"}
        output=result["recommendations"]
        for section in SECTIONS:
            st.subheader(labels[section])
            if not output[section]:
                st.write("No recommendation selected from the retrieved evidence.")
            for item in output[section]:
                with st.container(border=True):
                    st.write(item["action"])
                    st.caption("Model's patient-specific reason: "+item["reason"])
                    if section=="medication_plan":
                        st.table({"Field":list(item["medication"]),"Source value":[v or "Not stated in source" for v in item["medication"].values()]})
                    st.caption(f"{item['card_id']} · {item['source']['title']} · PDF pages "+", ".join(map(str,sorted({e['pdf_page'] for e in item['evidence']}))))
        st.subheader("Missing information")
        for question in output["missing_information"]:
            st.write("• "+question)
        if not output["missing_information"]:
            st.write("The model did not request additional details. This does not establish that the case is complete.")
    st.download_button("Download this case output",json.dumps(result,ensure_ascii=False,indent=2),"case_output.json","application/json")
