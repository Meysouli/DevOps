import sqlite3
conn = sqlite3.connect('souli.db',check_same_thread=False)
c = conn.cursor()

def create_event_table():
    c.execute('CREATE TABLE IF NOT EXISTS event(hall VARCHAR,organiser VARCHAR,spectacle VARCHAR, event_type VARCHAR,code VARCHAR, event_date DATE, start_time VARCHAR, duration INT, tickets INT)')

def create_attendee_table():
    c.execute('CREATE TABLE IF NOT EXISTS attendee(first_name VARCHAR,last_name VARCHAR,dob DATE, spectacle VARCHAR, tariff VARCHAR)')


def add_event(hall,organiser,spectacle,event_type,code,event_date,start_time,duration):
    c.execute('INSERT INTO event(hall,organiser,spectacle,event_type,code,event_date,start_time,duration) VALUES (?,?,?,?,?,?,?,?)',(hall,organiser,spectacle,event_type,code,event_date,start_time,duration))
    conn.commit()

def get_events():
    c.execute('SELECT spectacle,event_type,organiser,event_date,start_time,duration,hall, tickets FROM event')
    data = c.fetchall()
    return data

def get_old_events_by_type():
    c.execute('SELECT event_type,tickets FROM event where event_date < DATE()')
    data = c.fetchall()
    return data

def get_old_events_by_quarter():
    c.execute('select "Q" || floor((strftime("%m", event_date) + 2) / 3 ) quarters, tickets from event where tickets is not null')
    data = c.fetchall()
    return data

def get_sold_tickets_by_quarter():
    c.execute('select  "Q" || floor((strftime("%m", event_date) + 2) / 3 ) quarters,'
              'ifnull(sum(tickets), 0) tickets '
              'from event '
              'group by floor((strftime("%m", event_date) + 2) / 3 )')
    data = c.fetchall()
    return data

def get_sold_tickets():
    c.execute('select ifnull(tickets, 0) tickets '
              'from event ')
    data = c.fetchall()
    return data

def get_upcoming_events():
    c.execute('SELECT spectacle,'
              'event_type,'
              'event_date,'
              '"Q" || floor((strftime("%m", event_date) + 2) / 3 ) quarters '
              'FROM event where event_date >= DATE()')
    data = c.fetchall()
    return data

def reserve_place(first_name,last_name,dob,spectacle,tariff):
    c.execute('INSERT INTO attendee(first_name,last_name,dob,spectacle,tariff) VALUES (?,?,?,?,?)',(first_name,last_name,dob,spectacle,tariff))
    conn.commit()

def get_spectacles():
    c.execute('SELECT DISTINCT spectacle FROM event where event_date > DATE()')
    data = c.fetchall()
    return data

def get_number_of_sold_tickets_by_spectacle_name():
    c.execute('select e.spectacle, count(*) from attendee a left join event e on a.spectacle = e.spectacle ')
    data = c.fetchall()
    return data
