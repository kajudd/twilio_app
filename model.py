import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

database_url = os.environ.get('DATABASE_URL', 'postgresql://localhost/twilio_app')
ENGINE = create_engine(database_url, echo=False)
session = scoped_session(sessionmaker(bind=ENGINE, autocommit=False, autoflush=False))

Base = declarative_base()
Base.query = session.query_property()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(140), nullable=True)
    email = Column(String(140), nullable=True)
    password = Column(String(140), nullable=True)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.name)

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer(1000), ForeignKey('users.id'))
    first_name = Column(String(140), nullable=True)
    last_name = Column(String(140), nullable=True)
    phone_number = Column(String(140), nullable=True)
    last_called = Column(DateTime(300), nullable=True)
    last_confirmation = Column(DateTime(300), nullable=True)

    user = relationship("User", backref=backref("users", order_by=id))

class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer(1000), ForeignKey('contacts.id'))
    contacted_at = Column(DateTime(300), nullable=True)
    confirmation_at = Column(DateTime(300), nullable=True)
    status = Column(String(140), nullable=True)

    contact = relationship("Contact", backref=backref("contacts", order_by=id))

