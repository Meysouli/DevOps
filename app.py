import streamlit as st
import datetime
from db_functions import *
import math
from river.naive_bayes import MultinomialNB
from river.feature_extraction import BagOfWords, TFIDF
from river.compose import Pipeline
import numpy as np
import pandas as pd

subheader_template = """
<h5 style="color: #1e6666; text-align: center">{}</h5>
"""

title_template = """
<h5 style="color: rgb(30, 102, 102);
padding: 10px;
text-align: left;">{}</h5>
"""

nb_template = """
<div style="
background-color: rgb(30, 102, 102);
text-align: center;
border-radius: 8px;">
<h6 style="color: #fff; font-size: 18px;">{}</h6>
<h2 style="color: #fff;">{}</h2>
</div>
"""

p_template = """
<p style="font-size: 13px;">{}</p>
"""

def main():
    st.title("Souli's cultural association")
    menu = ["Home", "Add Event", "Reserve place", "About"]
    choice = st.sidebar.selectbox("Menu", menu)

    # create database tables
    create_event_table()
    create_attendee_table()

    old_events_by_type = get_old_events_by_type()
    events_by_type_model = Pipeline(('vectorizer', BagOfWords(lowercase=True)), ('nv', MultinomialNB()))

    old_events_by_quarter = get_old_events_by_quarter()
    events_by_quarter_model = Pipeline(('vectorizer', BagOfWords(lowercase=True)), ('nv', MultinomialNB()))

    for i in old_events_by_type:
        events_by_type_model = events_by_type_model.learn_one(i[0], str(i[1]))

    for i in old_events_by_quarter:
        events_by_quarter_model = events_by_quarter_model.learn_one(i[0], str(i[1]))

    if choice == "Home":
        subheader = "Welcome abroad, adding an event in our cultural area or registering your place has never been easier."
        st.markdown(subheader_template.format(subheader), unsafe_allow_html=True)

        # List of all events
        st.markdown(title_template.format("List of all events"), unsafe_allow_html=True)
        events = get_events()
        table = pd.DataFrame(events,
                             columns=["Spectacle", "Type", "Organiser", "Date", "Start time", "Duration", "Hall",
                                      "Sold tickets"])
        st.dataframe(table, use_container_width=True)

        # Sold tickets stats
        sold_tickets = get_sold_tickets()
        col1, col2, col3 = st.columns(3)
        with col1:
            mean = np.mean(sold_tickets)
            st.markdown(nb_template.format("The average number of sold tickets",
                                           str(math.floor(mean))),
                        unsafe_allow_html=True)
        with col2:
            median = np.median(sold_tickets)
            st.markdown(nb_template.format("The median number of sold tickets",
                                           str(math.floor(median))),
                        unsafe_allow_html=True)
        with col3:
            sum = np.sum(sold_tickets)
            st.markdown(nb_template.format("The total number of sold tickets",
                                           str(sum)),
                        unsafe_allow_html=True)

        # Upcoming events
        st.markdown(title_template.format("Upcoming events"), unsafe_allow_html=True)
        st.markdown(p_template.format(
            "Predicted attendees by type°: is the number of tickets we expect to be sold based on our sales for the choosen event type."),
            unsafe_allow_html=True)
        st.markdown(p_template.format(
            "Predicted attendees by quarter°: is the number of tickets we expect to be sold based on our sales for the choosen date."),
            unsafe_allow_html=True)
        events = get_upcoming_events()
        df = pd.DataFrame(
            columns=["Spectacle",
                     "Type",
                     "Predicted attendees by type",
                     "Date",
                     "Predicted attendees by quarter"])
        for i in events:
            spectacle = i[0]
            event_type = i[1]
            event_date = i[2]
            quarter = i[3]

            tickets_by_type_prediction = events_by_type_model.predict_one(event_type)
            # tickets_by_type_prediction_probability = tickets_by_type_prediction.predict_proba_one(i[0])
            # tickets_by_type_probability = max(tickets_by_type_prediction_probability.values())

            tickets_by_quarter_prediction = events_by_quarter_model.predict_one(quarter)
            # tickets_by_quarter_prediction_probability = tickets_by_quarter_prediction.predict_proba_one(quarter)
            # tickets_by_quarter_probability = max(tickets_by_quarter_prediction_probability.values())
            df2 = pd.DataFrame([[spectacle,
                                 event_type,
                                 tickets_by_type_prediction,
                                 event_date + ' | ' + quarter,
                                 tickets_by_quarter_prediction]],
                               columns=["Spectacle",
                                        "Type",
                                        "Predicted attendees by type",
                                        "Date",
                                        "Predicted attendees by quarter",
                                        ])
            df = df.append(df2)
        st.dataframe(df, use_container_width=True)

        # sold_tickets_by_quarter = pd.DataFrame(get_sold_tickets_by_quarter(),
        #                                        columns=['quarter','tickets'])
        # # st.text(sold_tickets_by_quarter["quarter"])
        # st.text(sold_tickets_by_quarter)
        # st.text(np.random.randn(20, 3))
        #
        #
        #
        # st.bar_chart(sold_tickets_by_quarter, x=None, y=None)

    if choice == "Add Event":
        st.subheader("Add Event")
        with st.form(key='addEvent'):
            hall = st.radio("Hall", ("Hall 1", "Hall 2"))
            organiser = st.text_input("Organiser")

            col1, col2, col3 = st.columns(3)
            with col1:
                spectacle = st.text_input("Spectacle name")
            with col2:
                code = st.text_input("Spectacle code")
            with col3:
                event_type = st.radio("Type", ("conference", "theatre", "musical", "cinema"))

            col4, col5, col6 = st.columns(3)
            with col4:
                event_date = st.date_input(label="Date")
            with col5:
                start_time = st.text_input(label="Start time", value="08:00")
            with col6:
                duration = st.number_input(label="Duration in minutes", min_value=0, step=1, help="60 means 1 hour")

            reserve_hall = st.form_submit_button(label='Reserve')
            if reserve_hall:
                add_event(hall, organiser, spectacle, event_type, code, event_date, start_time, duration)
                st.success("Event added")

    if choice == "Reserve place":
        st.subheader("Reserve your place")
        list_of_spectacles = [i[0] for i in get_spectacles()]

        with st.form(key='reservePlace'):
            col5, col6, col7 = st.columns([3, 2, 1])
            with col5:
                first_name = st.text_input("First name")
            with col6:
                last_name = st.text_input("Last name")
            with col7:
                dob = st.date_input(label="Date of birth", min_value=datetime.date(1930, 1, 1),
                                    max_value=datetime.date.today())

            spectacle = st.selectbox("Spectacle", list_of_spectacles)
            tariff = st.radio("Tariff", ("Normal", "Student", "Kid"))

            but_ticket = st.form_submit_button(label='Buy ticket')
            if but_ticket:
                reserve_place(first_name, last_name, dob, spectacle, tariff)
                st.success("Event added")
    if choice == "About":
        st.subheader("About")
        st.text("This project is realised by Oumaima Souli")


if __name__ == '__main__':
    main()
