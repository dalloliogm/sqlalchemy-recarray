from sqlalchemy.orm.query import Query

class LimitingQuery(Query):
    
    def get(self, ident):
        # override get() so that the flag is always checked in the 
        # DB as opposed to pulling from the identity map. - this is optional.
        return Query.get(self.populate_existing(), ident)
    
    def __iter__(self):
        return Query.__iter__(self.private())

    def private(self):
        crit = (self._mapper_zero().class_.public == True)
        
        return self.enable_assertions(False).filter(crit)

if __name__ == '__main__':

    from sqlalchemy import *
    from sqlalchemy.orm import *
    from sqlalchemy.ext.declarative import declarative_base
    
    Base = declarative_base()

    class User(Base):
        __tablename__ = 'user'

        id = Column(Integer, primary_key=True)
        name = Column(String)
        public = Column(Boolean, nullable=False)
        addresses = relation("Address", backref="user")

        def __eq__(self, other):
            assert isinstance(other, User) and other.name == self.name and other.public == self.public

    class Address(Base):
        __tablename__ = 'address'

        id = Column(Integer, primary_key=True)
        email = Column(String)
        user_id = Column(Integer, ForeignKey('user.id'))
        public = Column(Boolean, nullable=False)

        def __eq__(self, other):
            assert isinstance(other, Address) and other.email == self.email and other.public == self.public


    engine = create_engine('sqlite://', echo=True)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine, query_cls=LimitingQuery)
        
    sess = Session()

    sess.add_all([
        User(name='u1', public=True, addresses=[Address(email='u1a1', public=True), Address(email='u1a2', public=True)]),
        User(name='u2', public=True, addresses=[Address(email='u2a1', public=False), Address(email='u2a2', public=True)]),
        User(name='u3', public=False, addresses=[Address(email='u3a1', public=False), Address(email='u3a2', public=False)]),
        User(name='u4', public=False, addresses=[Address(email='u4a1', public=False), Address(email='u4a2', public=True)]),
        User(name='u5', public=True, addresses=[Address(email='u5a1', public=True), Address(email='u5a2', public=False)])
    ])

    sess.commit()

    entries = []
    for ad in sess.query(Address):
        assert ad.public
        user = ad.user
        if user:
            assert user.public
            entries.append((ad.email, user.name))
        else:
            entries.append((ad.email, "none"))
    
    assert entries == [(u'u1a1', u'u1'), (u'u1a2', u'u1'), (u'u2a2', u'u2'), (u'u4a2', 'none'), (u'u5a1', u'u5')]

    a1 = sess.query(Address).filter_by(email='u1a1').one()
    a1.user.public = False
    sess.commit()

    assert a1.user is None
