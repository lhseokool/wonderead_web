import streamlit as st
import json
import requests
import time


endpoint_url = 'https://wonderead-endpt-11280811525158.southeastasia.inference.ml.azure.com/score'
auth_key = 'PQsmH6CA9LudxUGS225LRiCOWPUMwcGi'
headers = {}
headers["Authorization"] = f"Bearer {auth_key}"

st.set_page_config(
    page_title="WONDERead",
    page_icon=":books:")

st.title("WONDE:red[READ] :books:")

def lock_selectbox1():
    st.session_state.pg1_locked = True
    
def lock_selectbox2():
    st.session_state.pg2_locked = True
    
def lock_selectbox3():
    st.session_state.pg3_locked = True


# Initialize Streamlit session state
def initialize_session_state():
    session_vars = [
        'messages', 
        'pg1_generated', 'pg2_generated', 'pg3_generated',
        'pg1_input', 'pg2_input', 
        'pg1_content', 'pg2_content', 'pg3_content',
        'pg1_locked', 'pg2_locked', 'pg3_locked', 
        'pg1_time', 'pg2_time', 'pg3_time'
    ]

    default_values = {
        'messages': [{"role": "system", "content": "Select AR, Topic, and Sentence Type, then click generate."}],
        'pg1_generated': False, 'pg2_generated': False,'pg3_generated': False,
        'pg1_locked': False, 'pg2_locked': False, 'pg3_locked': False,
        'pg1_time': False, 'pg2_time': False, 'pg3_time': False
    }

    for var in session_vars:
        if var not in st.session_state:
            st.session_state[var] = default_values.get(var, None)


initialize_session_state()

# 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# 사이드바 구성
with st.sidebar:
    TOPICS = ["family", "food", "emotions", "dance", "sports", "animals", "plants", "technology", "weathers", "health"]

    ar = st.selectbox("AR INDEX", range(1, 11), disabled=st.session_state.pg1_locked)
    # topic = st.selectbox("Topic", TOPICS, disabled=st.session_state.pg1_locked)
    topic = st.multiselect("Topic", TOPICS, disabled=st.session_state.pg1_locked, max_selections=3)
    exp_type = st.selectbox("문장 유형", ["Dialogue", "Prose"], disabled=st.session_state.pg1_locked)
    
    
    # 첫번째 지문 생성 버튼
    if st.button("첫번째 지문 생성", on_click=lock_selectbox1, disabled=st.session_state.pg1_locked):
        st.session_state.pg1_generated = True
        
        pg1_input = {"input": {"AR": ar, "topic": ', '.join(topic), "wr_type": "narrative", "exp_type": exp_type.lower()},
                     "pg_type": "pg1"}
        
        print(f"pg1_input: {pg1_input}")
        t0 = time.perf_counter()
        response = requests.post(endpoint_url, json=pg1_input, headers=headers)
        pg1_time = time.perf_counter() - t0
        print(response)
        print("\n\n\n")
        st.session_state.pg1_content = json.loads(response.json())
        st.session_state.pg1_time = pg1_time
        st.session_state.pg1_input = pg1_input
        

    # 두번째 지문 생성 버튼
    if st.session_state.pg1_generated:
        PG1_Q = ['Q1', 'Q2', 'Q3']
        sel_pg1_q = st.selectbox("질문을 선택하세요", PG1_Q, key='selectbox1', disabled=st.session_state.pg2_locked)
        
        if st.button("두번째 지문 생성", on_click=lock_selectbox2, disabled=st.session_state.pg2_locked):
            st.session_state.pg2_generated = True
            # st.session_state.pg2_locked = True  # 지문 생성 후 선택 잠금
            
            q1_num = sel_pg1_q[-1]
            pg1_data = st.session_state.pg1_content
            pg2_input = st.session_state.pg1_input
            
            pg2_input['input']['title'] = pg1_data['title']
            pg2_input['input']['pg1'] = pg1_data['content']
            pg2_input['input']['sel_q1_type'] = pg1_data[f'q{q1_num}_type']
            pg2_input['input']['sel_q1'] = pg1_data[f'q{q1_num}']
            pg2_input['pg_type'] = "pg2"
            st.session_state.pg2_input = pg2_input
            print(f"pg2_input: {pg2_input}")
            
            t0 = time.perf_counter()
            response = requests.post(endpoint_url, json=pg2_input, headers=headers)
            pg2_time = time.perf_counter() - t0
            st.session_state.pg2_content = json.loads(response.json())
            st.session_state.pg2_time = pg2_time
            
            
            
        # 세번째 지문 생성 버튼
        if st.session_state.pg2_generated:
            PG2_Q = ['Q1', 'Q2', 'Q3']
            sel_pg2_q = st.selectbox("질문을 선택하세요", PG2_Q, key='selectbox2', disabled=st.session_state.pg3_locked)
            
            if st.button("세번째 지문 생성", on_click=lock_selectbox3, disabled=st.session_state.pg3_locked):
                st.session_state.pg3_generated = True
                # st.session_state.pg3_locked = True  # 지문 생성 후 선택 잠금
                
                q2_num = sel_pg2_q[-1]
                pg2_data = st.session_state.pg2_content
                pg3_input = st.session_state.pg2_input
            
                del pg3_input['input']['sel_q1_type'], pg3_input['input']['sel_q1']
                pg3_input['input']['pg2'] = pg2_data['content']
                pg3_input['input']['sel_q2'] = pg2_data[f'q{q2_num}']
                pg3_input['pg_type'] = "pg3"
                print(f"pg3_input: {pg3_input}")
                
                t0 = time.perf_counter()
                response = requests.post(endpoint_url, json=pg3_input, headers=headers)
                pg3_time = time.perf_counter() - t0
                st.session_state.pg3_content = json.loads(response.json())
                st.session_state.pg3_time = pg3_time
                
                
                
# 첫번째 지문 생성 처리
if st.session_state.pg1_generated:    
    with st.chat_message("assistant"):
        pg1 = st.session_state.pg1_content
        st.markdown(f"{pg1['title']}\n\n{pg1['content']}\n")
        st.divider()
        for i in range(3):
            st.markdown(f"Q{i+1}({pg1[f'q{i+1}_type']}) {pg1[f'q{i+1}']}")
        st.text(f"생성 시간: {st.session_state.pg1_time:.2f} sec")
        
        
if st.session_state.pg1_generated and st.session_state.pg2_generated:    
    with st.chat_message("assistant"):
        pg2 = st.session_state.pg2_content
        st.markdown(f"{pg2['content']}\n")
        st.text(f"Q1({pg2['q1_type']}) {pg2['q1']}\nQ2({pg2['q2_type']}) {pg2['q2']}\nQ3({pg2['q3_type']}) {pg2['q3']}")
        st.text(f"생성 시간: {st.session_state.pg1_time:.2f} sec")
        
        
if st.session_state.pg3_generated:
    with st.chat_message("assistant"):
        pg3 = st.session_state.pg3_content
        st.markdown(f"{pg3['content']}\n")
        for i in range(6):
            st.markdown(f"{i+1}.{pg3[f'q{i+1}_type']}: {pg3[f'q{i+1}']}")
        st.text(f"생성 시간: {st.session_state.pg3_time:.2f} sec")
