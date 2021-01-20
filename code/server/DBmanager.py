import pymysql
import pickle

# add relative directory to python_path
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

# import from common(dir)
from role import Role
from role import Ship
from role import Mate
import constants as c

class Database:
    def __init__(self):
        self.db = pymysql.connect("127.0.0.1", "root", "dab9901025", "py_test")
        self.cursor = self.db.cursor()

    # accounts table
    def register(self, account, password):

        # check if account already exists
        sql_read = "SELECT * FROM accounts WHERE name = '{}'".format(account)
        self.cursor.execute(sql_read)
        rows = self.cursor.fetchall()

        # if exists
        if rows:
            print("account already exists!" )
            return False

        # not exist
        else:
            sql_insert = "insert into accounts(name,pw) values('{}','{}')".format(account, password)
            self.cursor.execute(sql_insert)
            self.db.commit()
            print("new account added!")
            return True

    def login(self, account, password):

        # check if such a row exists
        sql_read = "SELECT * FROM accounts WHERE name = '{}' and pw = '{}' and online = '0'".\
            format(account, password)
        print(sql_read)
        self.cursor.execute(sql_read)
        rows = self.cursor.fetchall()

        # if exits
        if rows:
            print("login success!" )
            id = rows[0][0]
            return account
        else:
            print("account or password wrong!")
            return False
        pass

    # data table
    def create_character(self, account, character_name):

        # exists?
        try:
            player = pickle.load(open("data/save." + account, "rb"))
            print("exists!")
            return False

        # no
        except:
            # check if role name exists
            sql_read = "SELECT * FROM accounts WHERE role = '{}'". \
                format(character_name)
            print(sql_read)
            self.cursor.execute(sql_read)
            rows = self.cursor.fetchall()

            # exists
            if rows:
                return False

            # not exist
            else:
                # set role name in DB
                sql_update = "UPDATE accounts SET role = '{}' WHERE name = '{}'".\
                    format(character_name,account)
                print(sql_update)
                self.cursor.execute(sql_update)
                self.db.commit()

                x = y = c.PIXELS_COVERED_EACH_MOVE
                default_role = Role(x, y, character_name)
                Ship.ROLE = default_role

                # ship0 = Ship('Reagan', 'Frigate')
                # ship0.crew = 20
                # ship1 = Ship('Reagan11', 'Balsa')
                # default_role.ships.append(ship0)
                # default_role.ships.append(ship1)
                mate0 = Mate(1)
                mate0.name = character_name
                default_role.mates.append(mate0)

                if c.DEVELOPER_MODE_ON:
                    ship0 = Ship('Reagan', 'Frigate')
                    ship0.crew = 20
                    default_role.ships.append(ship0)
                    mate0.set_as_captain_of(ship0)

                    ship1 = Ship('Reagan1', 'Frigate')
                    ship1.crew = 20
                    default_role.ships.append(ship1)

                    mate1 = Mate(2)
                    mate1.name = 'Mike'
                    default_role.mates.append(mate1)
                    mate1.set_as_captain_of(ship1)

                default_role.discoveries[2] = 1

                default_role.mates[0].exp = 100

                pickle.dump(default_role, open("data/save." + account, "wb"))
                print("new player created!")
                return True


    def get_character_data(self, account):
        try:
            player = pickle.load(open("data/save." + account, "rb"))

            # set online to true
            if c.SET_ONLINE_TO_TRUE_ON_LOGIN:
                sql_update = "UPDATE accounts SET online = '1' WHERE name = '{}'".\
                    format(account)
                print(sql_update)
                self.cursor.execute(sql_update)
                self.db.commit()

            return player
        except:
            return False

    def save_character_data(self, account, player):

        # save to file
        pickle.dump(player, open("data/save." + account, "wb"))
        print("saved!")

    def set_online_to_false(self, account):
        sql_update = "UPDATE accounts SET online = '0' WHERE name = '{}'". \
            format(account)
        print(sql_update)
        self.cursor.execute(sql_update)
        self.db.commit()

if __name__ == '__main__':
    db = Database()
    # db.register('test2', 'a9901025')
    id, account = db.login('test1', 'a9901025')
    db.create_character(id, account, "biteyou12")
    player = db.get_character_data(account)
    print(player.name)
    player.name = 'new_name'

    db.save_character_data(account, player)
