#!/usr/bin/env python

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, Item, User

engine = create_engine('sqlite:///categoryitems.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Yiyu Pan", email="yiyupan666@gmail.com",
             picture='https://pbs.twimg.com/profile_images/' +
             '2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Items for Soccer
category1 = Category(name="Soccer", user_id=User1.id)

session.add(category1)
session.commit()


item1 = Item(name="Jersey",
             description="""
             The Laws of the Game set out the basic equipment
              which must be worn by all players in Law 4: The Players'
              Equipment.
              Five separate items are specified: shirt
              (also known as a jersey),
              shorts, socks also known as stockings), footwear and shin pads.
             """,
             category_id=category1.id,
             user_id=User1.id)
session.add(item1)
session.commit()

item2 = Item(name="Soccer Cleats",
             description="""Soccer cleats, most of the time a soccer shoe
              is a firm ground soccer shoe. Firm ground is the classic soccer
              shoe with cleats/studs designed to provide traction and stability
              on most natural grass, outdoor soccer fields""",
             category_id=category1.id,
             user_id=User1.id)
session.add(item2)
session.commit()

item3 = Item(name="Two shinguards",
             description="""Today, there are a two basic types of shin guards
              used in association football:
              slip-in shin guards and ankle shin guards.""",
             category_id=category1.id,
             user_id=User1.id)
session.add(item3)
session.commit()

item4 = Item(name="Shinguards",
             description="""A shin guard or shin pad is a piece of
              equipment worn on the front of a player's shin to protect
              them from injury.""",
             category_id=category1.id,
             user_id=User1.id)
session.add(item4)
session.commit()

# Items for Hockey
category2 = Category(name="Hockey", user_id=User1.id)

session.add(category2)
session.commit()


item5 = Item(name="Stick",
             description="""
             The stick used in bandy
              should be made of an approved material such as wood
              or a similar material and should not contain any
              metal or sharp parts which can hurt the surrounding players.
             """,
             category_id=category2.id,
             user_id=User1.id)
session.add(item5)
session.commit()

# Items for Snowboarding
category3 = Category(name="Snowboarding", user_id=User1.id)

session.add(category3)
session.commit()


item6 = Item(name="Goggles",
             description="""
             Goggles, or safety glasses, are forms of protective
              eyewear that usually enclose or protect the area
              surrounding the eye in order to prevent
              particulates, water or chemicals from striking
              the eyes.
             """,
             category_id=category3.id,
             user_id=User1.id)
session.add(item6)
session.commit()

item7 = Item(name="Snowboard",
             description="""
             Snowboards are boards that are usually the width of one's
              foot longways, with the ability to glide on snow.
              Snowboards are differentiated from monoskis
              by the stance of the user
             """,
             category_id=category3.id,
             user_id=User1.id)
session.add(item7)
session.commit()

# Items for Frisbee
category4 = Category(name="Frisbee", user_id=1)

session.add(category4)
session.commit()


item8 = Item(name="Frisbee",
             description="""
             A frisbee is a gliding toy or sporting item that is generally
              plastic and roughly 20 to 25 centimetres in diameter with
              a lip,[1] used recreationally and competitively for throwing
              and catching, for example, in flying disc games.
             """,
             category_id=category4.id,
             user_id=User1.id)
session.add(item8)
session.commit()

# Items for Baseball
category5 = Category(name="Baseball", user_id=User1.id)

session.add(category5)
session.commit()


item9 = Item(name="Bat",
             description="""
                A baseball bat is a smooth wooden or metal club used in
                 the sport of baseball to hit the ball after it is thrown
                 by the pitcher.
                """,
             category_id=category5.id,
             user_id=User1.id)
session.add(item9)
session.commit()

# Category of Rock Climbing
category6 = Category(name="Rock Climbing", user_id=User1.id)

session.add(category6)
session.commit()

# Category of Foosball
category7 = Category(name="Foosball", user_id=User1.id)

session.add(category7)
session.commit()

# Category of Skating
category8 = Category(name="Skating", user_id=User1.id)

session.add(category8)
session.commit()

print "added items"
