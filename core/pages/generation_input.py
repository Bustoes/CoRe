import os
import re
import time
import datetime
import numpy as np
import pandas as pd
import streamlit as st

from core.systems import System
from core.utils import add_chat_message


@st.cache_data
def read_data(file_path: str):
    return pd.read_csv(file_path)

def remove_history(data_str, submit_time):
    histories_filtered = []
    histories = data_str.split(';')
    for history in histories:
        submit_time_match = re.search(r"Review Completion Timestamp: (\d+)", history)
        submit_time_match_int = int(submit_time_match.group(1))
        if 0 < submit_time_match_int < submit_time:
            histories_filtered.append(history)
    modified_data_str = ';'.join(histories_filtered)
    return modified_data_str

def click_button():
    st.session_state.round = -1
    st.session_state.clicked_button = True

def on_click():
    st.session_state.round += 1

def gen_page_input(system: System, task: str, dataset: str):
    reviewer_df = read_data(os.path.join('data', dataset, 'reviewer.csv')).set_index('reviewer_id', drop=False)
    reviewers_id = reviewer_df['reviewer_id'].to_list()


    if 'round' not in st.session_state:
        st.session_state.round = -1
    if 'clicked_button' not in st.session_state:
        st.session_state.clicked_button = False
    if 'data_sample_input' not in st.session_state:
        st.session_state.data_sample_input = None
    reset_data = False
    with st.form(key='data_form'):
        PR_id = st.number_input("PR ID", min_value=1, step=1)
        owner_name = st.text_input("contributor name")
        owner_gender = st.text_input("contributor gender")
        owner_nationality = st.text_input("contributor nationality")
        project = st.text_input("project")
        subject = st.text_input("subject")
        files = st.text_area("files")
        submit_date_d = st.date_input("submit date", min_value=datetime.date(2009, 1, 1))
        submit_date_t = st.time_input("submit time", step=60)
        candidate_num = st.number_input("number of candidate reviewer", min_value=5, step=1)

        submit_button = st.form_submit_button(label="Submit", on_click=click_button)

    if submit_button:
        submit_date = f"{submit_date_d} {submit_date_t}"
        submit_time = int(time.mktime(time.strptime(submit_date, "%Y-%m-%d %H:%M:%S")))
        owner_profile = f"Name: {owner_name}, Gender: {owner_gender}, Nationality: {owner_nationality}"
        PR_info = f"Project: {project}, Subject: {subject}, PR Contributor Info: [{owner_profile}], Files: {files}"

        candidate_reviewer_id = np.random.choice(reviewers_id, candidate_num, replace=False).tolist()

        st.session_state.data_sample_input = pd.Series({
            "PR_id": PR_id,
            "owner_profile": owner_profile,
            "submit_date": submit_date,
            "submit_time": submit_time,
            "project": project,
            "subject": subject,
            "files": files,
            "PR_info": PR_info,
            "candidate_reviewer_id": candidate_reviewer_id,
        })
        reset_data = True

    if st.session_state.clicked_button:
        data_prompt = system.prompts[f'data_prompt']
        with st.expander('Data Sample', expanded=True):
            st.markdown(f'#### Data Input')
            st.markdown(f'##### PR Info:')
            st.markdown(f'```\n{st.session_state.data_sample_input["PR_info"]}\n```')
            if task == 'pr':
                st.markdown(f'##### Candidate Reviewer History:')
                data_sample_candidates = st.session_state.data_sample_input['candidate_reviewer_id'].split(',')
                system.kwargs['n_candidate'] = len(data_sample_candidates)
                data_sample_candidates = [f'{i + 1}. {line}' for i, line in enumerate(data_sample_candidates)]
                data_sample_candidates = '\n'.join(data_sample_candidates)
                st.markdown(f'```\n{data_sample_candidates}\n```')
                system_input = data_prompt.format(
                    PR_id=st.session_state.data_sample_input['PR_id'],
                    files=st.session_state.data_sample_input['files'],
                    subject=st.session_state.data_sample_input['subject'],
                    project=st.session_state.data_sample_input['project'],
                    owner_profile=st.session_state.data_sample_input['owner_profile'],
                    candidate_reviewer_id=st.session_state.data_sample_input['candidate_reviewer_id'],
                )
            else:
                raise NotImplementedError
            st.markdown('##### Data Prompt:')
            st.markdown(f'```\n{system_input}\n```')
        if reset_data:
            system.set_data(input=system_input, context='', gt_answer=0, data_sample=st.session_state.data_sample_input)
            system.reset(clear=True)
            st.session_state.chat_history = []
        for chat in st.session_state.chat_history:
            if isinstance(chat['message'], str):
                st.chat_message(chat['role']).markdown(chat['message'])
            elif isinstance(chat['message'], list):
                with st.chat_message(chat['role']):
                    for message in chat['message']:
                        st.markdown(f'{message}')
            else:
                raise ValueError
        max_round = st.number_input('Max round', 1, 5, 1)
        if st.button('Start one round', on_click=on_click, disabled=(max_round <= st.session_state.round + 1)):
            with st.chat_message('assistant'):
                title = f'#### System running round {len(st.session_state.chat_history) // 2 + 1}'
                st.markdown(title)
                answer = system(max_round, st.session_state.round, mode_input=True)
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'message': [title] + system.web_log
                })
            if task == 'pr':
                add_chat_message('assistant', f'**Answer**: `{answer}`')
            st.session_state.start_round = False
            st.rerun()
