import streamlit as st
import requests

BASE_URL = 'http://127.0.0.1:8000'

st.set_page_config(page_title='Civic Service Dashboard', layout='wide')
st.title('AI Smart Civic Services Dashboard')

st.sidebar.header('Filters')
category = st.sidebar.selectbox('Category', ['', 'Water', 'Waste', 'Electricity', 'Road', 'Drainage', 'Safety', 'Other'])
priority = st.sidebar.selectbox('Priority', ['', 'Low', 'Medium', 'High', 'Critical'])
status = st.sidebar.selectbox('Status', ['', 'Open', 'Assigned', 'In Progress', 'Resolved'])
search = st.sidebar.text_input('Search description / location')

st.sidebar.button('Refresh')

with st.spinner('Loading complaints...'):
    params = {
        'category': category or None,
        'priority': priority or None,
        'status': status or None,
        'search': search or None,
    }
    complaints = requests.get(f'{BASE_URL}/complaints', params={k: v for k, v in params.items() if v}).json()

st.subheader('Complaints')
if complaints:
    for item in complaints:
        with st.expander(f"#{item['complaint_id']} [{item['priority']}] {item['category']} - {item['status']}"):
            st.write('**Description:**', item['description'])
            st.write('**Location:**', item['location'])
            st.write('**Date:**', item['date'])
            st.write('**Assigned department:**', item['assigned_department'] or 'Unassigned')
            st.write('**Recommended department:**', item.get('recommended_department') or 'General Services')
            st.write('**AI output:**', item['ai_output'])
            st.write('**Resolved date:**', item.get('resolved_date') or 'Not resolved')
            col1, col2 = st.columns(2)
            with col1:
                new_status = st.selectbox('Update status', ['', 'Open', 'Assigned', 'In Progress', 'Resolved'], key=f"status_{item['complaint_id']}" )
            with col2:
                new_department = st.text_input('Assigned department', value=item['assigned_department'] or '', key=f"dept_{item['complaint_id']}" )
            if st.button('Save updates', key=f'save_{item['complaint_id']}'):
                payload = {}
                if new_status:
                    payload['status'] = new_status
                if new_department:
                    payload['assigned_department'] = new_department
                if payload:
                    response = requests.put(f"{BASE_URL}/complaints/{item['complaint_id']}", json=payload)
                    if response.status_code == 200:
                        st.success('Updated complaint')
                    else:
                        st.error('Failed to update')
else:
    st.info('No complaints match the filter.')

st.subheader('Statistics')
stats = requests.get(f'{BASE_URL}/stats').json()
cols = st.columns(3)
cols[0].metric('Total complaints', stats.get('total_complaints', 0))
cols[1].metric('Resolved count', stats.get('resolution_count', 0))
cols[2].metric('Average resolution hours', stats.get('resolution_hours', {}).get('mean', 'N/A'))

st.markdown('### Priority distribution')
if stats.get('priority_distribution'):
    st.bar_chart({item: count for d in stats['priority_distribution'] for item, count in d.items()})

st.markdown('### Category distribution')
if stats.get('category_distribution'):
    st.bar_chart({item: count for d in stats['category_distribution'] for item, count in d.items()})

st.markdown('### Status distribution')
if stats.get('status_distribution'):
    st.bar_chart({item: count for d in stats['status_distribution'] for item, count in d.items()})

if stats.get('recommended_department_distribution'):
    st.markdown('### Recommended department distribution')
    st.bar_chart({item: count for d in stats['recommended_department_distribution'] for item, count in d.items()})
