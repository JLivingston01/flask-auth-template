from sqlalchemy import (
    create_engine,
    text
)

def main():
    db_url = 'sqlite:///.data/sqlite.db'
    engine = create_engine(db_url,echo=True)
    conn = engine.connect()

    with open("sql/dql/create_users_tbl.sql",'r') as f:
        sql = f.read()
        f.close()

    conn.execute(text(sql))
    conn.commit()
    conn.close()
    engine.dispose()

    return

if __name__=='__main__':
    main()
