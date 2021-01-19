import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):

    notification_id = msg.get_body().decode('utf-8')
    logging.info('Python ServiceBus queue trigger processed message: %s',notification_id)

    # TODO: Get connection to database
    connection = psycopg2.connect(dbname="techconfdb", user="techconfuser@techconfdb", password="I8covid19", host="techconfdb.postgres.database.azure.com")
    cursor = connection.cursor()

    try:
        # TODO: Get notification message and subject from database using the notification_id
        notification_query = cursor.execute("SELECT message, subject FROM notification WHERE id = {};".format(notification_id))

        # TODO: Get attendees email and name
        cursor.execute("SELECT first_name, last_name, email FROM attendee;")
        attendees = cursor.fetchall()
        # TODO: Loop through each attendee and send an email with a personalized subject
        for attendee in attendees:
            Mail('{}, {}, {}'.format({'admin@techconf.com'}, {attendee[2]}, {notification_query}))

        notification_completed_date = datetime.utcnow()
        notification_status = 'Notified {} attendees'.format(len(attendees))


        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        update_query = cursor.execute("UPDATE notification SET status = '{}', completed_date = '{}' WHERE id = {};".format(notification_status, notification_completed_date, notification_id))

        connection.commit()


    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        connection.rollback()
    finally:
        # TODO: Close connection
        cursor.close()
        connection.close()
