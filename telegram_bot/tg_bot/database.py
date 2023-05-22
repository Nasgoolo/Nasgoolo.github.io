from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Contact

engine = create_engine('sqlite:///phonebook.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def add_contact(user_id, name, phone):
    session = Session()
    contact = Contact(user_id=user_id, name=name, phone=phone)
    session.add(contact)
    session.commit()


def get_contact(user_id, name):
    session = Session()
    contact = session.query(Contact).filter_by(user_id=user_id, name=name).first()
    return contact


def delete_contact(user_id, name):
    session = Session()
    contact = session.query(Contact).filter_by(user_id=user_id, name=name).first()
    if contact:
        session.delete(contact)
        session.commit()


def display_contacts(user_id):
    session = Session()
    contacts = session.query(Contact).filter_by(user_id=user_id).all()
    contact_list = {contact.name: contact.phone for contact in contacts}
    return contact_list
