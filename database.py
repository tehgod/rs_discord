import pandas as pd
from sqlalchemy import create_engine, text
import os, os.path
from datetime import datetime


class database_connection:
    def __init__(self, db_name):
        self.db_name = db_name

    def load_engine (self):
        db_username = os.getenv('db_username')
        db_password = os.getenv('db_password')
        db_hostname = os.getenv('db_hostname')
        self.engine = create_engine(f"mysql+pymysql://{db_username}:{db_password}@{db_hostname}/Runescape")
        return True

    def df_to_db(self, df, table_name='HighscoreData'):
        self.load_engine()
        df.to_sql(table_name, con = self.engine, if_exists = 'append',index = False)
        self.engine.dispose()
        return True

    def generate_daily_dataframe(self, date=datetime.now().strftime("%Y-%m-%d")):
        self.load_engine()
        result = pd.read_sql(f"""select * from HighscoreData where DATE_FORMAT(`Timestamp`, '%%Y-%%m-%%d') = '{date}' group by Username order by username""", self.engine)
        self.engine.dispose()
        return result

    def load_skills(self):
        self.load_engine()
        result = pd.read_sql(f"""select * from HighscoreActivities order by CAST(HighscoreId AS unsigned) ASC""", self.engine)
        self.engine.dispose()
        return result

    def df_to_dict(self, df):
        return df.to_dict(orient='records')
    
    def load_members(self):
        self.load_engine()
        df = pd.read_sql("select Username from Usernames where TrackStats=1", self.engine)
        usernames = []
        for entry in df.values.tolist():
            usernames.append(entry[0])
        self.engine.dispose()
        return usernames
    
    def grab_secret(self, key):
        self.load_engine()
        df = pd.read_sql(f"select Value from DiscordInformation where `Key`='{key}'", self.engine)
        return df.values[0][0]

    def retrieve_usernames(self, discord_id):
        self.load_engine()
        df = pd.read_sql(f"call DiscordIdToUsername({discord_id});", self.engine)
        usernames = []
        for entry in df.values.tolist():
            usernames.append(entry[0].lower())
        self.engine.dispose()
        return usernames
    
    def update_usernames(self, old_username, new_username):
        self.load_engine()
        with self.engine.connect() as connection:
            connection.execute(text(f"call UpdateUsername('{old_username}', '{new_username}');"))
            connection.commit()
        self.engine.dispose()
